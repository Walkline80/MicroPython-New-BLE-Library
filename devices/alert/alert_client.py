"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import bluetooth
from struct import unpack
from ble import BLETools, ADVType, IRQ
from profiles.alert import AlertNotificationValues as Values


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

		self.__handle_supported_new_alert_category     = None
		self.__handle_new_alert                        = None
		self.__handle_supported_unread_alert_category  = None
		self.__handle_unread_alert_status              = None
		self.__handle_alert_notification_control_point = None

	@property
	def name(self) -> str:
		'''get device name or mac address'''
		return BLETools.decode_name(self.__adv_data) or BLETools.decode_mac(self.addr)


class AlertNotificationClient(object):
	'''Alert Notification Client'''
	def __init__(self,
			device_name: str = 'alert-client',
			target_name: str = 'alert-server',
			found_target_cb: function = None,
			new_alert_cb: function = None,
			unread_alert_status_cb: function = None,
			request_alert_category_cb: function = None):
		self.__ble          = bluetooth.BLE()
		self.__target       = None
		self.__target_name  = target_name
		self.__alert_values = Values()

		self.__supported_new_alert_category    = None
		self.__supported_unread_alert_category = None

		self.__found_target_cb           = found_target_cb
		self.__new_alert_cb              = new_alert_cb
		self.__unread_alert_status_cb    = unread_alert_status_cb
		self.__request_alert_category_cb = request_alert_category_cb

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
			printf(f'Scan Completed, Alert Notification Server{"" if self.__target else " not"} found')

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

			if uuid == bluetooth.UUID(Values.UUIDS.ALERT_NOTIFICATION_SERVICE):
				self.__target.start_handle = start_handle
				self.__target.end_handle   = end_handle

		elif event == IRQ.GATTC_SERVICE_DONE:
			conn_handle, _ = data

			if self.__target.start_handle and self.__target.end_handle:
				self.__ble.gattc_discover_characteristics(conn_handle,
					self.__target.start_handle, self.__target.end_handle)

		elif event == IRQ.GATTC_CHARACTERISTIC_RESULT:
			_, _, value_handle, _, uuid = data

			if   uuid == bluetooth.UUID(Values.UUIDS.SUPPORTED_NEW_ALERT_CATEGORY):
				self.__target.__handle_supported_new_alert_category = value_handle
			elif uuid == bluetooth.UUID(Values.UUIDS.NEW_ALERT):
				self.__target.__handle_new_alert = value_handle
			elif uuid == bluetooth.UUID(Values.UUIDS.SUPPORTED_UNREAD_ALERT_CATEGORY):
				self.__target.__handle_supported_unread_alert_category = value_handle
			elif uuid == bluetooth.UUID(Values.UUIDS.UNREAD_ALERT_STATUS):
				self.__target.__handle_unread_alert_status = value_handle
			elif uuid == bluetooth.UUID(Values.UUIDS.ALERT_NOTIFICATION_CONTROL_POINT):
				self.__target.__handle_alert_notification_control_point = value_handle

		elif event == IRQ.GATTC_CHARACTERISTIC_DONE:
			if self.__target.__handle_supported_new_alert_category and\
			   self.__target.__handle_new_alert and\
			   self.__target.__handle_supported_unread_alert_category and\
			   self.__target.__handle_unread_alert_status and\
			   self.__target.__handle_alert_notification_control_point:
				self.request_alert_category()

				if self.__found_target_cb:
					self.__found_target_cb()

		elif event == IRQ.GATTC_READ_RESULT:
			_, value_handle, char_data = data

			if value_handle == self.__target.__handle_supported_new_alert_category:
				self.__supported_new_alert_category = [int(c) for c in f'{unpack('<H', char_data)[0]:0>10b}']
				self.__supported_new_alert_category.reverse()
			elif value_handle == self.__target.__handle_supported_unread_alert_category:
				self.__supported_unread_alert_category = [int(c) for c in f'{unpack('<H', char_data)[0]:0>10b}']
				self.__supported_unread_alert_category.reverse()

		elif event == IRQ.GATTC_READ_DONE:
			if self.__supported_new_alert_category and self.__supported_unread_alert_category:
				if self.__request_alert_category_cb:
					self.__request_alert_category_cb(
						self.__supported_new_alert_category, self.__supported_unread_alert_category)

		elif event == IRQ.GATTC_NOTIFY:
			_, value_handle, notify_data = data

			if value_handle == self.__target.__handle_new_alert:
				if self.__new_alert_cb:
					self.__new_alert_cb(
						*unpack('<BB', notify_data[:2]), bytes(notify_data[2:]).decode())
			elif value_handle == self.__target.__handle_unread_alert_status:
				if self.__unread_alert_status_cb:
					self.__unread_alert_status_cb(*unpack('<BB', notify_data))

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
			printf(f'Uncaught IRQ Event: {event}, Data: {data}')

	def __check(self, data):
		_, _, adv_type, rssi, adv_data = data

		return (BLETools.decode_name(adv_data) == self.__target_name or\
			   bluetooth.UUID(Values.UUIDS.ALERT_NOTIFICATION_SERVICE) in BLETools.decode_services(adv_data)) and\
			   adv_type in (ADVType.IND, ADVType.DIRECT_IND, ADVType.SCAN_RSP) and rssi >= -80


	# region Class Methods
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

	def request_alert_category(self):
		if self.__target is None:
			return

		self.__ble.gattc_read(self.__target.conn_handle, self.__target.__handle_supported_new_alert_category)
		self.__ble.gattc_read(self.__target.conn_handle, self.__target.__handle_supported_unread_alert_category)

		self.__supported_new_alert_category    = None
		self.__supported_unread_alert_category = None

	def send_command(self, category_id: int, command: int):
		if self.__target is None:
			return

		if self.__alert_values.alert_notification_service.make_control_point(category_id, command):
			self.__ble.gattc_write(self.__target.conn_handle,
				self.__target.__handle_alert_notification_control_point,
				self.__alert_values.alert_notification_service.control_point)
	# endregion


	# region Class Properties
	@property
	def new_alert_category(self) -> list:
		'''服务器端支持的 New Alert 目录列表'''
		return self.__supported_new_alert_category

	@property
	def unread_alert_category(self) -> list:
		'''服务器端支持的 Unread Alert 目录列表'''
		return self.__supported_unread_alert_category
	# endregion
