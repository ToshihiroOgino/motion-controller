from gpiozero import DigitalInputDevice
import time
import datetime
import os

sensor = DigitalInputDevice(18, pull_up=None, active_state=False)
SAVE_DIR = "out"


def save_to_file(data):
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    filename = os.path.join(SAVE_DIR, f"ir_signal_{now_str}.csv")

    try:
        with open(filename, "w") as f:
            f.write("State,Duration_us\n")
            for state, duration in data:
                f.write(f"{state},{duration}\n")

        print(f"\n[成功] データを保存しました: {filename}")

    except IOError as e:
        print(f"\n[エラー] ファイル保存に失敗しました: {e}")


def main():
    print("=== 赤外線信号レコーダー (ファイル保存版) ===")
    print("待機中... リモコンのボタンを押してください")

    # 1. 信号の開始を待つ (最初のHigh->Lowのエッジ)
    sensor.wait_for_active()

    # 2. 記録開始
    print("信号検知！記録中...")
    timestamps = []

    # 高精度タイマーで計測開始
    start_time = time.perf_counter()
    last_time = start_time
    last_value = sensor.value  # 最初の状態 (恐らくActive)

    # タイムアウト設定 (秒)
    TIMEOUT = 0.1

    try:
        while True:
            now = time.perf_counter()
            current_value = sensor.value

            # 状態変化があった場合
            if current_value != last_value:
                # 経過時間を計算 (マイクロ秒)
                duration = int((now - last_time) * 1_000_000)
                timestamps.append((last_value, duration))

                last_time = now
                last_value = current_value

            # タイムアウト判定 (信号終了)
            if (now - last_time) > TIMEOUT:
                # 最後の状態も記録しておく (OFFに戻った時間など)
                duration = int((now - last_time) * 1_000_000)
                timestamps.append((last_value, duration))
                break

    except KeyboardInterrupt:
        print("\n中断されました")
        return

    # 3. ファイルへ保存
    if len(timestamps) > 0:
        print(f"検出されたエッジ数: {len(timestamps)}")
        save_to_file(timestamps)
    else:
        print("データが記録されませんでした。")


if __name__ == "__main__":
    main()
