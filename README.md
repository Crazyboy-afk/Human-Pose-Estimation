Human Pose Estimation

使用 YOLO Pose 進行人體骨架偵測，目前支援圖片及攝影機即時偵測。

Environment

Python 3.11

Ultralytics YOLO

OpenCV

Installation

Clone or download this repository.

Create a Python virtual environment:

py -3.11 -m venv .venv

Install dependencies:

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Usage

Run the program:

.\.venv\Scripts\python.exe pose.py




Dance BPM Analyzer (舞蹈節拍與動作轉換識別系統)
這是一個基於電腦視覺與人體姿態估計 (Pose Estimation) 的舞蹈節拍分析工具。透過追蹤舞者全身關鍵關節（雙手腕、雙肩膀、雙腳踝）的空間位移，計算出瞬間「速度差 (加速度)」，精準捕捉舞者發力、頓點 (Hit) 或鎖死 (Lock) 的動作轉換瞬間，並藉此推算出舞蹈的即時 BPM。

🌟 核心功能與檔案說明
本專案包含兩個主要的執行檔，分別對應不同的使用情境：

dance.py (即時攝影機偵測)
透過電腦攝影機 (Webcam) 進行即時串流分析。適合用於現場跳舞測試，程式會抓取系統時間 (System Time) 來計算兩次頓點之間的時間差，並即時在畫面上給予紅燈閃爍的視覺回饋。

dance_video.py (影片檔案分析)
透過讀取預錄好的舞蹈影片（如 .mp4）進行精準分析。程式會讀取影片內建的時間軸 (Timestamp)，確保就算電腦運算效能不足導致畫面慢動作播放，算出來的 BPM 依然絕對精準。適合用來分析 K-POP 練習室影片或 Popping/Locking 舞蹈片段。

⚙️ 運作環境要求
為了避免底層 C++ 動態連結庫 (DLL) 載入失敗或套件版本衝突，請確保你的開發環境符合以下條件：

作業系統： Windows 10/11, macOS, 或 Linux

Python 版本： 強烈建議使用 Python 3.11 或 3.12 (不建議使用過舊的 3.7 或過新的 3.14)

必要核心套件：

opencv-python (處理影像處理與視訊串流)

mediapipe (Google 開源的 AI 骨架辨識模型)

numpy (高效能陣列與矩陣數學運算)

🚀 安裝與執行指南
建立並啟動虛擬環境 (強烈建議)

Bash
python -m venv .venv

# Windows 啟動方式:
.\.venv\Scripts\activate
# Mac/Linux 啟動方式:
source .venv/bin/activate
安裝相依套件
確保虛擬環境啟動後，輸入以下指令安裝所需套件：

Bash
pip install mediapipe opencv-python numpy
執行程式
如果mediapipe在下載時報錯可以使用舊一點的版本
EX: 
pip install mediapipe==0.10.14 --force-reinstall

使用 Webcam 即時偵測：

Bash
python dance.py
分析影片檔案：
請先打開 dance_video.py，將程式碼中的 'your_dance_video.mp4' 替換為你的影片檔案路徑，然後執行：

Bash
python dance_video.py
(按下鍵盤 q 鍵可隨時關閉視窗)

🔧 參數微調指南 (Tuning)
每種舞蹈風格的力度與速度不同，你可以在原始碼中自行微調以下兩個核心常數，以達到最精準的判定：

SPEED_DIFF_THRESHOLD (加速度門檻)：預設為 0.12。若畫面紅燈狂閃（太敏感），請調高此數值；若用力頓點卻沒亮燈，請調低此數值。

COOLDOWN_TIME (冷卻時間)：預設為 0.4 秒。用來防止單一揮舞動作在短時間內觸發多次節拍。若分析的是快節奏音樂 (如 130 BPM 以上)，可適度將此數值調低 (例如 0.3)。

The pretrained YOLO Pose model will be downloaded automatically on the first run.
