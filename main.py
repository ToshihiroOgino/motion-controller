import cv2
import mediapipe as mp
import sys

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def process_and_draw(image, results):
    """画像と検出結果を受け取り、描画と判定を行う共通関数"""
    annotated_image = image.copy()
    height, width, _ = annotated_image.shape

    if not results.pose_landmarks:
        return annotated_image

    # --- 1. 標準的な骨格の描画 ---
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
    )

    # --- 2. 挙手判定カスタムロジックと強調表示 ---
    lm = results.pose_landmarks.landmark

    # 左手の判定
    left_wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST]
    ref_point_left = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]  # 肩を基準
    is_left_raised = left_wrist.y < ref_point_left.y

    # 右手の判定
    right_wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
    ref_point_right = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]  # 肩を基準
    is_right_raised = right_wrist.y < ref_point_right.y

    # 描画処理
    if is_left_raised or is_right_raised:
        status_text = "Hand Raised!"

        if is_left_raised:
            cx, cy = int(left_wrist.x * width), int(left_wrist.y * height)
            cv2.circle(annotated_image, (cx, cy), 30, (0, 255, 0), -1)
            # status_text += " (Left)" # 必要であれば詳細を表示

        if is_right_raised:
            cx, cy = int(right_wrist.x * width), int(right_wrist.y * height)
            cv2.circle(annotated_image, (cx, cy), 30, (0, 255, 0), -1)
            # status_text += " (Right)"

        cv2.putText(
            annotated_image,
            status_text,
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 255, 0),
            3,
        )

    return annotated_image


def visualize_hand_raise(img_path):
    """静止画ファイル用の処理"""
    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        min_detection_confidence=0.5,
    ) as pose:

        image = cv2.imread(img_path)
        if image is None:
            print(f"Error: Could not load image at {img_path}")
            return

        # BGR -> RGB変換
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        # 描画処理（共通関数へ切り出し）
        annotated_image = process_and_draw(image, results)

        # 表示リサイズ
        height, width, _ = annotated_image.shape
        display_img = annotated_image
        if width > 1280:
            scale = 1280 / width
            display_img = cv2.resize(annotated_image, None, fx=scale, fy=scale)

        cv2.imshow("Hand Raise Detection (Image)", display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def run_webcam_mode():
    """Webカメラ用の処理"""
    cap = cv2.VideoCapture(0)  # 0番目のカメラデバイス
    if not cap.isOpened():
        print("Error: Camera not found.")
        return

    # Webカメラでは static_image_mode=False にしてトラッキングを有効にする
    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:

        print("Webカメラを開始します。'q'キーまたは'Esc'キーで終了します。")

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # 鏡のように操作しやすくするため左右反転させる（任意）
            image = cv2.flip(image, 1)

            # パフォーマンス向上のため、参照渡しで書き込み不可にする
            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # 推論実行
            results = pose.process(image_rgb)

            # 描画のために書き込み許可に戻す
            image.flags.writeable = True

            # 描画処理（共通関数を使用）
            annotated_image = process_and_draw(image, results)

            cv2.imshow("Hand Raise Detection (Camera)", annotated_image)

            # 'q' または Esc(27) で終了
            key = cv2.waitKey(5) & 0xFF
            if key == ord("q") or key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


def main():
    if len(sys.argv) == 1:
        # Source: Camera
        run_webcam_mode()
    else:
        # source: Image file
        img_path = sys.argv[1]
        visualize_hand_raise(img_path)


if __name__ == "__main__":
    main()
