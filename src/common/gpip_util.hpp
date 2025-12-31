#ifndef GPIP_UTIL_HPP_
#define GPIP_UTIL_HPP_

#include <gpiod.h>

class GPIO_Pin {
  public:
	GPIO_Pin(uint32_t pin_offset);
	~GPIO_Pin();
	bool read_value();
	void wait_for_active();

  private:
	unsigned int pin_offset;
	struct gpiod_chip *chip;
	struct gpiod_line_info *line;
};

#endif /* GPIP_UTIL_HPP_ */
