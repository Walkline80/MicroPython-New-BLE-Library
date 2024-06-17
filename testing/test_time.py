"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from machine import RTC
from profiles.time import TimeValues
from testing.utils.utilities import Utilities
from testing.utils.dispatcher import Dispatcher


MODE_TIME_SERVER = 0
MODE_TIME_CLIENT = 1

TIME_SERVER_LOCAL_NAME = 'time-server'

AdjustReason = TimeValues.Consts.AdjustReason
DSTOffset    = TimeValues.Consts.DSTOffset

def printf(msg, *args, **kwargs):
	print(f'\033[1;37m[INFO]\033[0m {msg}', *args, **kwargs)

def run_time_server_test():
	from devices.time.time_server import TimeServer

	TIMEZONE = 8

	RTC().datetime((
		2024, # year
		6,    # month
		6,   # day
		0,    # week of day
		12,   # hours
		30,   # minutes
		0,    # seconds
		0,    # subseconds 
	))

	time_server = TimeServer(
		device_name=TIME_SERVER_LOCAL_NAME
	)

	time_server.adjust_reason = AdjustReason.MANUAL
	time_server.fractions256  = 0
	time_server.time_zone     = TIMEZONE * 4
	time_server.dst_offset    = DSTOffset.STANDARD

def run_time_client_test():
	from devices.time.time_client import TimeClient

	def task_request_current_time():
		time_client.request_current_time()

	def request_localtime_info_cb(timezone: float, dst_offset: int):
		printf(f'Timezone: {timezone}')
		printf(f'DST Offset: {dst_offset} ({DSTOffset.OFFSETS_MAP[dst_offset]})')

	def request_current_time_cb(current_time: tuple, fractions256: int, adjust_reason: int):
		printf(f'Current Datetime: {current_time}')
		# printf(f'Fractions 256: {fractions256} ({int(fractions256 / 255 * 1000)} mm)')
		# printf(f'Adjust Reason: {adjust_reason} ({AdjustReason.REASONS_MAP[adjust_reason]})')

	def found_server_cb():
		tasks.add_work(task_request_current_time, 1000)

	tasks = Dispatcher()

	time_client = TimeClient(
		target_name=TIME_SERVER_LOCAL_NAME,
		found_server_cb=found_server_cb,
		request_current_time_cb=request_current_time_cb,
		request_localtime_info_cb=request_localtime_info_cb
	)
	time_client.scan()


if __name__ == '__main__':
	options = [
		'Time Server: Providing current time service',
		'Time Client: Reading current time data from server',
	]

	mode = Utilities.choose_an_option('Time Test Mode', options)

	if mode is not None:
		if mode == MODE_TIME_SERVER:
			run_time_server_test()
		else:
			run_time_client_test()
