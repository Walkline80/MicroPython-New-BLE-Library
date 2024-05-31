"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from micropython import const
from struct import pack
from bluetooth import UUID
from ble import *


# Service UUIDs
UUID_DEVICE_INFORMATION = const(0x180A)
UUID_BATTERY_SERVICE = const(0x180F)
UUID_HUMAN_INTERFACE_DEVICE = const(0x1812)

# Characteristic UUIDs
UUID_MANUFACTURER_NAME_STRING = const(0x2A29)
UUID_MODEL_NUMBER_STRING = const(0x2A24)
UUID_SERIAL_NUMBER_STRING = const(0x2A25)
UUID_HARDWARE_REVISION_STRING = const(0x2A27)
UUID_FIRMWARE_REVISION_STRING = const(0x2A26)
UUID_SOFTWARE_REVISION_STRING = const(0x2A28)
UUID_PNP_ID = const(0x2A50)

UUID_BATTERY_LEVEL = const(0x2A19)

UUID_HID_INFORMATION = const(0x2A4A)
UUID_BOOT_KEYBOARD_INPUT_REPORT = const(0x2A22)
UUID_BOOT_KEYBOARD_OUTPUT_REPORT = const(0x2A32)
UUID_BOOT_MOUSE_INPUT_REPORT = const(0x2A33)
UUID_REPORT_MAP = const(0x2A4B)
UUID_REPORT = const(0x2A4D)
UUID_HID_CONTROL_POINT = const(0x2A4C)
UUID_PROTOCOL_MODE = const(0x2A4E)

# Descriptor UUIDs
UUID_REPORT_REFERENCE = const(0x2908)


class HIDProfile(Profile):
	'''只包含 HID 所需的三个服务'''
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self):
		super().__init__()
		self.__make_profile()

	def __make_profile(self):
		self.add_services(
			DeviceInformation().add_characteristics(
				ManufacturerNameString(),
				ModelNumberString(),
				SerialNumberString(),
				HardwareRevisionString(),
				FirmwareRevisionString(),
				SoftwareRevisionString(),
				PNPID(),
			),
			BatteryService().add_characteristics(
				BatteryLevel(),
			),
			HumanInterfaceDevice().add_characteristics(
				HIDInformation(),
				BootKeyboardInputReport(),
				BootKeyboardOutputReport(),
				BootMouseInputReport(),
				ReportMap(),
				HIDControlPoint(),
				ProtocolMode(),
			),
		)


class KeyboardProfile(HIDProfile):
	def __init__(self, report_count: int = 1):
		super().__init__()

		self.__report_count = report_count
		device = HumanInterfaceDevice()

		device.add_characteristics(
			Report().add_descriptors(
				ReportReference(), # input
			),
			Report().add_descriptors(
				ReportReference(), # output
			),
		)

		for _ in range(self.__report_count - 1):
			device.add_characteristics(
				Report().add_descriptors(
					ReportReference(), # input
				),
			)

		self.add_services(device)

	@property
	def report_count(self):
		return self.__report_count


