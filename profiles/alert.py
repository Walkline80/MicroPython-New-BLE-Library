"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from micropython import const
from struct import pack
from bluetooth import UUID
from ble import *


# Profile
# https://www.bluetooth.com/specifications/specs/alert-notification-profile-1-0/

# Service
# https://www.bluetooth.com/specifications/specs/alert-notification-service-1-0/


class AlertNotificationProfile(Profile):
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self):
		super().__init__()
		self.__make_profile()

	def __make_profile(self):
		self.add_services(
			AlertNotificationService().add_characteristics(
				SupportedNewAlertCategory(),
				NewAlert(),
				SupportedUnreadAlertCategory(),
				UnreadAlertStatus(),
				AlertNotificationControlPoint(),
			),
		)


class AlertNotificationValues(object):
	'''生成 Alert Notification 配置文件相关服务相关特征值字节串'''
	def __init__(self):
		self.alert_notification_service = self.AlertNotificationService()


	class UUIDS(object):
		# Service
		ALERT_NOTIFICATION_SERVICE = const(0x1811)

		# Characteristic
		SUPPORTED_NEW_ALERT_CATEGORY     = const(0x2A47)
		NEW_ALERT                        = const(0x2A46)
		SUPPORTED_UNREAD_ALERT_CATEGORY  = const(0x2A48)
		UNREAD_ALERT_STATUS              = const(0x2A45)
		ALERT_NOTIFICATION_CONTROL_POINT = const(0x2A44)


	class Consts(object):
		ERROR_CODE = 0xA0 # Command not supported

		class AlertCategory(object):
			SIMPLE_ALERT           = 0
			EMAIL                  = 1
			NEWS                   = 2
			CALL                   = 3
			MISSEDCALL             = 4
			SMS_MMS                = 5
			VOICEMAIL              = 6
			SCHEDULE               = 7
			HIGH_PRIORITIZED_ALERT = 8
			INSTANT_MESSAGE        = 9
			ALL                    = 0b1111111111
			CATEGORIES = {
				SIMPLE_ALERT,
				EMAIL,
				NEWS,
				CALL,
				MISSEDCALL,
				SMS_MMS,
				VOICEMAIL,
				SCHEDULE,
				HIGH_PRIORITIZED_ALERT,
				INSTANT_MESSAGE,
			}
			CATEGORIES_MAP = {
				SIMPLE_ALERT          : 'Simple Alert',
				EMAIL                 : 'Email',
				NEWS                  : 'News',
				CALL                  : 'Call',
				MISSEDCALL            : 'Missed Call',
				SMS_MMS               : 'SMS/MMS',
				VOICEMAIL             : 'Voice Mail',
				SCHEDULE              : 'Schedule',
				HIGH_PRIORITIZED_ALERT: 'High Prioritized Alert',
				INSTANT_MESSAGE       : 'Instant Message',
			}

		class AlertCommand(object):
			ENABLE_NEW_ALERT                 = 0
			ENABLE_UNREAD_STATUS             = 1
			DISABLE_NEW_ALERT                = 2
			DISABLE_UNREAD_STATUS            = 3
			NOTIFY_NEW_ALERT_IMMEDIATELY     = 4
			NOTIFY_UNREAD_STATUS_IMMEDIATELY = 5
			COMMANDS = {
				ENABLE_NEW_ALERT,
				ENABLE_UNREAD_STATUS,
				DISABLE_NEW_ALERT,
				DISABLE_UNREAD_STATUS,
				NOTIFY_NEW_ALERT_IMMEDIATELY,
				NOTIFY_UNREAD_STATUS_IMMEDIATELY,
			}
			COMMANDS_MAP = {
				ENABLE_NEW_ALERT:                 'Enable New Incoming Alert Notification',                
				ENABLE_UNREAD_STATUS:             'Enable Unread Category Status Notification',
				DISABLE_NEW_ALERT:                'Disable New Incoming Alert Notification',
				DISABLE_UNREAD_STATUS:            'Disable Unread Category Status Notification',
				NOTIFY_NEW_ALERT_IMMEDIATELY:     'Notify New Incoming Alert Immediately',
				NOTIFY_UNREAD_STATUS_IMMEDIATELY: 'Notify Unread Category Status Immediately',
			}


	class AlertNotificationService(object):
		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]

		def __init__(self):
			self.__new_alert_category    = 0
			self.__unread_alert_category = 0

			self.__alert_id     = None
			self.__alert_number = 0 # from 0 to 255
			self.__alert_text   = '' # length 0–18

			self.__unread_id    = None
			self.__unread_count = 0 # from 0 to 255

			self.__control_id      = None
			self.__control_command = None

		def get_category_status(self, category, for_new_alert: bool = True) -> int:
			status = 0

			if category in AlertNotificationValues.Consts.AlertCategory.CATEGORIES:
				if for_new_alert:
					status = (self.__new_alert_category >> category) & 1
				else:
					status = (self.__unread_alert_category >> category) & 1

			return status

		def enable_category(self, category: int, for_new_alert: bool = True):
			if category in AlertNotificationValues.Consts.AlertCategory.CATEGORIES:
				if for_new_alert:
					self.__new_alert_category |= 1 << category
				else:
					self.__unread_alert_category |= 1 << category

		def disable_category(self, category: int, for_new_alert: bool = True):
			if category in AlertNotificationValues.Consts.AlertCategory.CATEGORIES:
				if for_new_alert:
					self.__new_alert_category &= ~(1 << category)
				else:
					self.__unread_alert_category &= ~(1 << category)

		def make_new_alert(self, category_id: int, number: int, text: str = '') -> bool:
			if category_id not in AlertNotificationValues.Consts.AlertCategory.CATEGORIES:
				return

			self.__alert_id     = category_id
			self.__alert_number = number if 0 <= number <= 255 else 255
			self.__alert_text   = text[:18]

			return True

		def make_unread_alert_status(self, category_id: int, count: int) -> bool:
			if category_id not in AlertNotificationValues.Consts.AlertCategory.CATEGORIES:
				return

			self.__unread_id    = category_id
			self.__unread_count = count if 0 <= count <= 255 else 255

			return True

		def make_control_point(self, category_id: int, command: int) -> bool:
			if category_id not in AlertNotificationValues.Consts.AlertCategory.CATEGORIES or\
			   command not in AlertNotificationValues.Consts.AlertCommand.COMMANDS:
				return

			self.__control_id      = category_id
			self.__control_command = command

			return True

		# region Properties
		@property
		def new_alert_category(self) -> bytes:
			return pack('<H', self.__new_alert_category)

		@new_alert_category.setter
		def new_alert_category(self, value: int):
			if value <= AlertNotificationValues.Consts.AlertCategory.ALL:
				self.__new_alert_category = value

		@property
		def unread_alert_category(self) -> bytes:
			return pack('<H', self.__unread_alert_category)

		@unread_alert_category.setter
		def unread_alert_category(self, value: int):
			if value <= AlertNotificationValues.Consts.AlertCategory.ALL:
				self.__unread_alert_category = value

		@property
		def new_alert(self) -> bytes:
			return pack(f'<BB{len(self.__alert_text)}s',
			   			self.__alert_id, self.__alert_number, self.__alert_text)

		@property
		def unread_alert_status(self) -> bytes:
			return pack(f'<BB', self.__unread_id, self.__unread_count)

		@property
		def control_point(self) -> bytes:
			return pack(f'<BB', self.__control_command, self.__control_id)
		# endregion


