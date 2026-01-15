#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "common/gpio_util.hpp"

using namespace std;
using namespace chrono;

#define PWM_FREQUENCY_HZ 38000
#define RETRY_COUNT 3
#define INTERVAL_MS 50
#define ON_DUTY_CYCLE 25

struct SensorData {
	long timestamp_us;
	bool value;
};

/**
 * @brief Read sensor data from CSV file
 * @param filename Path to the CSV file
 * @return Vector of sensor data records
 */
vector<SensorData> read_csv(const string &filename) {
	vector<SensorData> data;
	ifstream ifs(filename);

	if (!ifs.is_open()) {
		cerr << "Failed to open file: " << filename << endl;
		throw runtime_error("File open error");
	}

	string line;
	// Skip header
	getline(ifs, line);

	while (getline(ifs, line)) {
		if (line.empty()) {
			continue;
		}

		stringstream ss(line);
		string timestamp_str, value_str;

		if (!getline(ss, timestamp_str, ',')) {
			continue;
		}
		if (!getline(ss, value_str, ',')) {
			continue;
		}

		try {
			SensorData record;
			record.timestamp_us = stol(timestamp_str);
			record.value = stoi(value_str) != 0;
			data.emplace_back(record);
		} catch (const exception &e) {
			cerr << "Error parsing line: " << line << endl;
			cerr << "Exception: " << e.what() << endl;
			continue;
		}
	}

	ifs.close();
	cerr << "Read " << data.size() << " records from " << filename << endl;
	return data;
}

void send_data(const vector<SensorData> &data, GPIO_PWM &pwm) {
	auto start_at = high_resolution_clock::now();
	size_t data_index = 0;

	if (data[0].value) {
		pwm.set_duty_cycle(50);
	}

	while (data_index < data.size()) {
		auto now = high_resolution_clock::now();
		auto elapsed = duration_cast<microseconds>(now - start_at).count();

		const auto current_state_end_at = data[data_index].timestamp_us;
		if (elapsed >= current_state_end_at) {
			// Update PWM state
			const bool current_value = data[data_index].value;
			if (current_value) {
				pwm.set_duty_cycle(ON_DUTY_CYCLE);
			} else {
				pwm.set_duty_cycle(0);
			}
			data_index++;
		}
		this_thread::sleep_for(microseconds(100));
	}
}

int main(int argc, char const *argv[]) {
	if (argc < 2) {
		cerr << "Usage: " << argv[0] << " <csv_file>" << endl;
		cerr << "Example: " << argv[0] << " sensor_data.csv" << endl;
		return 1;
	}

	const string csv_filename = argv[1];

	const auto data = read_csv(csv_filename);
	if (data.empty()) {
		cerr << "No data to send" << endl;
		return 1;
	}

	cerr << "Start sending data..." << endl;

	try {
		GPIO_PWM pwm(1, PWM_FREQUENCY_HZ);
		pwm.enable();
		for (int i = 0; i < RETRY_COUNT; ++i) {
			send_data(data, pwm);
			this_thread::sleep_for(milliseconds(INTERVAL_MS));
		}
		pwm.disable();
		cerr << "Send completed" << endl;
	} catch (const exception &e) {
		cerr << "Error: " << e.what() << endl;
		return 1;
	}

	return 0;
}
