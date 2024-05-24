"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from micropython import const
from struct import pack
from bluetooth import UUID
from time import localtime

try:
	from ble import *
except ImportError:
	from ..ble import *


UUID_CURRENT_TIME_SERVICE = const(0x1805)
UUID_CURRENT_TIME = const(0x2A2B)
UUID_LOCAL_TIME_INFORMATION = const(0x2A0F)


class CTSProfile(Profile):
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self):
		super().__init__()
		self.__make_profile()

	def __make_profile(self):
		self.add_services(
			CurrentTimeService().add_characteristics(
				CurrentTime(),
				LocalTimeInformation(),
			),
		)


class CTSValues(object):
	'''生成 CTS 服务相关特征值字节串'''
	def __init__(self):
		self.current_time_service = self.CurrentTimeService()

	class CurrentTimeService(object):
		ADJUST_REASON_MANUAL   = 0b0001
		ADJUST_REASON_EXTERNAL = 0b0010
		ADJUST_REASON_TIMEZONE = 0b0100
		ADJUST_REASON_DST      = 0b1000
		ADJUST_REASONS = (
			ADJUST_REASON_MANUAL,
			ADJUST_REASON_EXTERNAL,
			ADJUST_REASON_TIMEZONE,
			ADJUST_REASON_DST,
		)

		DST_OFFSET_STANDARD       = 0
		DST_OFFSET_HALF_DAYLIGHT  = 2 # (+ 0.5h)
		DST_OFFSET_DAYLIGHT       = 4 # (+ 1h)
		DST_OFFSET_DOUBLEDAYLIGHT = 8 # (+ 2h)
		DST_OFFSETS = (
			DST_OFFSET_STANDARD,
			DST_OFFSET_HALF_DAYLIGHT,
			DST_OFFSET_DAYLIGHT,
			DST_OFFSET_DOUBLEDAYLIGHT,
		)

		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]

		def __init__(self):
			# current_time related
			self.__adjust_reason = self.ADJUST_REASON_MANUAL
			self.__fractions256  = 0

			# local_time_information related
			self.__time_zone  = 8 * 4 # UTC+8
			self.__dst_offset = self.DST_OFFSET_STANDARD


		# region Properties
		@property
		def adjust_reason(self) -> int:
			return self.__adjust_reason

		@adjust_reason.setter
		def adjust_reason(self, value: int):
			if isinstance(value, int) and value in self.ADJUST_REASONS:
				self.__adjust_reason = value

		@property
		def fractions256(self) -> int:
			return self.__fractions256

		@fractions256.setter
		def fractions256(self, value: int):
			if isinstance(value, int) and 0 <= value <= 1000:
				self.__fractions256 = int(value / 1000 * 255)

		@property
		def current_time(self) -> bytes:
			datetime = list(localtime())
			datetime[6] += 1 # week of day
			return pack('<H8B', *datetime[:7], self.__fractions256, self.__adjust_reason)

		@property
		def time_zone(self) -> int:
			return self.__time_zone

		@time_zone.setter
		def time_zone(self, value: int):
			if isinstance(value, int) and -48 <= value <= 56:
				self.__time_zone = value

		@property
		def dst_offset(self) -> int:
			return self.__dst_offset

		@dst_offset.setter
		def dst_offset(self, value: int):
			if isinstance(value, int) and value in self.DST_OFFSETS:
				self.__dst_offset = value

		@property
		def local_time_information(self) -> bytes:
			return pack('<bB', self.__time_zone, self.__dst_offset)


# region Service
class CurrentTimeService(Service):
	def __init__(self):
		super().__init__(UUID(UUID_CURRENT_TIME_SERVICE))
# endregion


# region Characteristics
class CurrentTime(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_CURRENT_TIME), Flag.READ_NOTIFY)

class LocalTimeInformation(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_LOCAL_TIME_INFORMATION), Flag.READ)
# endregion
