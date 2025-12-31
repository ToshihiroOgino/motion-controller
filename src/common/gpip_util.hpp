#ifndef GPIP_UTIL_HPP_
#define GPIP_UTIL_HPP_

#include <cstdint>
#include <fstream>
#include <gpiod.hpp>

class GPIO_Pin {
  public:
	GPIO_Pin(uint32_t pin_offset);
	~GPIO_Pin();
	bool read_value();
	void wait_for_active();

  private:
	uint32_t pin_offset;
	std::unique_ptr<gpiod::chip> chip;
	std::unique_ptr<gpiod::line_request> request;
};

class GPIO_PWM {
  public:
	GPIO_PWM(uint32_t pwm_channel, uint32_t frequency_hz);
	~GPIO_PWM();
	void set_duty_cycle(int duty_cycle);
	void enable();
	void disable();

  private:
	uint32_t pwm_channel;
	uint32_t frequency_hz;
	std::filesystem::path enable_path;
	std::filesystem::path duty_cycle_path;
	void write_pwm_sysfs(int duty_cycle);
};

#endif /* GPIP_UTIL_HPP_ */
