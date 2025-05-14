# main.py
from modules.detect_people import detect_people_in_image
from modules.pose_estimation import pose_estimation
from modules.which_pose import classify_pose
from modules.camera_with_pose import real_time_pose_estimation
def main():
    # 测试人物检测功能
    print("开始人物检测...")
    imagepath = 'pose/237462ea677b8038aab58ce221262fc.jpg'

    detect_people_in_image(
        image_path=imagepath,
        model_path='yolov8l.pt',
        output_dir='people_output',
        conf=0.25
    )

    # 测试姿态估计功能
    print("开始姿态估计...")
    pose_estimation(
        image_path=imagepath,
        model_path='yolov8n-pose.pt',
        output_dir='pose_output',
        conf=0.3
    )


if __name__ == "__main__":
    real_time_pose_estimation()
