# Motion Controller

## Requirements

- Raspberry Pi 4B
- Python 3.12 (**not higher than 3.12**)

## Installation

```sh
pip install -r requirements.txt
```

## Hardware

UV Sensor

- 3.3V Power Supply
- GPIO 18: UV Sensor Output

UV LED

- 5V Power Supply
- GPIO 19: UV LED Output

## Setting

Append blow line to /boot/firmaere/config.txt

```plaintext
dtoverlay=pwm,pin=19,func=2
```

## Resources

- [GPIO Usage on Raspberry Pi Devices](https://pip.raspberrypi.com/categories/685-whitepapers-app-notes/documents/RP-006553-WP/A-history-of-GPIO-usage-on-Raspberry-Pi-devices-and-current-best-practices.pdf)
- [libgpiod/libgpiod.git](https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/?h=v2.1.x)
