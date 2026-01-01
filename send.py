import numpy as np
import time
import sys
from rpi_hardware_pwm import HardwarePWM

# PWM周波数: 38kHz (send.cppに合わせる)
PWM_FREQUENCY_HZ = 38000
# GPIO19 -> PWM Channel 1
PWM_CHANNEL = 1
# 送信リトライ回数
RETRY_COUNT = 3
# リトライ間隔(秒)
INTERVAL_SEC = 0.05
# ONの時のDuty Cycle (%)
ON_DUTY_CYCLE = 25

pwm = HardwarePWM(pwm_channel=PWM_CHANNEL, hz=PWM_FREQUENCY_HZ)


def read_csv(filename):
    """
    CSVファイルからセンサーデータを読み込む
    フォーマット: timestamp_us, value
    """
    print(f"読み込み中: {filename}")
    data = np.loadtxt(filename, delimiter=",", dtype=int, skiprows=1)
    print(f"{len(data)} 件のレコードを読み込みました")
    return data


def send_data(data):
    """
    タイムスタンプベースでデータを送信
    """
    start_time = time.perf_counter()
    data_index = 0
    
    # 最初のデータが1の場合、最初にPWMをONにする
    if data[0][1] == 1:
        pwm.change_duty_cycle(ON_DUTY_CYCLE)
    
    while data_index < len(data):
        elapsed_us = (time.perf_counter() - start_time) * 1_000_000
        current_state_end_at = data[data_index][0]
        
        if elapsed_us >= current_state_end_at:
            current_value = data[data_index][1]
            if current_value == 1:
                pwm.change_duty_cycle(ON_DUTY_CYCLE)
            else:
                pwm.change_duty_cycle(0)
            data_index += 1
    
        time.sleep(0.0001)


def play_ir_signal(filename):
    """
    赤外線信号を送信
    """
    data = read_csv(filename)
    
    if len(data) == 0:
        print("送信するデータがありません")
        return
    
    print("送信開始...")
    
    pwm.start(0)
    try:
        for i in range(RETRY_COUNT):
            send_data(data)
            if i < RETRY_COUNT - 1:
                time.sleep(INTERVAL_SEC)
    except KeyboardInterrupt:
        print("\n送信が中断されました")
    finally:
        pwm.stop()
    
    print("送信完了")


if __name__ == "__main__":

    csv_file_path: str = sys.argv[1] if len(sys.argv) > 1 else ""

    if csv_file_path == "":
        print(f"Usage: python {sys.argv[0]} <csv_file_path>")
        sys.exit(1)
    play_ir_signal(csv_file_path)
