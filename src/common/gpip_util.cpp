#include "gpip_util.hpp"

#include <iostream>
#include <string>

using namespace std;

#define GPIO_CHIP_PATH "/dev/gpiochip0"

GPIO_Pin::GPIO_Pin(unsigned int pin_offset) : pin_offset(pin_offset) {
	GPIO_Pin::chip = gpiod_chip_open(GPIO_CHIP_PATH);
	if (GPIO_Pin::chip == NULL) {
		const auto msg = string() + GPIO_CHIP_PATH;
		cerr << "Failed to open GPIO chip at " << GPIO_CHIP_PATH << endl;
		throw 1;
	}

	GPIO_Pin::line = gpiod_chip_get_line_info(GPIO_Pin::chip, pin_offset);
}

GPIO_Pin::~GPIO_Pin() {
	gpiod_chip_close(GPIO_Pin::chip);
}

bool GPIO_Pin::read_value() {
	auto val = gpiod_line_info_get_offset(GPIO_Pin::line);
	return val;
}

void GPIO_Pin::wait_for_active() {
	while (true) {
		if (read_value()) {
			break;
		}
	}
}
