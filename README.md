# Motion Controller

## Requirements

- Raspberry Pi 4B
- C++ Dev Environment
- Python 3.12 (**not higher than 3.12** because of mediapipe compatibility)
- CMake
- libgpiod-dev

## Installation

```sh
sudo apt install -y libgpiod-dev
pip install -r requirements.txt
```

## Hardware

IR Sensor

- 3.3V Power Supply
- GPIO 18: IR Sensor Output

IR LED

- 5V Power Supply (If you want to ensure IR LED brightness, use an external power supply)
- GPIO 19: IR LED Output

## Setting

In `/boot/firmware/config.txt`, add the following setting:

```plaintext
[all]
dtoverlay=pwm,pin=19,func=2
```

## Build

```sh
mkdir build
cd build
cmake ..
make
```

Executables:

- `bin/record`: Record IR signal
- `bin/send`: Transmit IR signal

## Resources

- [GPIO Usage on Raspberry Pi Devices](https://pip.raspberrypi.com/categories/685-whitepapers-app-notes/documents/RP-006553-WP/A-history-of-GPIO-usage-on-Raspberry-Pi-devices-and-current-best-practices.pdf)
- [libgpiod/libgpiod.git](https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/?h=v2.1.x)
