'''
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ble-hid-controller
'''
from struct import pack
from .tools import BLETools


class BLEValues(object):
	'''生成 BLE 设备信息字节串'''
	def __init__(self):
		self.generic_access = self.GenericAccess()
		self.device_information = self.DeviceInformation()
		self.battery_service = self.BatteryService()
		self.human_interface_device = self.HumanInterfaceDevice()

	class GenericAccess(object):
		def __init__(self):
			self.__device_name = 'MP_HID'

			# (0x00f, 0x01)
			# category: Human Interface Device
			# subcategory: Keyboard
			self.__appearance = 961

			# (min, max, latency, timeout)
			# Minimum connection interval
			# Maximum connection interval
			# Slave Latency
			# Connection Supervision timeout multiplier
			# for min & max, 1 = 1.25ms
			self.__ppcp = [40, 80, 10, 300] # peripheral_preferred_connection_parameters

		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]


		# region Properties
		@property
		def device_name(self):
			return pack(f'<{len(self.__device_name)}s', self.__device_name.encode())

		@device_name.setter
		def device_name(self, value: str):
			self.__device_name = value

		@property
		def appearance(self):
			return pack('<H', self.__appearance)

		@appearance.setter
		def appearance(self, value: tuple[int, tuple]):
			if isinstance(value, tuple) and len(value) == 2:
				self.__appearance = BLETools.make_appearance(*value)
			else:
				self.__appearance = value if isinstance(value, int) else 961

		@property
		def ppcp(self):
			return pack('<4H', *self.__ppcp)

		@ppcp.setter
		def ppcp(self, value: tuple[tuple, list]):
			if isinstance(value, (tuple, list)) and len(value) == 4:
				self.__ppcp = value

		# CENTRAL_ADDRESS_RESOLUTION = pack('<b', 1)
		# endregion


	class DeviceInformation(object):
		def __init__(self):
			self.__manufacturer_name = 'Walkline Wang'
			self.__model_number = 'MP_KB'
			self.__serial_number = '4e897424-061d-4dd9-a798-454f79b37245'
			self.__firmware_revision = 'v0.1'
			self.__hardware_revision = 'v0.2'
			self.__software_revision = 'v0.3'
			self.__pnp_id = 0x02E5 # 0x02E5: Espressif, 0x0006: Microsoft

		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]


		# region Properties
		@property
		def manufacturer_name(self):
			return pack(f'<{len(self.__manufacturer_name)}s', self.__manufacturer_name.encode())

		@manufacturer_name.setter
		def manufacturer_name(self, value: str):
			self.__manufacturer_name = value

		@property
		def model_number(self):
			return pack(f'<{len(self.__model_number)}s', self.__model_number.encode())

		@model_number.setter
		def model_number(self, value: str):
			self.__model_number = value

		@property
		def serial_number(self):
			return pack(f'<{len(self.__serial_number)}s', self.__serial_number.encode())

		@serial_number.setter
		def serial_number(self, value: str):
			self.__serial_number = value

		@property
		def firmware_revision(self):
			return pack(f'<{len(self.__firmware_revision)}s', self.__firmware_revision.encode())

		@firmware_revision.setter
		def firmware_revision(self, value: str):
			self.__firmware_revision = value

		@property
		def hardware_revision(self):
			return pack(f'<{len(self.__hardware_revision)}s', self.__hardware_revision.encode())

		@hardware_revision.setter
		def hardware_revision(self, value: str):
			self.__hardware_revision = value

		@property
		def software_revision(self):
			return pack(f'<{len(self.__software_revision)}s', self.__software_revision.encode())

		@software_revision.setter
		def software_revision(self, value: str):
			self.__software_revision = value

		@property
		def pnp_id(self):
			return pack('<BHHH', 1, self.__pnp_id, 0x01, 0x01)

		@pnp_id.setter
		def pnp_id(self, value: int):
			self.__pnp_id = value
		# endregion


	class BatteryService(object):
		def __init__(self):
			self.__battery_level = 100

		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]


		# region Properties
		@property
		def battery_level(self):
			return pack('<B', self.__battery_level)

		@battery_level.setter
		def battery_level(self, value: int):
			self.__battery_level = value
		# endregion


	class HumanInterfaceDevice(object):
		def __init__(self):
			# [0]: bcdHID - HID 规范版本（0x0111: v1.11)
			# [1]: bCountryCode - 国家代码，默认不设置
			# [2]: Flags - 禁用 RemoteWake 和 NormallyConnectable
			self.__hid_information = [0x0111, 0x00, 0b00]

			self.__report_count = 1

			# 该服务可以有多个 report，每个 report 下都要有一个 report reference
			# 用于记录 report id
			# self.__report_reference = []

			self.__protocol_mode = 1

		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]


		# region Properties
		@property
		def hid_information(self):
			return pack('<HBB', self.__hid_information[0], self.__hid_information[1], self.__hid_information[2])

		@hid_information.setter
		def hid_information(self, value: tuple[tuple, list]):
			if isinstance(value, (tuple, list)) and len(value) == 3:
				self.__hid_information = value

		# BOOT_KEYBOARD_INPUT_REPORT
		# BOOT_KEYBOARD_OUTPUT_REPORT
		# BOOT_MOUSE_INPUT_REPORT

		@property
		def report_count(self):
			return self.__report_count

		@report_count.setter
		def report_count(self, value: int):
			self.__report_count = value

		@property
		def report_reference(self):
			return [pack('<BB', report_id, 1) for report_id in range(1, self.__report_count + 1)]

		# HID_CONTROL_POINT

		@property
		def protocol_mode(self):
			return pack('<B', self.__protocol_mode)

		@protocol_mode.setter
		def protocol_mode(self, value: int):
			self.__protocol_mode = value
		# endregion
