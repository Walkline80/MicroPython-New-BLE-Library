"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import time
import bluetooth
from ble import BLETools, ADVType, IRQ
from profiles.findme import FindMeValues


MODE_FINDME_SERVER = 0
MODE_FINDME_CLIENT = 1

FINDME_SERVER_LOCAL_NAME = 'findme-target'

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

		self.conn_handle        = None
		self.start_handle       = None
		self.end_handle         = None
		self.handle_alert_level = None

	@property
	def name(self) -> str:
		'''get device name or mac address'''
		return BLETools.decode_name(self.__adv_data) or BLETools.decode_mac(self.addr)


class FindMeLocator(object):
	def __init__(self,
			device_name: str = 'findme-locator',
			found_target_cb: function = None):
		self.__ble             = bluetooth.BLE()
		self.__target          = None
		self.__found_target_cb = found_target_cb
		self.__findme_values   = FindMeValues()

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
			printf(f'Scan Completed, Find Me Target{"" if self.__target else " not"} found')

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
			conn_handle, start_handle, end_handle, uuid = data

			if uuid == bluetooth.UUID(FindMeValues.UUIDS.IMMEDIATE_ALERT_SERVICE):
				self.__target.start_handle  = start_handle
				self.__target.end_handle    = end_handle
		elif event == IRQ.GATTC_SERVICE_DONE:
			conn_handle, _ = data

			if self.__target.start_handle and self.__target.end_handle:
				self.__ble.gattc_discover_characteristics(
					conn_handle,
					self.__target.start_handle,
					self.__target.end_handle
				)
		elif event == IRQ.GATTC_CHARACTERISTIC_RESULT:
			_, _, value_handle, _, uuid = data

			if uuid == bluetooth.UUID(FindMeValues.UUIDS.ALERT_LEVEL):
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
		elif event == IRQ.SET_SECRET:
			return False
		elif event == IRQ.GET_SECRET:
			return None
		else:
			printf(f'event: {event}, data: {data}')

	def __check(self, data):
		_, _, adv_type, rssi, adv_data = data

		return (BLETools.decode_name(adv_data) == FINDME_SERVER_LOCAL_NAME or\
			   bluetooth.UUID(FindMeValues.UUIDS.IMMEDIATE_ALERT_SERVICE) in BLETools.decode_services(adv_data)) and\
			   adv_type in (ADVType.IND, ADVType.DIRECT_IND, ADVType.SCAN_RSP) and rssi >= -80

	def disconnect(self):
		try:
			if self.__target:
				self.__ble.gap_disconnect(self.__target.conn_handle)
		except OSError:
			pass

	def scan(self, seconds=5):
		self.__target = None
		printf('Scaning', 'forever' if seconds == 0 else f'{seconds} second(s)')
		self.__ble.gap_scan(seconds * 1000, 50000, 50000, True)

	def set_alert_level(self, level: int):
		if self.__target and level in FindMeValues.Consts.ALERT_LEVELS:
			self.__findme_values.immediate_alert_service.alert_level = level
			self.__ble.gattc_write(
				self.__target.conn_handle, self.__target.handle_alert_level,
				self.__findme_values.immediate_alert_service.alert_level
			)


def run_findme_target_test():
	from devices.findme.findmeserver import FindMeServer

	def alert_level_cb(level: int):
		print(f'Received a new alert at level: {level} ({FindMeValues.Consts.ALERT_LEVELS_MAP[level]})')

	findme_server = FindMeServer(
		device_name=FINDME_SERVER_LOCAL_NAME,
		# alert_level_cb=alert_level_cb
		alert_level_cb=lambda level: printf(
		f'Received a new alert at level: {level} ({FindMeValues.Consts.ALERT_LEVELS_MAP[level]})'
		)
	)

def run_findme_locator_test():
	def found_target_cb():
		alert_level = FindMeValues.Consts.ALERT_LEVEL_HIGH_ALERT
		printf(f'Set Alert Level to {alert_level} ({FindMeValues.Consts.ALERT_LEVELS_MAP[alert_level]})')
		findme_locator.set_alert_level(alert_level)

		time.sleep(2)
		findme_locator.disconnect()

	findme_locator = FindMeLocator(found_target_cb=found_target_cb)
	findme_locator.scan(0)

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
		'Find Me Server: Acting as a Find Me Target',
		'Find Me Client: Acting as a Find Me Locator',
	]

	mode = choose_an_option('Find Me Test Mode', options)

	if mode is not None:
		if mode == MODE_FINDME_SERVER:
			run_findme_target_test()
		else:
			run_findme_locator_test()
