import cv2
import mediapipe as mp
import sys
import os
from datetime import datetime
import time
import threading
from collections import deque
import subprocess

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# 定数定義
CAPTURE_INTERVAL = 0.3  # カメラキャプチャ間隔（秒）
STABLE_FRAMES_REQUIRED = 1  # 状態を確定するのに必要なフレーム数
SEND_EXECUTABLE_PATH = "build/bin/send"  # 送信コマンドの実行ファイルパス
SIGNAL_FILE_PATH = "./signal/toggle.csv"  # トグル信号のCSVファイルパス


def process_and_draw(image, results):
    """画像と検出結果を受け取り、描画と判定を行う共通関数"""
    annotated_image = image.copy()
    height, width, _ = annotated_image.shape

    if not results.pose_landmarks:
        return annotated_image, False

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

    # いずれかの手が上がっているか
    hand_raised = is_left_raised or is_right_raised

    # 描画処理
    if hand_raised:
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

    return annotated_image, hand_raised


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
        annotated_image, _ = process_and_draw(image, results)

        # 結果を保存
        output_dir = "captured_images"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"pose_{timestamp}.jpg")
        cv2.imwrite(output_path, annotated_image)
        print(f"Saved pose detection result to: {output_path}")


def run_webcam_mode():
    """Webカメラ用の処理（GUI不要モード・マルチスレッド版）"""
    cap = cv2.VideoCapture(0)  # 0番目のカメラデバイス
    if not cap.isOpened():
        print("Error: Camera not found.")
        return

    # 出力ディレクトリの作成
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    # 共有変数
    latest_image = None
    latest_results = None
    running = True
    lock = threading.Lock()

    def camera_capture_thread():
        """カメラキャプチャと姿勢検出を行うスレッド（画像保存は行わない）"""
        nonlocal latest_image, latest_results, running

        # 手の状態管理用変数
        previous_hand_state = None  # 前回の確定した状態
        STABLE_FRAMES_REQUIRED = 1  # 状態を確定するのに必要なフレーム数
        state_history = deque(maxlen=STABLE_FRAMES_REQUIRED)  # 固定長の状態履歴リスト

        with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as pose:

            while running:
                start_at = time.perf_counter()
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    time.sleep(CAPTURE_INTERVAL)
                    continue

                # 鏡のように操作しやすくするため左右反転させる
                image = cv2.flip(image, 1)

                # パフォーマンス向上のため、参照渡しで書き込み不可にする
                image.flags.writeable = False
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # 推論実行
                results = pose.process(image_rgb)

                # 描画のために書き込み許可に戻す
                image.flags.writeable = True

                # 手が上がっているかどうかを検出
                hand_raised = False
                if results.pose_landmarks:
                    lm = results.pose_landmarks.landmark
                    left_wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST]
                    ref_point_left = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
                    is_left_raised = left_wrist.y < ref_point_left.y

                    right_wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
                    ref_point_right = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                    is_right_raised = right_wrist.y < ref_point_right.y

                    hand_raised = is_left_raised or is_right_raised

                # 状態履歴に追加（固定長なので古いものは自動的に削除される）
                state_history.append(hand_raised)

                # 状態が安定しているかチェック（全要素が同じ状態）
                if (
                    len(state_history) == STABLE_FRAMES_REQUIRED
                    and len(set(state_history)) == 1
                ):
                    current_stable_state = state_history[0]
                    if (
                        previous_hand_state is None
                        or previous_hand_state != current_stable_state
                    ):
                        # 状態が変化した（または初回）
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        state_str = "UP" if current_stable_state else "DOWN"
                        print(f"[{timestamp}] Hand state: {state_str}")
                        
                        # 手が上がった瞬間にコマンドを実行
                        if current_stable_state and previous_hand_state is not None:
                            try:
                                subprocess.run(
                                    [SEND_EXECUTABLE_PATH, SIGNAL_FILE_PATH],
                                    check=True,
                                    capture_output=True,
                                    text=True
                                )
                                print(f"[{timestamp}] Command executed: {SEND_EXECUTABLE_PATH} {SIGNAL_FILE_PATH}")
                            except subprocess.CalledProcessError as e:
                                print(f"[{timestamp}] Command failed: {e}")
                            except FileNotFoundError:
                                print(f"[{timestamp}] Command not found: {SEND_EXECUTABLE_PATH}")
                        
                        previous_hand_state = current_stable_state

                # 結果を共有変数に保存（画像保存はしない）
                with lock:
                    latest_image = image
                    latest_results = results

                # インターバルを設けて負荷を減らす
                end_at = time.perf_counter()
                elapsed = end_at - start_at

                time.sleep(max(0, CAPTURE_INTERVAL - elapsed))

    print("Webカメラを開始します。")
    print("'c'キーを入力してEnter: カメラをキャプチャして姿勢検出結果を保存")
    print("'q'キーを入力してEnter: 終了")

    # カメラキャプチャスレッドを開始
    capture_thread = threading.Thread(target=camera_capture_thread, daemon=True)
    capture_thread.start()

    # メインスレッドでキーボード入力を受け取り、画像保存を行う
    while running:
        try:
            key = input().strip().lower()

            if key == "c":
                # 最新のキャプチャ画像を保存
                with lock:
                    if latest_image is not None and latest_results is not None:
                        # 描画処理（共通関数を使用）
                        annotated_image, _ = process_and_draw(
                            latest_image.copy(), latest_results
                        )

                        # タイムスタンプ付きで保存
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_path = os.path.join(
                            output_dir, f"capture_{timestamp}.jpg"
                        )
                        cv2.imwrite(output_path, annotated_image)
                        print(f"Captured and saved to: {output_path}")
                    else:
                        print("No image available yet. Please wait...")

            elif key == "q":
                print("Exiting...")
                running = False
                break

        except EOFError:
            # 標準入力が閉じられた場合
            running = False
            break

    # カメラスレッドの終了を待つ（最大1秒）
    capture_thread.join(timeout=1.0)

    cap.release()
    print("Camera released.")


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