class HIDValues(object):
	'''生成 BLE 设备信息字节串'''
	def __init__(self):
		self.device_information     = self.DeviceInformation()
		self.battery_service        = self.BatteryService()
		self.human_interface_device = self.HumanInterfaceDevice()


	class DeviceInformation(object):
		VENDOR_ID_SOURCE_BLUETOOTH = 1
		VENDOR_ID_SOURCE_USB       = 2

		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]

		def __init__(self):
			self.__manufacturer_name = 'Walkline Wang'
			self.__model_number      = 'MP_KB'
			self.__serial_number     = '4e897424-061d-4dd9-a798-454f79b37245'
			self.__firmware_revision = 'v0.1'
			self.__hardware_revision = 'v0.2'
			self.__software_revision = 'v0.3'

			# pnp_id related
			# self.__vendor_id_source = self.VENDOR_ID_SOURCE_USB
			# self.__vendor_id        = 0x045E # 0x045E: Microsoft
			self.__vendor_id_source = self.VENDOR_ID_SOURCE_BLUETOOTH
			self.__vendor_id        = 0x02E5 # 0x02E5: Espressif, 0x0006: Microsoft
			self.__product_id       = 0x0001
			self.__product_version  = 0x0001


		# region Properties
		@property
		def manufacturer_name(self) -> bytes:
			return pack(f'<{len(self.__manufacturer_name)}s', self.__manufacturer_name.encode())

		@manufacturer_name.setter
		def manufacturer_name(self, value: str):
			self.__manufacturer_name = value if isinstance(value, str) else str(value)

		@property
		def model_number(self) -> bytes:
			return pack(f'<{len(self.__model_number)}s', self.__model_number.encode())

		@model_number.setter
		def model_number(self, value: str):
			self.__model_number = value if isinstance(value, str) else str(value)

		@property
		def serial_number(self) -> bytes:
			return pack(f'<{len(self.__serial_number)}s', self.__serial_number.encode())

		@serial_number.setter
		def serial_number(self, value: str):
			self.__serial_number = value if isinstance(value, str) else str(value)

		@property
		def firmware_revision(self) -> bytes:
			return pack(f'<{len(self.__firmware_revision)}s', self.__firmware_revision.encode())

		@firmware_revision.setter
		def firmware_revision(self, value: str):
			self.__firmware_revision = value if isinstance(value, str) else str(value)

		@property
		def hardware_revision(self) -> bytes:
			return pack(f'<{len(self.__hardware_revision)}s', self.__hardware_revision.encode())

		@hardware_revision.setter
		def hardware_revision(self, value: str):
			self.__hardware_revision = value if isinstance(value, str) else str(value)

		@property
		def software_revision(self) -> bytes:
			return pack(f'<{len(self.__software_revision)}s', self.__software_revision.encode())

		@software_revision.setter
		def software_revision(self, value: str):
			self.__software_revision = value if isinstance(value, str) else str(value)

		@property
		def vendor_id_source(self) -> int:
			return self.__vendor_id_source

		@vendor_id_source.setter
		def vendor_id_source(self, value: int):
			if isinstance(value, int) and value in (self.VENDOR_ID_SOURCE_BLUETOOTH, self.VENDOR_ID_SOURCE_USB):
				self.__vendor_id_source = value

		@property
		def vendor_id(self) -> int:
			return self.__vendor_id

		@vendor_id.setter
		def vendor_id(self, value: int):
			if isinstance(value, int):
				self.__vendor_id = value

		@property
		def product_id(self) -> int:
			return self.__product_id

		@product_id.setter
		def product_id(self, value: int):
			if isinstance(value, int):
				self.__product_id = value

		@property
		def product_version(self) -> int:
			return self.__product_version

		@product_version.setter
		def product_version(self, value: int):
			if isinstance(value, int):
				self.__product_version = value

		@property
		def pnp_id(self) -> bytes:
			return pack('<BHHH', self.vendor_id_source, self.vendor_id, self.product_id, self.product_version)
		# endregion


	class BatteryService(object):
		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]

		def __init__(self):
			self.__battery_level = 100


		# region Properties
		@property
		def battery_level(self) -> bytes:
			return pack('<B', self.__battery_level)

		@battery_level.setter
		def battery_level(self, value: int):
			if isinstance(value, int) and 0 <= value <= 100:
				self.__battery_level = value
		# endregion


	class HumanInterfaceDevice(object):
		PROTOCOL_MODE_BOOT   = 0
		PROTOCOL_MODE_REPORT = 1

		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]

		def __init__(self):
			# [0]: bcdHID - HID 规范版本（0x0111: v1.11)
			# [1]: bCountryCode - 国家代码，默认不设置
			# [2]: Flags - 禁用 RemoteWake 和 NormallyConnectable
			self.__hid_information = [0x0111, 0x00, 0b00]

			self.__report_count = 1

			self.__protocol_mode = self.PROTOCOL_MODE_REPORT


		# region Properties
		@property
		def hid_information(self):
			return pack('<HBB', *self.__hid_information)

		# @hid_information.setter
		# def hid_information(self, value: tuple | list):
		# 	if isinstance(value, (tuple, list)) and len(value) == 3 and all(isinstance(v, int) for v in value):
		# 		self.__hid_information = value

		@property
		def report_count(self):
			return self.__report_count

		@report_count.setter
		def report_count(self, value: int):
			if isinstance(value, int):
				self.__report_count = value

		@property
		def report_reference(self):
			return [pack('<BB', report_id, 1) for report_id in range(1, self.__report_count + 1)]

		@property
		def report_reference_led(self):
			return pack('<BB', 1, 2)

		@property
		def protocol_mode(self):
			return pack('<B', self.__protocol_mode)

		@protocol_mode.setter
		def protocol_mode(self, value: int):
			if isinstance(value, int) and value in (self.PROTOCOL_MODE_BOOT, self.PROTOCOL_MODE_REPORT):
				self.__protocol_mode = value
		# endregion


# region Services
class DeviceInformation(Service):
	def __init__(self):
		super().__init__(UUID(UUID_DEVICE_INFORMATION))

class BatteryService(Service):
	def __init__(self):
		super().__init__(UUID(UUID_BATTERY_SERVICE))

class HumanInterfaceDevice(Service):
	def __init__(self):
		super().__init__(UUID(UUID_HUMAN_INTERFACE_DEVICE))
# endregion


# region Characteristics

# region DeviceInformation's Characteristics
class ManufacturerNameString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_MANUFACTURER_NAME_STRING), Flag.READ)

class ModelNumberString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_MODEL_NUMBER_STRING), Flag.READ)

class SerialNumberString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_SERIAL_NUMBER_STRING), Flag.READ)

class HardwareRevisionString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_HARDWARE_REVISION_STRING), Flag.READ)

class FirmwareRevisionString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_FIRMWARE_REVISION_STRING), Flag.READ)

class SoftwareRevisionString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_SOFTWARE_REVISION_STRING), Flag.READ)

class PNPID(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_PNP_ID), Flag.READ)
# endregion


# region BatteryService's Characteristics
class BatteryLevel(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_BATTERY_LEVEL), Flag.READ)
# endregion


# region HumanInterfaceDevice's Characteristics
class HIDInformation(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_HID_INFORMATION), Flag.READ)

class BootKeyboardInputReport(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_BOOT_KEYBOARD_INPUT_REPORT), Flag.READ_NOTIFY)

class BootKeyboardOutputReport(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_BOOT_KEYBOARD_OUTPUT_REPORT), Flag.READ_WRITE | Flag.WRITE_NO_RESPONSE)

class BootMouseInputReport(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_BOOT_MOUSE_INPUT_REPORT), Flag.READ_WRITE)

class ReportMap(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_REPORT_MAP), Flag.READ)

class Report(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_REPORT), Flag.READ_WRITE | Flag.NOTIFY | Flag.WRITE_NO_RESPONSE)

class HIDControlPoint(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_HID_CONTROL_POINT), Flag.WRITE_NO_RESPONSE)

class ProtocolMode(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_PROTOCOL_MODE), Flag.READ | Flag.WRITE_NO_RESPONSE)
# endregion

# endregion


# region Descriptors

# region Report Characteristic's Descriptors
class ReportReference(Descriptor):
	def __init__(self):
		super().__init__(UUID(UUID_REPORT_REFERENCE), Flag.READ_WRITE | Flag.WRITE_NO_RESPONSE)
# endregion

# endregion
