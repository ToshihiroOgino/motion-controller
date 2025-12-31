#ifndef GPIP_UTIL_HPP_
#define GPIP_UTIL_HPP_

#include <gpiod.hpp>

class GPIO_Pin {
  public:
	GPIO_Pin(uint32_t pin_offset);
	~GPIO_Pin();
	bool read_value();
	void wait_for_active();

  private:
	unsigned int pin_offset;
	std::unique_ptr<gpiod::chip> chip;
    std::unique_ptr<gpiod::line_request> request;
};

#endif /* GPIP_UTIL_HPP_ */
