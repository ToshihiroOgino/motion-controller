import numpy as np
import time
import sys
from rpi_hardware_pwm import HardwarePWM

# リモコンのキャリア周波数: 38kHz
CARRIER_FREQ = 40_000
# GPIO19 -> PWM Channel 1
PWM_CHANNEL = 1

pwm = HardwarePWM(pwm_channel=PWM_CHANNEL, hz=CARRIER_FREQ)


def high_precision_sleep(duration_sec):
    target_time = time.perf_counter() + duration_sec
    while time.perf_counter() < target_time:
        pass


def play_ir_signal(filename):
    print(f"送信準備中: {filename} を読み込んでいます...")
    signal_data = np.loadtxt(filename, delimiter=",", dtype=int, skiprows=1)

    print(f"送信開始")

    pwm.start(0)
    try:
        for _ in range(3):
            for state, duration_us in signal_data:
                duration_sec = duration_us / 1_000_000.0
                if state == 1:
                    pwm.change_duty_cycle(25)
                else:
                    pwm.change_duty_cycle(0)
                # 指定時間待機
                high_precision_sleep(duration_sec)
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
