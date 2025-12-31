#include "gpip_util.hpp"

#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

using namespace std;

#define PWM_SYSFS_PATH "/sys/class/pwm/pwmchip0"
#define ENABLE_FILENAME "enable"
#define DUTY_CYCLE_FILENAME "duty_cycle"

void _write_file(std::filesystem::path &path, const string &value) {
	auto ofs = std::ofstream(path);
	if (!ofs.is_open()) {
		cerr << "File stream is not open" << endl;
		throw runtime_error("File stream error");
	}
	ofs << value;
	ofs.flush();
	ofs.close();
}

GPIO_PWM::GPIO_PWM(uint32_t pwm_channel, uint32_t frequency_hz)
	: pwm_channel(pwm_channel), frequency_hz(frequency_hz) {
	const auto pwm_dir =
		filesystem::path(PWM_SYSFS_PATH) / ("pwm" + to_string(pwm_channel));
	this->enable_path = pwm_dir / ENABLE_FILENAME;
	this->duty_cycle_path = pwm_dir / DUTY_CYCLE_FILENAME;
}

GPIO_PWM::~GPIO_PWM() {
	disable();
}

void GPIO_PWM::enable() {
	this->set_duty_cycle(0);
	_write_file(this->enable_path, "1");
}

void GPIO_PWM::disable() {
	this->set_duty_cycle(0.0);
	_write_file(this->enable_path, "0");
}

void GPIO_PWM::set_duty_cycle(int duty_cycle) {
	if (duty_cycle < 0 || duty_cycle > 100) {
		cerr << "Duty cycle must be between 0 and 100" << endl;
		throw invalid_argument("Invalid duty cycle value");
	}
	write_pwm_sysfs(duty_cycle);
}

void GPIO_PWM::write_pwm_sysfs(int duty_cycle) {
	const double max_duty_cycle = 1e6 / frequency_hz;
	const double duty_cycle_val =
		(duty_cycle / 100.0) * (max_duty_cycle * 1'000);
	string duty_cycle_str = to_string(static_cast<uint64_t>(duty_cycle_val));
	_write_file(this->duty_cycle_path, duty_cycle_str);
}
