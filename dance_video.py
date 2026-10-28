import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def calculate_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


cap = cv2.VideoCapture(r"C:\Users\s0979\Downloads\Locking training ep.24  Foundation & Advance - 21 Pump (720p, h264).mp4")  # 記得換成你的影片檔名

prev_points = None
prev_speed = 0.0
last_beat_time = 0
bpm_history = []

# 因為現在加總了 6 個部位，數值會比之前大，門檻預設提高到 0.12
SPEED_DIFF_THRESHOLD = 0.12
COOLDOWN_TIME = 0.4

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        current_speed = 0
        speed_diff = 0
        display_bpm = 0

        try:
            landmarks = results.pose_landmarks.landmark

            # 將全身 6 個關鍵點的 X, Y 座標打包成 Dictionary
            points = {
                'l_wrist': [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y],
                'r_wrist': [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y],
                'l_ankle': [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y],
                'r_ankle': [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y],
                'l_shoulder': [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                               landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
                'r_shoulder': [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            }

            if prev_points is not None:
                # 跑迴圈算出 6 個點各自的移動距離，然後全部加總
                total_dist = sum([calculate_distance(prev_points[k], points[k]) for k in points.keys()])

                current_speed = total_dist
                speed_diff = abs(current_speed - prev_speed)

                if speed_diff > SPEED_DIFF_THRESHOLD and (current_time - last_beat_time) > COOLDOWN_TIME:

                    if last_beat_time != 0:
                        time_diff = current_time - last_beat_time
                        bpm = 60.0 / time_diff

                        if 40 < bpm < 200:
                            bpm_history.append(bpm)
                            if len(bpm_history) > 5:
                                bpm_history.pop(0)

                    last_beat_time = current_time
                    print("🎵 全身動態抓到頓點！")

            # 更新狀態
            prev_points = points
            prev_speed = current_speed

            if len(bpm_history) > 0:
                display_bpm = int(sum(bpm_history) / len(bpm_history))

        except Exception as e:
            pass

        # 畫面上改為顯示 BODY SPD DIFF (全身加速度)
        cv2.putText(image, f'BODY SPD DIFF: {speed_diff:.3f}', (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f'EST. BPM: {display_bpm}', (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA)

        if (current_time - last_beat_time) < 0.15:
            cv2.rectangle(image, (10, 120), (100, 180), (0, 0, 255), -1)

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        cv2.imshow('Full Body Dance BPM', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()