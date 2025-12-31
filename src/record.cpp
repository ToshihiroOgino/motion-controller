#include <chrono>
#include <stdio.h>

#include "common/gpip_util.hpp"

using namespace std;
using namespace chrono;

int main(int argc, char const *argv[]) {
	printf("GPIO Pin Test Program\n");

	auto pin = GPIO_Pin(12);

	printf("Waiting for pin to become active...\n");
	pin.wait_for_active();

	printf("Pin is now active!\n");

	return 0;
}
