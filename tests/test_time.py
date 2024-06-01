"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import bluetooth
from ble import BLETools, IRQ
from struct import unpack


MODE_TIME_SERVER = 0
MODE_TIME_CLIENT = 1

ADJUST_REASON_MANUAL   = 0b0001
ADJUST_REASON_EXTERNAL = 0b0010
ADJUST_REASON_TIMEZONE = 0b0100
ADJUST_REASON_DST      = 0b1000

DST_OFFSET_STANDARD       = 0
DST_OFFSET_HALF_DAYLIGHT  = 2 # (+ 0.5h)
DST_OFFSET_DAYLIGHT       = 4 # (+ 1h)
DST_OFFSET_DOUBLEDAYLIGHT = 8 # (+ 2h)

CURRENT_TIME_SERVICE_UUID   = bluetooth.UUID(0x1805)
CURRENT_TIME_UUID           = bluetooth.UUID(0x2A2B)
LOCAL_TIME_INFORMATION_UUID = bluetooth.UUID(0x2A0F)
TIME_SERVER_LOCAL_NAME       = 'time-server'

def printf(msg, *args, **kwargs):
	print(f'\033[1;37m[INFO]\033[0m {msg}', *args, **kwargs)


class Device(object):
	def __init__(self, data):
		# addr_type, addr, adv_type, rssi, adv_data = data
		self.addr_type  = data[0]
		self.addr       = bytes(data[1])
		self.adv_type   = data[2]
		self.__rssi     = data[3]
		self.__adv_data = bytes(data[4])

		self.name          = BLETools.decode_name(self.__adv_data) or BLETools.decode_mac(self.addr)
		self.conn_handle   = None
		self.is_time_server = False
		self.start_handle  = 0
		self.end_handle    = 0

		self.handle_current_time           = None
		self.handle_local_time_information = None


class TimeClient(object):
	def __init__(self, device_name: str = 'time-client', found_server_cb: function = None):
		self.__ble             = bluetooth.BLE()
		self.__time_server     = None
		self.__found_server_cb = found_server_cb

		self.__write = self.__ble.gattc_write
		self.__read  = self.__ble.gattc_read

		self.__ble.config(gap_name=device_name)
		self.__ble.irq(self.__irq_callback)

		self.__ble.active(False)
		printf('Activating BLE...')
		self.__ble.active(True)
		printf(f'BLE Activated [{BLETools.decode_mac(self.__ble.config('mac')[1])}]')

		self.__ble.config(mtu=256)

	def __irq_callback(self, event, data):
		if event == IRQ.PERIPHERAL_CONNECT:
			conn_handle, addr_type, addr = data

			if self.__time_server:
				printf(f'[{self.__time_server.name}] Connected')
				self.__time_server.conn_handle = conn_handle
				self.__ble.gattc_discover_services(conn_handle)
		elif event == IRQ.PERIPHERAL_DISCONNECT:
			if self.__time_server:
				printf(f'[{self.__time_server.name}] Disconnected')
				self.__time_server.conn_handle = None
		elif event == IRQ.SCAN_RESULT:
			addr_type, addr, adv_type, rssi, adv_data = data

			if self.__check(adv_data):
				self.__time_server = Device(data)
				self.__ble.gap_scan(None)
		elif event == IRQ.SCAN_DONE:
			printf(f'Scan Completed, Time Server{"" if self.__time_server else " not"} found')

			if self.__time_server:
				printf(f'Connecting to [{self.__time_server.name}]')
				self.__ble.gap_connect(self.__time_server.addr_type, self.__time_server.addr)
		elif event == IRQ.GATTC_SERVICE_RESULT:
			conn_handle, start_handle, end_handle, uuid = data

			if uuid == CURRENT_TIME_SERVICE_UUID:
				self.__time_server.is_time_server = True
				self.__time_server.start_handle  = start_handle
				self.__time_server.end_handle    = end_handle
		elif event == IRQ.GATTC_SERVICE_DONE:
			conn_handle, status = data

			if self.__time_server.is_time_server:
				self.__ble.gattc_discover_characteristics(
					conn_handle,
					self.__time_server.start_handle,
					self.__time_server.end_handle
				)
		elif event == IRQ.GATTC_CHARACTERISTIC_RESULT:
			conn_handle, end_handle, value_handle, properties, uuid = data

			if uuid == CURRENT_TIME_UUID:
				self.__time_server.handle_current_time = value_handle
			elif uuid == LOCAL_TIME_INFORMATION_UUID:
				self.__time_server.handle_local_time_information = value_handle
		elif event == IRQ.GATTC_CHARACTERISTIC_DONE:
			if self.__time_server.handle_current_time and self.__time_server.handle_local_time_information:
				if self.__found_server_cb is not None:
					self.__found_server_cb()
		elif event == IRQ.GATTC_READ_RESULT:
			conn_handle, value_handle, char_data = data

			if value_handle == self.__time_server.handle_current_time:
				printf(unpack('<H8B', char_data))
			elif value_handle == self.__time_server.handle_local_time_information:
				printf(unpack('<bB', char_data))
		elif event == IRQ.GATTC_READ_DONE:
			pass
		elif event == IRQ.CONNECTION_UPDATE:
			pass
		elif event == IRQ.SET_SECRET:
			return False
		elif event == IRQ.GET_SECRET:
			return None
		else:
			printf(f'event: {event}, data: {data}')

	def __check(self, adv_data):
		return BLETools.decode_name(adv_data) == TIME_SERVER_LOCAL_NAME

	def scan(self, seconds=5):
		self.__time_server = None
		printf(f'Scaning for {seconds} second(s)...')
		self.__ble.gap_scan(seconds * 1000, 50000, 50000, True)

	def get_info(self):
		if self.__time_server and self.__time_server.handle_current_time and self.__time_server.handle_local_time_information:
			self.__read(self.__time_server.conn_handle, self.__time_server.handle_current_time)
			self.__read(self.__time_server.conn_handle, self.__time_server.handle_local_time_information)


def run_time_server_test():
	from machine import RTC

	from devices.time.timeserver import TimeServer


	TIMEZONE = 8

	RTC().datetime((
		2024, # year
		5,    # month
		22,   # day
		0,    # week of day
		12,   # hours
		30,   # minutes
		0,    # seconds
		0,    # subseconds 
	))

	time_server = TimeServer(TIME_SERVER_LOCAL_NAME) 

	time_server.adjust_reason = ADJUST_REASON_MANUAL
	time_server.fractions256  = 0
	time_server.time_zone     = TIMEZONE * 4
	time_server.dst_offset    = DST_OFFSET_STANDARD

def run_time_client_test():
	def found_server_cb():
		time_client.get_info()

	time_client = TimeClient(found_server_cb=found_server_cb)
	time_client.scan()

def choose_an_option(title, options):
	print(f'\n{title}:')

	for index, option in enumerate(options, start=1):
		if index == 1:
			print(f'\x1b[32m  [{index}] {option}\033[0m')
		else:
			print(f'  [{index}] {option}')

	selected = None

	while True:
		try:
			selected = input('Choose an option: ')

			if selected == '':
				return 0

			selected = int(selected)

			assert type(selected) is int and 0 < selected <= len(options)

			return selected - 1
		except KeyboardInterrupt:
			return
		except:
			pass


if __name__ == '__main__':
	options = [
		'Time Server: Providing current time service',
		'Time Client: Reading current time data from server',
	]

	mode = choose_an_option('Time Test Mode', options)

	if mode is not None:
		if mode == MODE_TIME_SERVER:
			run_time_server_test()
		else:
			run_time_client_test()
