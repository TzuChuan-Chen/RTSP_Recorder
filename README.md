# RTSP 多串流錄製程式

## 目錄
1. [簡介](#簡介)
2. [功能特點](#功能特點)
3. [系統需求](#系統需求)
4. [安裝指南](#安裝指南)
5. [使用說明](#使用說明)
6. [常見問題](#常見問題)
7. [注意事項](#注意事項)

## 簡介
這是一個使用 PyQt5 開發的 GUI 應用程式，允許您同時錄製多個 RTSP 串流。該應用程式提供了一個直觀的界面，方便用戶管理和錄製多個視頻流。

## 功能特點
- 添加多個 RTSP 串流進行錄製
- 使用 ffmpeg 進行錄製，使用 ffplay 進行預覽
- 批量導入攝影機設定（例如 camera_config.csv）
- 儲存和載入設定
- 實時顯示錄製時間
- 單個串流預覽功能

## 系統需求
- Python 版本：Python 3.9 或更高版本
- 作業系統：Windows、macOS 或 Ubuntu
- 必要套件：
  - PyQt5
  - ffmpeg
  - ffplay（通常與 ffmpeg 一起安裝）

## 安裝指南
1. 安裝 Python：
   確保您的系統已安裝 Python 3.6 或更高版本。可以從 [Python 官方網站](https://www.python.org/downloads/) 下載並安裝。

2. 安裝 ffmpeg 和 ffplay：
   - Windows：
     從 [ffmpeg 官網](https://ffmpeg.org/download.html) 或 [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 下載 Windows 版本的 ffmpeg。解壓縮後，將 bin 目錄添加到系統的環境變數 PATH 中。
   - macOS：
     使用 Homebrew 安裝：`brew install ffmpeg`
   - Linux：
     使用包管理器安裝（以 Ubuntu 為例）：
     ```
     sudo apt update
     sudo apt install ffmpeg
     ```

3. 安裝 Python 依賴套件：
   ```
   pip install PyQt5
   ```

4. 下載程式碼：
   將提供的程式碼保存為 `rtsp_recorder.py`。

## 使用說明
1. 執行程式：
   ```
   python rtsp_recorder.py
   ```

2. 介面介紹：
   - RTSP URL：輸入要錄製的 RTSP 串流網址
   - 輸出目錄：指定錄製檔案的存放目錄
   - 前綴：為錄製的檔案設定名稱前綴
   - 新增串流：將上述資訊添加到串流列表
   - 串流列表：顯示已添加的串流，包括 RTSP URL、輸出目錄、前綴、錄製時間和操作
   - 預覽：點擊以使用 ffplay 即時預覽該串流
   - 導入設定：從 CSV 檔案批量導入串流設定
   - 儲存設定：將當前的串流設定儲存為 CSV 檔案
   - 開始錄製：開始錄製所有已添加的串流
   - 停止錄製：停止錄製所有串流

3. 添加單個串流：
   填寫 RTSP URL、輸出目錄和前綴，然後點擊 "新增串流"。

4. 批量導入串流設定：
   準備一個 CSV 檔案（例如 camera_config.csv），格式如下：
   ```
   RTSP_URL,輸出目錄,前綴
   rtsp://example.com/stream1,/path/to/output1,Camera1_
   rtsp://example.com/stream2,/path/to/output2,Camera2_
   ```
   點擊 "導入設定" 按鈕，選擇準備好的 CSV 檔案。

5. 開始和停止錄製：
   點擊 "開始錄製" 按鈕開始錄製，點擊 "停止錄製" 按鈕停止錄製。

6. 預覽串流：
   在串流列表中，點擊每一行的 "預覽" 按鈕，可以即時預覽該 RTSP 串流。

## 常見問題
1. 無法錄製或預覽：
   - 檢查 RTSP URL 是否正確
   - 確保攝影機在線且可訪問
   - 檢查網路連接是否正常

2. ffmpeg 或 ffplay 未找到：
   - 確保 ffmpeg 和 ffplay 已正確安裝
   - 確認它們的可執行檔所在的目錄已添加到系統的環境變數 PATH 中

3. 程式報錯或無響應：
   - 在命令提示字元或終端中執行程式，以查看錯誤訊息
   - 確保所有依賴套件已正確安裝

## 注意事項
- 關閉程式：在錄製過程中，無法關閉程式。請先停止錄製再關閉。
- 權限問題：確保您有權讀寫指定的輸出目錄。
- 網路連接：確保您的電腦能夠連接到所有攝影機的 RTSP 串流。