#include "gpip_util.hpp"

#include <iostream>
#include <string>

using namespace std;

#define GPIO_CHIP_PATH "/dev/gpiochip0"

GPIO_Pin::GPIO_Pin() {
	GPIO_Pin::chip = gpiod_chip_open(GPIO_CHIP_PATH);
	if (GPIO_Pin::chip == NULL) {
		const auto msg = string() + GPIO_CHIP_PATH;
		cerr << "Failed to open GPIO chip at " << GPIO_CHIP_PATH << endl;
		throw 1;
	}

	GPIO_Pin::line = gpiod_chip_get_line_info(GPIO_Pin::chip, 4);
}

GPIO_Pin::~GPIO_Pin() {
	gpiod_chip_close(GPIO_Pin::chip);
}
