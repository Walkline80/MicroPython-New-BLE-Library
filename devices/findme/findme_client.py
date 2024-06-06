"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import bluetooth
from ble import BLETools, ADVType, IRQ
from profiles.findme import FindMeValues as Values


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

		self.handle_alert_level = None

	@property
	def name(self) -> str:
		'''get device name or mac address'''
		return BLETools.decode_name(self.__adv_data) or BLETools.decode_mac(self.addr)


class FindMeClient(object):
	def __init__(self,
			device_name: str = 'findme-client',
			target_name: str = 'findme-server',
			found_target_cb: function = None):
		self.__ble           = bluetooth.BLE()
		self.__target        = None
		self.__target_name   = target_name
		self.__findme_values = Values()

		self.__found_target_cb = found_target_cb

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
			printf(f'Scan Completed, Find Me Server{"" if self.__target else " not"} found')

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
				self.__target = None

		elif event == IRQ.GATTC_SERVICE_RESULT:
			_, start_handle, end_handle, uuid = data

			if uuid == bluetooth.UUID(Values.UUIDS.IMMEDIATE_ALERT_SERVICE):
				self.__target.start_handle = start_handle
				self.__target.end_handle   = end_handle

		elif event == IRQ.GATTC_SERVICE_DONE:
			conn_handle, _ = data

			if self.__target.start_handle and self.__target.end_handle:
				self.__ble.gattc_discover_characteristics(conn_handle,
					self.__target.start_handle, self.__target.end_handle)

		elif event == IRQ.GATTC_CHARACTERISTIC_RESULT:
			_, _, value_handle, _, uuid = data

			if uuid == bluetooth.UUID(Values.UUIDS.ALERT_LEVEL):
				self.__target.handle_alert_level = value_handle

		elif event == IRQ.GATTC_CHARACTERISTIC_DONE:
			if self.__target.handle_alert_level:
				if self.__found_target_cb is not None:
					self.__found_target_cb()

		elif event == IRQ.GATTC_INDICATE:
			conn_handle, value_handle, status = data
			printf(f'GATTS Indicate Done [Handle: {conn_handle}, Value_Handle: {value_handle}, Status: {bytes(status)}]')

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
			   bluetooth.UUID(Values.UUIDS.IMMEDIATE_ALERT_SERVICE) in BLETools.decode_services(adv_data)) and\
			   adv_type in (ADVType.IND, ADVType.DIRECT_IND, ADVType.SCAN_RSP) and rssi >= -80

	# region Class Methods
	def disconnect(self):
		try:
			if self.__target:
				self.__ble.gap_disconnect(self.__target.conn_handle)
		except OSError:
			pass

	def scan(self, seconds: int = 5):
		self.__target = None
		printf('Scaning', 'forever' if seconds == 0 else f'{seconds} second(s)')
		self.__ble.gap_scan(seconds * 1000, 50000, 50000, True)

	def set_alert_level(self, level: int):
		if self.__target is None:
			return

		if level in Values.Consts.AlertLevel.LEVELS:
			self.__findme_values.immediate_alert_service.alert_level = level
			self.__ble.gattc_write(self.__target.conn_handle,
				self.__target.handle_alert_level,
				self.__findme_values.immediate_alert_service.alert_level)
	# endregion
