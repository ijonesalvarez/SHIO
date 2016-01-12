#include <stdio.h>
#include <unistd.h>
#include <mraa/aio.h>

int main()
{
	uint16_t value = 0;
	char cmd_buf[1024];
	mraa_aio_context rotary;
	rotary = mraa_aio_init(0);

	while(1) {
		value = mraa_aio_read(rotary);
		snprintf(cmd_buf, sizeof(cmd_buf), "./send_udp.js rotary %d", value);
		system(cmd_buf);
		printf("%d\n", value);
		sleep(1);
}
mraa_aio_close(rotary);
return 0;
}