# region Service
class  AlertNotificationService(Service):
	def __init__(self):
		super().__init__(UUID(AlertNotificationValues.UUIDS.ALERT_NOTIFICATION_SERVICE))
# endregion


# region Characteristics
class SupportedNewAlertCategory(Characteristic):
	def __init__(self):
		super().__init__(UUID(AlertNotificationValues.UUIDS.SUPPORTED_NEW_ALERT_CATEGORY), Flag.READ)

class NewAlert(Characteristic):
	def __init__(self):
		super().__init__(UUID(AlertNotificationValues.UUIDS.NEW_ALERT), Flag.NOTIFY)

class SupportedUnreadAlertCategory(Characteristic):
	def __init__(self):
		super().__init__(UUID(AlertNotificationValues.UUIDS.SUPPORTED_UNREAD_ALERT_CATEGORY), Flag.READ)

class UnreadAlertStatus(Characteristic):
	def __init__(self):
		super().__init__(UUID(AlertNotificationValues.UUIDS.UNREAD_ALERT_STATUS), Flag.NOTIFY)

class AlertNotificationControlPoint(Characteristic):
	def __init__(self):
		super().__init__(UUID(AlertNotificationValues.UUIDS.ALERT_NOTIFICATION_CONTROL_POINT), Flag.WRITE)
# endregion
