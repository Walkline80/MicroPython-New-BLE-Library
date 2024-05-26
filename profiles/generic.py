"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from micropython import const
from struct import pack
from bluetooth import UUID

try:
	from ble import *
except ImportError:
	from ..ble import *


# Service UUIDs
UUID_GENERIC_ACCESS = const(0x1800)
UUID_GENERIC_ATTRIBUTE = const(0x1801)

# Characteristic UUIDs
UUID_DEVICE_NAME = const(0x2A00)
UUID_APPEARANCE = const(0x2A01)
UUID_PPCP = const(0x2A04) # Peripheral_Preferred_Connection_Parameters

UUID_SERVICE_CHANGED = const(0x2A05)


class GenericProfile(Profile):
	'''只包含蓝牙必须的两个服务，GenericAccess 和 GenericAttribute'''
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self):
		super().__init__()
		self.__make_profile()

	def __make_profile(self):
		self.add_services(
			GenericAccess().add_characteristics(
				DeviceName(),
				Appearance(),
				PPCP(),
			),
			GenericAttribute().add_characteristics(
				ServiceChanged(),
			),
		)


class GenericValues(object):
	def __init__(self):
		self.generic_access = self.GenericAccess()


	class GenericAccess(object):
		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]

		def __init__(self):
			self.__device_name = 'MP_HID'

			# (0x00f, 0x01)
			# category: Human Interface Device
			# subcategory: Keyboard
			self.__appearance = 961 # or (0x00f, 0x01)

			# (min, max, latency, timeout)
			# Minimum connection interval
			# Maximum connection interval
			# Slave Latency
			# Connection Supervision timeout multiplier
			# for min & max, 1 = 1.25ms
			self.__ppcp = [40, 80, 10, 300] # Peripheral_Preferred_Connection_Parameters


		# region Properties
		@property
		def device_name(self) -> bytes:
			return pack(f'<{len(self.__device_name)}s', self.__device_name.encode())

		@device_name.setter
		def device_name(self, value: str):
			self.__device_name = value if isinstance(value, str) else str(value)

		@property
		def appearance(self) -> bytes:
			return pack('<H', self.__appearance)

		@appearance.setter
		def appearance(self, value: int | tuple):
			if isinstance(value, tuple) and len(value) == 2 and all(isinstance(v, int) for v in value):
				self.__appearance = BLETools.make_appearance(*value)
			elif isinstance(value, int):
				self.__appearance = value

		@property
		def ppcp(self) -> bytes:
			return pack('<4H', *self.__ppcp)

		@ppcp.setter
		def ppcp(self, value: tuple | list):
			if isinstance(value, (tuple, list)) and len(value) == 4 and all(isinstance(v, int) for v in value):
				self.__ppcp = value
		# endregion


# region Services
class GenericAccess(Service):
	def __init__(self):
		super().__init__(UUID(UUID_GENERIC_ACCESS))

class GenericAttribute(Service):
	def __init__(self):
		super().__init__(UUID(UUID_GENERIC_ATTRIBUTE))
# endregion


# region Characteristics

# region GenericAccess's Characteristics
class DeviceName(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_DEVICE_NAME), Flag.READ_WRITE)

class Appearance(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_APPEARANCE), Flag.READ)

class PPCP(Characteristic): # PeripheralPreferredConnectionParameters
	def __init__(self):
		super().__init__(UUID(UUID_PPCP), Flag.READ)
# endregion


# region GenericAttribute's Characteristics
class ServiceChanged(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_SERVICE_CHANGED), Flag.INDICATE)
# endregion

# endregion
