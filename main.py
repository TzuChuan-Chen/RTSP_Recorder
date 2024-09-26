import sys
import os
import csv
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, 
                             QHeaderView, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
import subprocess
import threading
import time

class RTSPRecorder:
    def __init__(self, url, output_dir, prefix):
        self.url = url
        self.output_dir = output_dir
        self.prefix = prefix
        self.process = None
        self.is_recording = False
        self.start_time = None

    def start_recording(self):
        if self.is_recording:
            return
        
        self.is_recording = True
        self.start_time = datetime.now()
        current_time = self.start_time.strftime("%Y%m%d/%H/%M")
        output_dir = os.path.join(self.output_dir, current_time)
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = f"{self.prefix}{self.start_time.strftime('%Y%m%d_%H%M%S')}.mkv"
        output_path = os.path.join(output_dir, output_filename)
        
        command = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-use_wallclock_as_timestamps", "1",
            "-i", self.url,
            "-c", "copy",
            "-y",
            output_path
        ]
        
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE)

    def stop_recording(self):
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.process.stdin.write(b'q')
        self.process.stdin.flush()
        self.process.wait()
        self.process = None
        self.start_time = None

    def get_recording_time(self):
        if not self.is_recording or self.start_time is None:
            return "00:00:00"
        elapsed = datetime.now() - self.start_time
        return str(elapsed).split('.')[0]  # 移除微秒

class RecordingManager(QThread):
    recording_finished = pyqtSignal()
    recording_time_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.recorders = []
        self.is_recording = False

    def add_recorder(self, recorder):
        self.recorders.append(recorder)

    def start_recording(self):
        self.is_recording = True
        for recorder in self.recorders:
            recorder.start_recording()
        self.start()

    def stop_recording(self):
        self.is_recording = False
        for recorder in self.recorders:
            recorder.stop_recording()

    def run(self):
        while self.is_recording:
            recording_times = [recorder.get_recording_time() for recorder in self.recorders]
            self.recording_time_updated.emit(recording_times)
            time.sleep(1)
        self.recording_finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTSP 多串流錄製程式")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()
        self.recording_manager = RecordingManager()
        self.recording_manager.recording_finished.connect(self.on_recording_finished)
        self.recording_manager.recording_time_updated.connect(self.update_recording_times)

    def setup_ui(self):
        # 創建輸入欄位
        input_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("RTSP URL")
        self.url_label = QLabel("RTSP URL:")
        self.url_label.setMinimumWidth(60)
        input_layout.addWidget(self.url_label)
        input_layout.addWidget(self.url_input)

        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("輸出目錄")
        self.output_dir_label = QLabel("輸出目錄:")
        self.output_dir_label.setMinimumWidth(60)
        input_layout.addWidget(self.output_dir_label)
        input_layout.addWidget(self.output_dir_input)

        self.browse_button = QPushButton("瀏覽")
        self.browse_button.clicked.connect(self.browse_output_dir)
        input_layout.addWidget(self.browse_button)

        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("前綴")
        self.prefix_label = QLabel("前綴:")
        self.prefix_label.setMinimumWidth(60)
        input_layout.addWidget(self.prefix_label)
        input_layout.addWidget(self.prefix_input)

        self.add_button = QPushButton("新增串流")
        self.add_button.clicked.connect(self.add_stream)
        input_layout.addWidget(self.add_button)

        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        self.layout.addWidget(input_widget)

        # 創建串流列表
        self.streams_table = QTableWidget(0, 5)
        self.streams_table.setHorizontalHeaderLabels(["RTSP URL", "輸出目錄", "前綴", "錄製時間", "操作"])
        self.streams_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.streams_table.horizontalHeader().setMinimumSectionSize(160)  # Adjust the value as needed
        self.layout.addWidget(self.streams_table)



        # 批量導入按鈕
        self.bulk_import_button = QPushButton("批量導入")
        self.bulk_import_button.clicked.connect(self.bulk_import)
        self.layout.addWidget(self.bulk_import_button)

        # 創建控制按鈕
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("開始錄製")
        self.start_button.clicked.connect(self.start_recording)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止錄製")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        self.layout.addWidget(control_widget)

        # 創建 QSplitter
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(input_widget)
        splitter.addWidget(self.streams_table)
        splitter.addWidget(self.bulk_import_button)
        splitter.addWidget(control_widget)
        
        self.layout.addWidget(splitter)

    def browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇輸出目錄")
        if folder:
            self.output_dir_input.setText(folder)

    def add_stream(self):
        url = self.url_input.text()
        output_dir = self.output_dir_input.text()
        prefix = self.prefix_input.text()

        if not url or not output_dir or not prefix:
            return

        self.add_stream_to_table(url, output_dir, prefix)

        self.url_input.clear()
        self.output_dir_input.clear()
        self.prefix_input.clear()

    def add_stream_to_table(self, url, output_dir, prefix):
        row = self.streams_table.rowCount()
        self.streams_table.insertRow(row)
        self.streams_table.setItem(row, 0, QTableWidgetItem(url))
        self.streams_table.setItem(row, 1, QTableWidgetItem(output_dir))
        self.streams_table.setItem(row, 2, QTableWidgetItem(prefix))
        self.streams_table.setItem(row, 3, QTableWidgetItem("00:00:00"))

        preview_button = QPushButton("預覽")
        preview_button.clicked.connect(lambda: self.preview_camera(url))
        self.streams_table.setCellWidget(row, 4, preview_button)

    def preview_camera(self, url):
        command = [
            "ffplay",
            "-rtsp_transport", "tcp",
            "-i", url,
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-framedrop",
            "-sync", "ext"
        ]
        subprocess.Popen(command)

    def bulk_import(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "選擇 CSV 文件", "", "CSV Files (*.csv)")
        if file_name:
            with open(file_name, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) == 3:
                        url, output_dir, prefix = row
                        self.add_stream_to_table(url, output_dir, prefix)

    def start_recording(self):
        self.recording_manager.recorders.clear()
        for row in range(self.streams_table.rowCount()):
            url = self.streams_table.item(row, 0).text()
            output_dir = self.streams_table.item(row, 1).text()
            prefix = self.streams_table.item(row, 2).text()
            
            recorder = RTSPRecorder(url, output_dir, prefix)
            self.recording_manager.add_recorder(recorder)

        self.recording_manager.start_recording()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recording(self):
        self.recording_manager.stop_recording()

    def on_recording_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_recording_times(self, times):
        for row, time in enumerate(times):
            self.streams_table.setItem(row, 3, QTableWidgetItem(time))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())