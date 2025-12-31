#include "gpip_util.hpp"

#include <filesystem>
#include <iostream>
#include <string>

using namespace std;

#define GPIO_CHIP_PATH "/dev/gpiochip0"

GPIO_Pin::GPIO_Pin(unsigned int pin_offset) : pin_offset(pin_offset) {
	this->chip =
		std::make_unique<gpiod::chip>(filesystem::path(GPIO_CHIP_PATH));

	this->request = std::make_unique<gpiod::line_request>(
		chip->prepare_request()
			.set_consumer("uv-reader")
			.add_line_settings(pin_offset, gpiod::line_settings().set_direction(
											   gpiod::line::direction::INPUT))
			.do_request());
}

GPIO_Pin::~GPIO_Pin() {
	if (this->chip != nullptr) {
		this->chip->close();
	}
}

bool GPIO_Pin::read_value() {
	if (!chip || !request) {
		cerr << "GPIO chip is not initialized." << endl;
		throw std::runtime_error("GPIO not initialized");
	}

	const auto value = request->get_value(this->pin_offset);
	// Because of the pull-up resistor, ACTIVE means LOW voltage level.
	return value == gpiod::line::value::INACTIVE;
}

void GPIO_Pin::wait_for_active() {
	while (true) {
		if (read_value()) {
			break;
		}
	}
}
