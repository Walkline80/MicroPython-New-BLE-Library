"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from micropython import const
from struct import pack
from bluetooth import UUID
from time import localtime
from ble import *


# Profile
# https://www.bluetooth.com/specifications/specs/time-profile-1-0/

# Service
# https://www.bluetooth.com/specifications/specs/current-time-service-1-1/


class TimeProfile(Profile):
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


class TimeValues(object):
	'''生成 Time 配置文件相关服务特征值字节串'''
	def __init__(self):
		self.current_time_service = self.CurrentTimeService()


	class UUIDS(object):
		# Service
		CURRENT_TIME_SERVICE = const(0x1805)

		# Characteristics
		CURRENT_TIME = const(0x2A2B)
		LOCAL_TIME_INFORMATION = const(0x2A0F)


	class Consts(object):
		class AdjustReason(object):
			MANUAL   = 0b0001
			EXTERNAL = 0b0010
			TIMEZONE = 0b0100
			DST      = 0b1000
			REASONS = {
				MANUAL,
				EXTERNAL,
				TIMEZONE,
				DST,
			}
			REASONS_MAP ={
				MANUAL  : 'Manual Adjustment',
				EXTERNAL: 'External Adjustment',
				TIMEZONE: 'Time Zone Adjustment',
				DST     : 'Daylight Saving Time Adjustment',
			}

		class DSTOffset(object):
			STANDARD       = 0
			HALF_DAYLIGHT  = 2 # (+ 0.5h)
			DAYLIGHT       = 4 # (+ 1h)
			DOUBLEDAYLIGHT = 8 # (+ 2h)
			OFFSETS = {
				STANDARD,
				HALF_DAYLIGHT,
				DAYLIGHT,
				DOUBLEDAYLIGHT,
			}
			OFFSETS_MAP = {
				STANDARD      : 'Standard Time',
				HALF_DAYLIGHT : 'Half Daylight Saving Time',
				DAYLIGHT      : 'Daylight Saving Time',
				DOUBLEDAYLIGHT: 'Double Daylight Saving Time',
			}


	class CurrentTimeService(object):
		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]

		def __init__(self):
			# current_time related
			self.__adjust_reason = TimeValues.Consts.AdjustReason.MANUAL
			self.__fractions256  = 0

			# local_time_information related
			self.__time_zone  = 8.0 # for UTC+8:00, -4.50 for UTC-4:30
			self.__dst_offset = TimeValues.Consts.DSTOffset.STANDARD


		# region Properties
		@property
		def adjust_reason(self) -> int:
			return self.__adjust_reason

		@adjust_reason.setter
		def adjust_reason(self, value: int):
			if isinstance(value, int) and value in TimeValues.Consts.AdjustReason.REASONS:
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
		def time_zone(self, value: float):
			if isinstance(value, float) and -12.00 <= value <= 14.00 and value % 0.25 == 0.0:
				self.__time_zone = value

		@property
		def dst_offset(self) -> int:
			return self.__dst_offset

		@dst_offset.setter
		def dst_offset(self, value: int):
			if isinstance(value, int) and value in TimeValues.Consts.DSTOffset.OFFSETS:
				self.__dst_offset = value

		@property
		def local_time_information(self) -> bytes:
			return pack('<bB', int(self.__time_zone * 4), self.__dst_offset)
		# endregion


# region Service
class CurrentTimeService(Service):
	def __init__(self):
		super().__init__(UUID(TimeValues.UUIDS.CURRENT_TIME_SERVICE))
# endregion


# region Characteristics
class CurrentTime(Characteristic):
	def __init__(self):
		super().__init__(UUID(TimeValues.UUIDS.CURRENT_TIME), Flag.READ_NOTIFY)

class LocalTimeInformation(Characteristic):
	def __init__(self):
		super().__init__(UUID(TimeValues.UUIDS.LOCAL_TIME_INFORMATION), Flag.READ)
# endregion
