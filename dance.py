import cv2
import mediapipe as mp
import numpy as np
import time  # 引入時間模組，用來計算 BPM

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


# 計算兩點之間空間距離的函數 (歐式距離距離公式)
def calculate_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


cap = cv2.VideoCapture(0)

# --- BPM 計算相關變數初始化 ---
prev_wrists = None  # 儲存上一幀的雙手手腕座標
last_beat_time = 0  # 記錄上一次觸發節拍的時間
bpm_history = []  # 用 List (類似 C++ std::vector) 來儲存最近幾次的 BPM，用來算平均
SPEED_THRESHOLD = 0.05  # 速度門檻 (需根據鏡頭距離微調，數值越大代表動作要越劇烈才算數)
COOLDOWN_TIME = 0.3  # 冷卻時間 0.3 秒 (限制最高能測到的 BPM 為 200)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        current_time = time.time()  # 取得當下系統時間 (秒)
        current_speed = 0  # 初始化當前速度
        display_bpm = 0  # 畫面上顯示的平均 BPM

        try:
            landmarks = results.pose_landmarks.landmark

            # 取得當前幀的左右手腕座標 (以 0~1 的比例表示)
            l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            r_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # 如果有上一幀的紀錄，就可以計算移動速度
            if prev_wrists is not None:
                # 分別計算左手與右手的移動距離
                l_dist = calculate_distance(prev_wrists['left'], l_wrist)
                r_dist = calculate_distance(prev_wrists['right'], r_wrist)

                # 兩手移動距離相加，當作全身的「綜合移動速度信號」
                current_speed = l_dist + r_dist

                # 判斷邏輯：如果速度超過門檻，且距離上次觸發已經超過冷卻時間
                if current_speed > SPEED_THRESHOLD and (current_time - last_beat_time) > COOLDOWN_TIME:

                    # 如果不是第一次觸發，就可以計算時間差與 BPM
                    if last_beat_time != 0:
                        time_diff = current_time - last_beat_time
                        bpm = 60.0 / time_diff  # BPM 公式

                        # 排除太誇張的錯誤數值 (例如超過 200 BPM 的雜訊)
                        if 40 < bpm < 200:
                            bpm_history.append(bpm)
                            # 只保留最近 5 次的 BPM 來算平均 (避免畫面數字狂跳)
                            if len(bpm_history) > 5:
                                bpm_history.pop(0)

                    # 更新觸發時間
                    last_beat_time = current_time
                    print("🎵 抓到節拍轉換！")

            # 更新「上一幀」的座標，供下一次迴圈使用
            prev_wrists = {'left': l_wrist, 'right': r_wrist}

            # 計算平均 BPM 用於顯示
            if len(bpm_history) > 0:
                display_bpm = int(sum(bpm_history) / len(bpm_history))

        except Exception as e:
            # 畫面沒人時跳過
            pass

        # 繪製視覺化數據
        # 1. 顯示當前移動速度 (可以觀察數值變化來微調 SPEED_THRESHOLD)
        cv2.putText(image, f'SPEED: {current_speed:.3f}', (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # 2. 顯示計算出的平均 BPM
        cv2.putText(image, f'EST. BPM: {display_bpm}', (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA)

        # 3. 畫出節拍指示燈 (當處於冷卻時間內時，顯示紅色方塊代表 "HIT")
        if (current_time - last_beat_time) < 0.15:
            cv2.rectangle(image, (10, 120), (100, 180), (0, 0, 255), -1)  # 紅色實心方塊

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow('Dance BPM Analyzer', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()