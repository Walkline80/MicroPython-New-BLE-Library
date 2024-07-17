"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import bluetooth
from bluetooth import UUID
from machine import Timer
from ble import *


class Device(object):
	def __init__(self, data):
		# addr_type, addr, adv_type, rssi, adv_data = data
		self.addr_type  = data[0]
		self.addr       = bytes(data[1])
		self.adv_type   = data[2]
		self.rssi       = data[3]
		self.__adv_data = bytes(data[4])

		self.conn_handle = None

		self.profile = {
			'services': {}
		}

		# profile = {
		# 	'services': {
		# 		'uuid1': {
		# 			'start': 1,
		# 			'end'  : 2,
		# 			'characteristics': {
		# 				'uuid2': {
		# 					'start': 3,
		# 					'end'  : 4,
		# 					'descriptors': {
		# 						'uuid3': {
		# 							'start': 5,
		# 							'end'  : 6,
		# 						},
		# 					},
		# 				},
		# 				'uuid4': {
		# 					'start': 7,
		# 					'end'  : 8,
		# 				},
		# 			},
		# 		},
		# 	}
		# }

	@property
	def name(self) -> str:
		'''get device name or mac address'''
		return BLETools.decode_name(self.__adv_data) or BLETools.decode_mac(self.addr)

	@property
	def connectable(self) -> bool:
		return self.adv_type in (ADVType.IND, ADVType.DIRECT_IND, ADVType.SCAN_RSP) and self.rssi >= -80


class DeviceFactory(object):
	def __init__(self):
		self.__devices = []
		self.__addrs   = []
		self.__targets = set()

	def append(self, data):
		_, addr, _, _, _ = data

		if addr not in self.__addrs:
			self.__addrs.append(bytes(addr))
			self.__devices.append(Device(data))

	def remove(self, data):
		_, _, addr = data

		if addr in self.__addrs:
			device = self.find(addr=addr)

			self.__addrs.remove(bytes(addr))
			self.__devices.remove(device)

	def update(self, data):
		_, addr, _, rssi, adv_data = data

		device = self.find(addr=addr)

		if device:
			if adv_data not in device.__adv_data:
				device.__adv_data += bytes(adv_data)
				device.rssi = rssi

	def clear(self):
		self.__addrs.clear()
		self.__devices.clear()

	def count(self):
		return len(self.__devices)

	def find(self, addr: memoryview = None) -> Device | None:
		if addr:
			try:
				index = self.__addrs.index(bytes(addr))
				return self.__devices[index]
			except ValueError:
				return

	def devices(self) -> list:
		return self.__devices

	def set_targets(self, value: str | bytes | UUID | tuple | list = None):
		if isinstance(value, (str, bytes, UUID)):
			self.__targets.add(value)
		elif isinstance(value, (tuple, list)):
			self.__targets.update(value)

	def check(self, adv_data) -> bool:
		'''Check if it's a target device'''
		if len(self.__targets) == 0:
			return True

		result = False

		for target in self.__targets:
			if isinstance(target, str):
				result = target == BLETools.decode_name(adv_data)
			elif isinstance(target, bytes):
				result = target == BLETools.decode_mac(adv_data)
			elif isinstance(target, UUID):
				result = target in BLETools.decode_service_data(adv_data)[0]

		return result


