"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from micropython import const
from struct import pack
from bluetooth import UUID
from ble import *


# Profile
# https://www.bluetooth.com/specifications/specs/find-me-profile-1-0/

# Service
# https://www.bluetooth.com/specifications/specs/immediate-alert-service-1-0/


class FindMeProfile(Profile):
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self):
		super().__init__()
		self.__make_profile()

	def __make_profile(self):
		self.add_services(
			ImmediateAlertService().add_characteristics(
				AlertLevel(),
			)
		)


class FindMeValues(object):
	'''生成 Find Me 配置文件相关服务相关特征值字节串'''
	def __init__(self):
		self.immediate_alert_service = self.ImmediateAlertService()


	class UUIDS(object):
		# Service
		IMMEDIATE_ALERT_SERVICE = const(0x1802)

		# Characteristic
		ALERT_LEVEL = const(0x2A06)


	class Consts(object):
		class AlertLevel(object):
			NO_ALERT   = 0x00
			MILD_ALERT = 0x01
			HIGH_ALERT = 0x02
			LEVELS = {
				NO_ALERT,
				MILD_ALERT,
				HIGH_ALERT,
			}
			LEVELS_MAP = {
				NO_ALERT  : 'No Alert',
				MILD_ALERT: 'Mild Alert',
				HIGH_ALERT: 'High Alert',
			}


	class ImmediateAlertService(object):
		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]

		def __init__(self):
			self.__alert_level = FindMeValues.Consts.AlertLevel.NO_ALERT


		# region Properties
		@property
		def alert_level(self) -> bytes:
			return pack('<B', self.__alert_level)

		@alert_level.setter
		def alert_level(self, value: int | bytes):
			if isinstance(value, bytes):
				value = int.from_bytes(value, 'little')

			if isinstance(value, int) and value in FindMeValues.Consts.AlertLevel.LEVELS:
				self.__alert_level = value
		# endregion


# region Service
class  ImmediateAlertService(Service):
	def __init__(self):
		super().__init__(UUID(FindMeValues.UUIDS.IMMEDIATE_ALERT_SERVICE))
# endregion


# region Characteristic
class AlertLevel(Characteristic):
	def __init__(self):
		super().__init__(UUID(FindMeValues.UUIDS.ALERT_LEVEL), Flag.WRITE_NO_RESPONSE)
# endregion
