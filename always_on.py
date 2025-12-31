from rpi_hardware_pwm import HardwarePWM
import time

# リモコンのキャリア周波数: 38kHz
CARRIER_FREQ = 38000
# GPIO19 -> PWM Channel 1
PWM_CHANNEL = 1

pwm = HardwarePWM(pwm_channel=PWM_CHANNEL, hz=CARRIER_FREQ)


if __name__ == "__main__":
    print(f"送信開始")
    pwm.start(0)
    try:
        pwm.change_duty_cycle(50)
        while True:
            # pwm.change_duty_cycle(50)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n送信が中断されました")
    finally:
        pwm.stop()
    print("送信完了")