class Scanner(object):
	MODE_SCANNER = 0
	MODE_CENTRAL = 1

	DESCRIPTORS_UUID = {
		UUID(0x2900), UUID(0x2901), UUID(0x2902), UUID(0x2903), UUID(0x2904),
		UUID(0x2905), UUID(0x2906), UUID(0x2907), UUID(0x2908), UUID(0x2909),
		UUID(0x290a), UUID(0x290b), UUID(0x290c), UUID(0x290d), UUID(0x290e),
		UUID(0x2910), UUID(0x2911)
	}

	def __init__(self,
			device_name: str = 'ble-scanner',
			scan_done_cb: function = None,
			central_connected_cb: function = None,
			service_done_cb: function = None,
			characteristic_done_cb: function = None,
			descriptor_done_cb: function = None,
			discover_done_cb: function = None
		):
		self.__ble     = bluetooth.BLE()
		self.__factory = DeviceFactory()
		self.__timer   = Timer(10)
		self.__mode    = self.MODE_SCANNER

		self.__scan_done_cb           = scan_done_cb
		self.__central_connected_cb   = central_connected_cb
		self.__service_done_cb        = service_done_cb
		self.__characteristic_done_cb = characteristic_done_cb
		self.__descriptor_done_cb     = descriptor_done_cb
		self.__discover_done_cb       = discover_done_cb

		self.__device_list = None

		self.__discovering_device         = False
		self.__discovering_characteristic = False
		self.__discovering_descriptor     = False

		self.__ble.config(gap_name=device_name)
		self.__ble.irq(self.__irq_callback)

		self.__ble.active(False)
		printf('Activating BLE...')
		self.__ble.active(True)
		printf(f'BLE Activated [{BLETools.decode_mac(self.__ble.config('mac')[1])}]')

		self.__ble.config(mtu=256)

	def __irq_callback(self, event, data):
		if event == IRQ.SCAN_RESULT:
			_, addr, adv_type, _, adv_data = data

			if adv_type == ADVType.SCAN_RSP:
				self.__factory.update(data)

			if self.__factory.check(adv_data):
				self.__factory.append(data)

				if self.__scan_timeout == 0:
					self.__ble.gap_scan(None)

		elif event == IRQ.SCAN_DONE:
			if self.__scan_done_cb:
				self.__scan_done_cb(self.__factory.devices())

			self.__discovering_device = True
			self.__device_list = self.__get_devices()
			self.__timer.init(
				mode=Timer.PERIODIC,
				period=50,
				callback=self.__discover_devices_timer_cb
			)

		elif event == IRQ.PERIPHERAL_CONNECT:
			conn_handle, _, addr = data
			device = self.__factory.find(addr=addr)

			if device:
				printf(f'Device [{device.name}] connected')

				if self.__mode == self.MODE_CENTRAL:
					if self.__central_connected_cb:
						self.__central_connected_cb(device)
					return

				device.conn_handle = conn_handle

				printf('Discovering services')
				self.__ble.gattc_discover_services(conn_handle)

		elif event == IRQ.PERIPHERAL_DISCONNECT:
			_, _, addr = data
			device = self.__factory.find(addr=addr)

			if device:
				printf(f'[{device.name}] Disconnected')
				# self.__factory.remove(data)

		elif event == IRQ.GATTC_SERVICE_RESULT:
			_, start_handle, end_handle, uuid = data

			self.__current_device.profile['services'].update(
				{str(uuid): {'start_handle': start_handle, 'end_handle': end_handle, 'characteristics': {}}})

		elif event == IRQ.GATTC_SERVICE_DONE:
			if self.__service_done_cb:
				self.__service_done_cb(self.__current_device)

			self.__services = self.__get_services()
			self.__discovering_characteristic = True

			printf('Discovering characteristics')

		elif event == IRQ.GATTC_CHARACTERISTIC_RESULT:
			_, end_handle, value_handle, properties, uuid = data

			self.__current_device.profile['services'][self.__current_service]['characteristics'].update(
				{str(uuid): {'end_handle': end_handle, 'value_handle': value_handle, 'properties': properties, 'descriptors': {}}})

		elif event == IRQ.GATTC_CHARACTERISTIC_DONE:
			self.__discovering_characteristic = True

			printf('Discovering descriptors')

		elif event == IRQ.GATTC_DESCRIPTOR_RESULT:
			_, desc_handle, uuid = data

			# if UUID(0x2900) <= uuid <= UUID(0x2911):
			# 	print(uuid)
			if uuid in self.DESCRIPTORS_UUID:
				self.__current_device.profile['services'][self.__current_service]['characteristics'][self.__current_characteristic]['descriptors'].update(
					{str(uuid): {'desc_handle': desc_handle}})

		elif event == IRQ.GATTC_DESCRIPTOR_DONE:
			self.__discovering_descriptor = True

	def __get_devices(self):
		for device in self.__factory.devices():
			if device.connectable:
				yield device

	def __get_services(self):
		device = self.__current_device

		if device.connectable:
			for service, values in device.profile['services'].items():
				yield device.conn_handle, values['start_handle'], values['end_handle'], service

	def __get_characteristics(self):
		device = self.__current_device

		if device.connectable:
			for service, s_values in device.profile['services'].items():
				for characteristic, c_values in s_values['characteristics'].items():
					yield device.conn_handle, s_values['start_handle'], s_values['end_handle'], service, characteristic

	def __discover_devices_timer_cb(self, timer=None):
		if self.__discovering_device:
			try:
				device = next(self.__device_list)
				print()
				printf(f'Discovering device: [{BLETools.decode_mac(device.addr)}], rssi: {device.rssi}')

				self.__current_device = device
				self.__discovering_device = False

				self.connect(device)
			except StopIteration:
				self.__timer.deinit()

				if self.__discover_done_cb:
					self.__discover_done_cb(self.__factory.devices())
		elif self.__discovering_characteristic:
			try:
				service = next(self.__services)
				self.__current_service = service[3]
				self.__discovering_characteristic = False

				# print(f'device: {self.__current_device.name}, discovering characteristics for service: [{self.__current_service}]')

				try:
					self.__ble.gattc_discover_characteristics(service[0], service[1], service[2])
				except OSError:
					pass
			except StopIteration:
				self.__discovering_characteristic = False

				if self.__characteristic_done_cb:
					self.__characteristic_done_cb(self.__current_device)

				self.__characteristics = self.__get_characteristics()
				self.__discovering_descriptor = True
		elif self.__discovering_descriptor:
			try:
				characteristic = next(self.__characteristics)
				self.__current_service = characteristic[3]
				self.__current_characteristic = characteristic[4]
				self.__discovering_descriptor = False

				# print(f'device: {self.__current_device.name}, service: {self.__current_service}, discovering descriptors for characteristics: [{self.__current_characteristic}]')

				try:
					self.__ble.gattc_discover_descriptors(characteristic[0], characteristic[1], characteristic[2])
				except OSError:
					pass
			except StopIteration:
				self.__discovering_descriptor = False

				if self.__descriptor_done_cb:
					self.__descriptor_done_cb(self.__current_device)

				self.disconnect(self.__current_device)

				self.__discovering_device = True

	def set_targets(self, value: str | bytes | UUID | tuple | list = None):
		self.__factory.set_targets(value)

	def scan(self, seconds: int = 5):
		if self.__mode == self.MODE_CENTRAL:
			return

		self.__factory.clear()
		self.__scan_timeout = seconds

		printf('Scaning', 'forever' if seconds == 0 else f'{seconds} second(s)')
		self.__ble.gap_scan(seconds * 1000, 50000, 50000, True)

	def connect(self, device:Device):
		self.__ble.gap_connect(device.addr_type, device.addr)

	def write(self, device:Device, handle:int, data: bytes):
		self.__ble.gattc_write(device.conn_handle, handle, data)

	def disconnect(self, device:Device):
		try:
			self.__ble.gap_disconnect(device.conn_handle)
		except OSError:
			pass

	@property
	def mode(self) -> int:
		return self.__mode

	@mode.setter
	def mode(self, value:int):
		if value in (self.MODE_SCANNER, self.MODE_CENTRAL):
			self.__mode = value


