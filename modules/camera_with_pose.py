import cv2
from ultralytics import YOLO
from modules.which_pose import classify_pose
import time
import json
import os
import requests

# wasn't sure
import numpy

# 存储数字序列和定时器
sequence = ""
last_saved_time = 0
output_path = r"backend/checkpassword.json"

def draw_simplified_pose(image, keypoints, confidence_threshold=0.5):
    """
    在视频帧中绘制简化版人体骨架，只关注头、肩、手臂、躯干和腿部。

    Args:
        image (np.array): 摄像头输入图像。
        keypoints (list): 关键点列表 [x, y, confidence]。
        confidence_threshold (float): 关键点可视化置信度阈值。
    """
    if keypoints is None or len(keypoints) == 0:
        return  
    skeleton = [
        (5, 7), (7, 9),      # 左臂
        (6, 8), (8, 10),     # 右臂
        (11, 13), (13, 15),  # 左腿
        (12, 14), (14, 16),  # 右腿
        (5, 6),              # 肩连线
        (11, 12),            # 髋连线
        (5, 11), (6, 12),    # 肩到髋，构建躯干
        (0, 5), (0, 6)       # 鼻子到肩（头部连线）
    ]

    for person in keypoints:
        # 绘制关键点
        for i, keypoint in enumerate(person):
            x, y, conf = keypoint
            if conf > confidence_threshold:
                cv2.circle(image, (int(x), int(y)), 5, (0, 255, 0), -1)

        # 连接骨架
        for start_idx, end_idx in skeleton:
            if (person[start_idx][2] > confidence_threshold and person[end_idx][2] > confidence_threshold):
                x1, y1 = int(person[start_idx][0]), int(person[start_idx][1])
                x2, y2 = int(person[end_idx][0]), int(person[end_idx][1])
                cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 2)


def draw_custom_pose(image, keypoints, confidence_threshold=0.3):
    """
    绘制定制骨架：加入 neck 和 pelvis 两个中点，连接更合理。

    Args:
        image (np.array): 图像。
        keypoints (list): 每人 [17, 3] 的关键点列表。
        confidence_threshold (float): 最小置信度。
    """
    if keypoints is None or len(keypoints) == 0:
        return  
    skeleton = [
        (1, 2),      # 左眼 - 右眼s
        (0, 17),     # 鼻子 - neck
        (5, 7), (7, 9),    # 左臂
        (6, 8), (8, 10),   # 右臂
        (17, 5), (17, 6),  # neck - 肩
        (18, 11), (18, 12),# pelvis - 髋
        (11, 13), (13, 15),# 左腿
        (12, 14), (14, 16),# 右腿
        (17, 18)           # neck - pelvis
    ]

    for person in keypoints:
        keypts = person.tolist()

        # -- 构造 neck --
        if person[5][2] > confidence_threshold and person[6][2] > confidence_threshold:
            neck = [
                (person[5][0] + person[6][0]) / 2,
                (person[5][1] + person[6][1]) / 2,
                (person[5][2] + person[6][2]) / 2
            ]
        else:
            neck = [0, 0, 0]

        # -- 构造 pelvis --
        if person[11][2] > confidence_threshold and person[12][2] > confidence_threshold:
            pelvis = [
                (person[11][0] + person[12][0]) / 2,
                (person[11][1] + person[12][1]) / 2,
                (person[11][2] + person[12][2]) / 2
            ]
        else:
            pelvis = [0, 0, 0]

        # 添加两个中点到关键点列表（作为索引 17、18）
        keypts.append(neck)    # index 17
        keypts.append(pelvis)  # index 18

        # 绘制所有关键点
        for x, y, conf in keypts:
            if conf > confidence_threshold:
                cv2.circle(image, (int(x), int(y)), 4, (0, 255, 0), -1)

        # 绘制骨架线
        for i, j in skeleton:
            if keypts[i][2] > confidence_threshold and keypts[j][2] > confidence_threshold:
                x1, y1 = int(keypts[i][0]), int(keypts[i][1])
                x2, y2 = int(keypts[j][0]), int(keypts[j][1])
                cv2.line(image, (x1, y1), (x2, y2), (255, 0, 255), 2)

def action_to_digit(action: str) -> str:
    return {
        "Left Hand Up": "1",
        "Right Hand Up": "2",
        "Both Hands Up": "3",
        "Arms Sideways": "4"
    }.get(action, "")


def real_time_pose_estimation(camera_index=0, model_path='yolov8l-pose.pt', confidence_threshold=0.7):
    """
    实时摄像头人体姿态检测。

    Args:
        camera_index (int): 摄像头索引（默认 0）。
        model_path (str): YOLOv8-Pose 模型路径。
        confidence_threshold (float): 关键点置信度阈值。
    """
    print(f"🎥 正在打开摄像头索引 {camera_index}...")

    # 加载 YOLOv8-Pose 模型
    model = YOLO(model_path)
    print(f"✅ 成功加载模型: {model_path}")

    # 打开摄像头
    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("❌ 错误: 无法打开摄像头！")
        return
    start_time = time.time()

    print("🚀 按 'q' 退出...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ 错误: 读取摄像头帧失败！")
            break

        # 检测人体姿态
        results = model(frame, conf=confidence_threshold)
        keypoints = results[0].keypoints.data.cpu().numpy()  # 提取关键点
        if keypoints.shape[0] > 0:
            draw_custom_pose(frame, keypoints)

        current_time = time.time()
        global sequence, last_saved_time
        current_time = time.time()

        # 等待 3 秒钟再开始记录动作
        if current_time - start_time < 5:
            cv2.putText(frame, f"⏳ Starting in {5 - int(current_time - start_time)} sec...",
                        (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            cv2.imshow("实时姿态检测", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        for person in keypoints:
            action_label = classify_pose(person)
            digit = action_to_digit(action_label)

            # 获取鼻子位置用于显示
            nose = person[0]
            if nose[2] > confidence_threshold:
                cv2.putText(frame, action_label, (int(nose[0]), int(nose[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # 如果识别到新动作并超过 2 秒间隔，记录数字
            if digit and (current_time - last_saved_time >= 2) and len(sequence) < 4:
                sequence += digit
                last_saved_time = current_time
                print(f"✅ 已添加动作：{action_label} → 当前序列：{sequence}")

        # 在左上角显示当前已记录数字序列
        cv2.putText(frame, f"Password: {sequence}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        # ✅ 显示视频帧
        cv2.imshow("实时姿态检测", frame)

        # 如果按下 q 键也可以退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 一旦记录满 4 个数字，写入 JSON 并等待关闭
        if len(sequence) == 4:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({"password": sequence}, f, ensure_ascii=False)
                print(f"💾 写入 JSON 成功: {output_path}")
            SERVER_IP = "http://10.186.9.149:5000/upload"
            # 要发送的 checkpassword 内容
            data = {
                "password": sequence
            }

            try:
                response = requests.post(SERVER_IP, json=data)
                print(f"Server response: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error sending request: {e}")
            time.sleep(2)

            
            break  # 退出摄像头



if __name__ == "__main__":
    real_time_pose_estimation()
