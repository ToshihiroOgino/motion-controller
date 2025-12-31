#include <chrono>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdio.h>
#include <string>
#include <vector>

#include "common/gpip_util.hpp"

using namespace std;
using namespace chrono;

/**
 * @brief Read sensor data from a GPIO pin for a specified timeout duration.
 * @param pin GPIO pin object to read from.
 * @param timeout_ms Timeout duration in milliseconds.
 * @return Vector of pairs containing the timestamp (in microseconds) and the
 * pin value
 */
vector<pair<microseconds, bool>> read_sensor(GPIO_Pin &pin,
											 const int timeout_ms) {
	const auto timeout = milliseconds(timeout_ms);
	vector<pair<high_resolution_clock::time_point, bool>> readings;

	printf("Waiting for pin to become active...\n");
	pin.wait_for_active();
	const auto begining = high_resolution_clock::now();

	readings.emplace_back(begining, pin.read_value());
	auto prev_value = true;
	while (true) {
		const auto now = high_resolution_clock::now();
		const auto current_value = pin.read_value();
		if (current_value != prev_value) {
			readings.emplace_back(now, current_value);
			prev_value = current_value;
		}
		if (now - begining > timeout) {
			if (current_value) {
				readings.emplace_back(now, current_value);
			}
			break;
		}
	}

	vector<pair<microseconds, bool>> data;
	for (const auto &[time_point, value] : readings) {
		data.emplace_back(duration_cast<microseconds>(time_point - begining),
						  value);
	}
	return data;
}

void write_csv(const string &filename,
			   const vector<pair<microseconds, bool>> &data) {
	printf("Writing data to %s...\n", filename.c_str());
	ofstream ofs(filename);
	ofs << "timestamp_us,value\n";
	for (const auto &[timestamp, value] : data) {
		ofs << timestamp.count() << "," << value << "\n";
	}
	ofs.close();
	printf("Data written to %s\n", filename.c_str());
}

int main(int argc, char const *argv[]) {
	printf("GPIO Pin Test Program\n");

	auto pin = GPIO_Pin(18);

	const auto data = read_sensor(pin, 500);

	// Write to csv file
	const auto timestamp = chrono::system_clock::now();
	auto time_t_obj = std::chrono::system_clock::to_time_t(timestamp);
	std::stringstream ss;
	ss << "sensor_data_"
	   << put_time(std::localtime(&time_t_obj), "%Y%m%d%H%M%S") << ".csv";
	write_csv(ss.str(), data);

	return 0;
}