def run_test():
	def discover_done_cb(devices:list):
		print()
		printf(f'{len(devices)} device(s) discover completed')

		for device in devices:
			if not device.connectable:
				printf(f'Device: [{BLETools.decode_mac(device.addr)}]')
				continue

			printf(f'Device: [{BLETools.decode_mac(device.addr)}]:')
			for service, values in device.profile['services'].items():
				print(f'- {service}')
				for characteristic, values in values['characteristics'].items():
					print(f'  - {characteristic}')
					for key, value in values.items():
						print(f'    - {key}: {value}')

	def descriptor_done_cb(device:Device):
		printf(f'Descriptor discover completed')

	def characteristic_done_cb(device:Device):
		printf(f'Characteristics discover completed')

	def service_done_cb(device:Device):
		printf(f'Service discover completed, {len(device.profile['services'])} service(s) found')

	def scan_done_cb(devices:list):
		printf(f'Scan completed, {len(devices)} device(s) found')

		for device in devices:
			print(f'- [{device.name}] ({BLETools.decode_mac(device.addr)}), Connectable: {device.connectable}')

	scanner = Scanner(
		device_name='ble-scanner',
		scan_done_cb=scan_done_cb,
		service_done_cb=service_done_cb,
		characteristic_done_cb=characteristic_done_cb,
		descriptor_done_cb=descriptor_done_cb,
		discover_done_cb=discover_done_cb
	)

	scanner.set_targets('ble-config')
	scanner.scan(seconds=5)


if __name__ == '__main__':
	run_test()
