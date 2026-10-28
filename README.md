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



The pretrained YOLO Pose model will be downloaded automatically on the first run.


# 🕺 Dance BPM Analyzer (舞蹈節拍與動作轉換識別系統)

本專案是一個基於電腦視覺 (Computer Vision) 與人體姿態估計 (Pose Estimation) 的舞蹈節拍分析系統。有別於傳統基於「音訊頻譜」的 BPM 偵測，本專案旨在透過**「視覺動作信號處理 (Visual Motion Signal Processing)」**，追蹤舞者全身關鍵關節的空間位移，計算出瞬間的「加速度 (速度差)」，以演算法精準捕捉舞者發力、頓點 (Hit) 或鎖死 (Lock) 的動作轉換瞬間，並即時推算舞蹈影片的 BPM (Beats Per Minute)。

---

## 🔬 核心演算法與實作原理 (Methodology)

本系統並非單純判斷關節角度，而是基於物理運動學的連續幀運算，演算法分為以下四個核心步驟：

### 1. 空間關鍵點提取 (Keypoint Extraction)
使用 Google 開源之 `MediaPipe Pose` 模型，提取舞者 33 個 3D 人體拓樸節點。為捕捉全身動態，本演算法過濾出 6 個核心受力點：**雙手腕 (Wrists)、雙腳踝 (Ankles)、雙側肩膀 (Shoulders)**。

### 2. 幀間動能計算 (Velocity Calculation)
提取兩相鄰幀 (Frame $N$ 與 Frame $N-1$) 的關鍵點座標，利用**歐式距離公式 (Euclidean Distance)** 計算各部位的空間位移量。因為影像幀率 (FPS) 恆定，此位移量即可視為當下之「瞬時速度 ($V$)」。將 6 個節點的位移相加，得出舞者當下的「全身綜合動能」。
* 數學表達： $V_{current} = \sum \sqrt{(X_{current} - X_{prev})^2 + (Y_{current} - Y_{prev})^2}$

### 3. 瞬間加速度檢測 (Acceleration / Peak Detection)
舞蹈的「重拍 (Hit)」本質上是肌肉的瞬間發力 (急加速) 或瞬間鎖死 (急停)。本系統透過計算與前一幀的「速度差絕對值 ($\Delta V$)」來獲取加速度指標：
* 數學表達： $\Delta V = |V_{current} - V_{prev}|$
當 $\Delta V$ 突破設定之閾值 (`SPEED_DIFF_THRESHOLD`)，即判定發生一次動作轉換 (Beat)。

### 4. 去彈跳機制與 BPM 推算 (Debounce & BPM Calculation)
為避免單一動作在極短時間內產生多個波峰導致重複觸發，系統引入了類似硬體訊號處理的**去彈跳機制 (Cooldown Time)**。
當成功觸發一次節拍，系統會紀錄當下時間 ($T$)，並與上一次觸發時間進行計算：
* 瞬時 BPM = $60 / (T_{current} - T_{prev})$
* 為確保數據穩定，系統會利用一維陣列 (List) 儲存最近 5 次的 BPM 數值，並輸出**移動平均值 (Moving Average)**。

---

## 📂 專案架構與檔案說明

本專案包含兩個針對不同處理情境的執行模組：

* **`dance.py` (即時攝影機串流分析)**
  透過 Webcam 進行現場即時演算。系統擷取 Python 系統時鐘 (`time.time()`) 進行 $\Delta t$ 計算。由於 Webcam 畫面與現實時間同步，適合做為現場互動或即時視覺回饋測試。

* **`dance_video.py` (預錄影片精準分析) 🌟 (核心亮點)**
  解決了電腦視覺處理影片時「運算速度不等於播放速度」的技術痛點。本模組**棄用系統時間，改為提取 OpenCV 底層之影片內建時間軸 (`cv2.CAP_PROP_POS_MSEC`)**。即使硬體效能不足導致畫面呈現慢動作逐格運算，最終推算出的 BPM 依舊與實際音樂節拍絕對同步。

---

## ⚙️ 系統環境與重現步驟 (Reproducibility)

* **開發語言：** Python 3.11 / 3.12 (避免使用過舊或實驗性版本以確保 C++ DLL 正常載入)
* **核心依賴套件：** `mediapipe`, `opencv-python`, `numpy`
