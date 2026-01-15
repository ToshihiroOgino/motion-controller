#include "gpio_util.hpp"

#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>

using namespace std;

#define PWM_SYSFS_PATH "/sys/class/pwm/pwmchip0"

#define UNEXPORT_FILENAME "unexport"
#define EXPORT_FILENAME "export"

#define PERIOD_FILENAME "period"
#define ENABLE_FILENAME "enable"
#define DUTY_CYCLE_FILENAME "duty_cycle"

void _write_file(const std::filesystem::path &path, const string &value) {
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
	// Export the PWM channel
	const auto export_path = filesystem::path(PWM_SYSFS_PATH) / EXPORT_FILENAME;
	_write_file(export_path, to_string(pwm_channel));

	this_thread::sleep_for(chrono::milliseconds(100));

	const auto pwm_dir =
		filesystem::path(PWM_SYSFS_PATH) / ("pwm" + to_string(pwm_channel));
	this->enable_path = pwm_dir / ENABLE_FILENAME;
	this->duty_cycle_path = pwm_dir / DUTY_CYCLE_FILENAME;
	this->period_path = pwm_dir / PERIOD_FILENAME;

	if (!filesystem::exists(this->enable_path) ||
		!filesystem::exists(this->duty_cycle_path) ||
		!filesystem::exists(this->period_path)) {
		cerr << "Failed to export PWM channel " << pwm_channel << endl;
		throw runtime_error("PWM sysfs error");
	}

	this->set_frequency(frequency_hz);
}

GPIO_PWM::~GPIO_PWM() {
	disable();

	// Unexport the PWM channel
	const auto unexport_path =
		filesystem::path(PWM_SYSFS_PATH) / UNEXPORT_FILENAME;
	_write_file(unexport_path, to_string(pwm_channel));
}

void GPIO_PWM::enable() {
	this->set_duty_cycle(0);
	_write_file(this->enable_path, "1");
}

void GPIO_PWM::disable() {
	this->set_duty_cycle(0.0);
	_write_file(this->enable_path, "0");
}

void GPIO_PWM::set_frequency(uint32_t frequency_hz) {
	this->frequency_hz = frequency_hz;
	const double period_val = 1e9 / frequency_hz;
	string period_str = to_string(static_cast<uint64_t>(period_val));
	_write_file(this->period_path, period_str);
}

void GPIO_PWM::set_duty_cycle(int duty_cycle) {
	if (duty_cycle < 0 || duty_cycle > 100) {
		cerr << "Duty cycle must be between 0 and 100" << endl;
		throw invalid_argument("Invalid duty cycle value");
	}
	write_pwm_sysfs(duty_cycle);
}

void GPIO_PWM::write_pwm_sysfs(int duty_cycle) {
	const double max_duty_cycle = 1e9 / frequency_hz;
	const double duty_cycle_val = (duty_cycle / 100.0) * max_duty_cycle;
	string duty_cycle_str = to_string(static_cast<uint64_t>(duty_cycle_val));
	_write_file(this->duty_cycle_path, duty_cycle_str);
}
