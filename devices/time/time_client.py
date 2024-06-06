"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import bluetooth
from struct import unpack
from ble import BLETools, ADVType, IRQ
from profiles.time import TimeValues as Values


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

		self.conn_handle  = None
		self.start_handle = None
		self.end_handle   = None

		self.handle_current_time          = None
		self.handle_localtime_information = None

	@property
	def name(self) -> str:
		'''get device name or mac address'''
		return BLETools.decode_name(self.__adv_data) or BLETools.decode_mac(self.addr)


class TimeClient(object):
	'''Time Client'''
	def __init__(self,
			device_name: str = 'time-client',
			target_name: str = 'time-server',
			found_server_cb: function = None,
			request_current_time_cb: function = None,
			request_localtime_info_cb: function = None):
		self.__ble         = bluetooth.BLE()
		self.__target      = None
		self.__target_name = target_name

		self.__current_time   = self.__current_datetime = self.__fractions256 = self.__adjust_reason = None
		self.__localtime_info = self.__time_zone = self.__dst_offset = None

		self.__found_server_cb           = found_server_cb
		self.__request_current_time_cb   = request_current_time_cb
		self.__request_localtime_info_cb = request_localtime_info_cb

		self.__ble.config(gap_name=device_name)
		self.__ble.irq(self.__irq_callback)

		self.__ble.active(False)
		printf('Activating BLE...')
		self.__ble.active(True)
		printf(f'BLE Activated [{BLETools.decode_mac(self.__ble.config('mac')[1])}]')

		self.__ble.config(mtu=256)

	def __irq_callback(self, event, data):
		if event == IRQ.SCAN_RESULT:
			if self.__check(data):
				self.__target = Device(data)
				self.__ble.gap_scan(None)

		elif event == IRQ.SCAN_DONE:
			printf(f'Scan Completed, Time Server{"" if self.__target else " not"} found')

			if self.__target:
				printf(f'Connecting to [{self.__target.name}]')
				self.__ble.gap_connect(self.__target.addr_type, self.__target.addr)

		elif event == IRQ.PERIPHERAL_CONNECT:
			conn_handle, _, _ = data

			if self.__target:
				printf(f'[{self.__target.name}] Connected')

				self.__target.conn_handle = conn_handle
				self.__ble.gattc_discover_services(conn_handle)

		elif event == IRQ.PERIPHERAL_DISCONNECT:
			if self.__target:
				printf(f'[{self.__target.name}] Disconnected')
				self.__target.conn_handle = None

		elif event == IRQ.GATTC_SERVICE_RESULT:
			_, start_handle, end_handle, uuid = data

			if uuid == bluetooth.UUID(Values.UUIDS.CURRENT_TIME_SERVICE):
				self.__target.start_handle = start_handle
				self.__target.end_handle   = end_handle

		elif event == IRQ.GATTC_SERVICE_DONE:
			conn_handle, _ = data

			if self.__target.start_handle and self.__target.end_handle:
				self.__ble.gattc_discover_characteristics(conn_handle,
					self.__target.start_handle, self.__target.end_handle)

		elif event == IRQ.GATTC_CHARACTERISTIC_RESULT:
			_, _, value_handle, _, uuid = data

			if   uuid == bluetooth.UUID(Values.UUIDS.CURRENT_TIME):
				self.__target.handle_current_time = value_handle
			elif uuid == bluetooth.UUID(Values.UUIDS.LOCAL_TIME_INFORMATION):
				self.__target.handle_localtime_information = value_handle

		elif event == IRQ.GATTC_CHARACTERISTIC_DONE:
			if self.__target.handle_current_time and\
			   self.__target.handle_localtime_information:
				self.request_localtime_info()
				self.request_current_time()

				if self.__found_server_cb:
					self.__found_server_cb()

		elif event == IRQ.GATTC_READ_RESULT:
			_, value_handle, char_data = data

			if value_handle == self.__target.handle_current_time:
				self.__current_time = unpack('<H8B', char_data)
				self.__current_datetime = self.__current_time[:7]
				self.__fractions256     = self.__current_time[-2]
				self.__adjust_reason    = self.__current_time[-1]
			elif value_handle == self.__target.handle_localtime_information:
				self.__localtime_info = unpack('<bB', char_data)
				self.__time_zone  = self.__localtime_info[0] / 4
				self.__dst_offset = self.__localtime_info[1]

		elif event == IRQ.GATTC_READ_DONE:
			if self.__current_time:
				if self.__request_current_time_cb:
					self.__request_current_time_cb(self.__current_datetime, self.__fractions256, self.__adjust_reason)
					self.__current_time = None

			if self.__localtime_info:
				if self.__request_localtime_info_cb:
					self.__request_localtime_info_cb(self.__time_zone, self.__dst_offset)
					self.__localtime_info = None

		elif event == IRQ.CONNECTION_UPDATE:
			pass
		elif event == IRQ.GET_SECRET:
			return None
		elif event == IRQ.SET_SECRET:
			return False
		else:
			printf(f'event: {event}, data: {data}')

	def __check(self, data):
		_, _, adv_type, rssi, adv_data = data

		return (BLETools.decode_name(adv_data) == self.__target_name or\
			   bluetooth.UUID(Values.UUIDS.CURRENT_TIME_SERVICE) in BLETools.decode_services(adv_data)) and\
			   adv_type in (ADVType.IND, ADVType.DIRECT_IND, ADVType.SCAN_RSP) and rssi >= -80


	# region Class Methods
	def disconnect(self):
		try:
			if self.__target:
				self.__ble.gap_disconnect(self.__target.conn_handle)
		except OSError:
			pass

	def scan(self, seconds=5):
		self.__target = None
		printf(f'Scaning for {seconds} second(s)...')
		self.__ble.gap_scan(seconds * 1000, 50000, 50000, True)

	def request_current_time(self):
		if self.__target is None:
			return

		if self.__target.handle_current_time:
			self.__ble.gattc_read(
				self.__target.conn_handle, self.__target.handle_current_time)

	def request_localtime_info(self):
		if self.__target is None:
			return

		if self.__target.handle_localtime_information:
			self.__ble.gattc_read(
				self.__target.conn_handle, self.__target.handle_localtime_information)
	# endregion


	# region Class Properties
	@property
	def adjust_reason(self) -> int:
		return self.__adjust_reason

	@property
	def timezone(self) -> float:
		return self.__time_zone

	@property
	def dst_offset(self) -> int:
		return self.__dst_offset
	# endregion
