"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import bluetooth
from struct import unpack
from ble import *
from profiles.alert import AlertNotificationProfile, AlertNotificationValues


def printf(msg, *args, **kwargs):
	print(f'\033[1;37m[INFO]\033[0m {msg}', *args, **kwargs)


class AlertNotificationServer(object):
	'''Alert Notification Server'''
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self,
			device_name: str = 'alert-server',
			control_point_cb: function = None):
		self.__ble              = bluetooth.BLE()
		self.__control_point_cb = control_point_cb
		self.__conn_handles     = set()

		self.__ble.config(gap_name=device_name)
		self.__ble.irq(self.__irq_callback)

		self.__ble.active(False)
		printf('Activating BLE...')
		self.__ble.active(True)
		printf(f'BLE Activated [{BLETools.decode_mac(self.__ble.config('mac')[1])}]')

		self.__ble.config(addr_mode=AddressMode.RPA, mtu=256)

		alert_profile = AlertNotificationProfile()

		self.__alert_values = AlertNotificationValues()

		self.__register_services(alert_profile.get_services())

		adv_payload = BLETools.generate_advertising_payload(
			alert_profile.get_services_uuid(),
			appearance=0, # (0x000, 0x00)
		)

		resp_payload = BLETools.generate_advertising_payload(
			name=device_name,
			for_resp=True
		)

		assert (len(adv_payload)  <= MAX_PAYLOAD_LENGTH) and\
			   (len(resp_payload) <= MAX_PAYLOAD_LENGTH),\
			   f'Advertising payload too long, more than {MAX_PAYLOAD_LENGTH} bytes'

		self.__advertise(adv_payload, resp_payload)

	def __register_services(self, services: list):
		(
			(
				self.__handle_supported_new_alert_category,
				self.__handle_new_alert,
				self.__handle_supported_unread_alert_category,
				self.__handle_unread_alert_status,
				self.__handle_alert_notification_control_point,
			),
		) = self.__ble.gatts_register_services(services)

		printf('Services Registered')

		if False:
			printf('- supported new alert category:',
					self.__handle_supported_new_alert_category)
			printf('- new alert:', self.__handle_new_alert)
			printf('- supproted unread alert category:',
					self.__handle_supported_unread_alert_category)
			printf('- unread alert status:',
					self.__handle_unread_alert_status)
			printf('- alert notification control point:',
					self.__handle_alert_notification_control_point)

	def __advertise(self, adv_payload: bytes = None,
				         resp_payload: bytes = None, interval_us: int = 100000):
		self.__ble.gap_advertise(None)
		self.__ble.gap_advertise(interval_us, adv_data=adv_payload, resp_data=resp_payload)

		printf('Advertising Payload...')

	def __irq_callback(self, event, data):
		if event == IRQ.CENTRAL_CONNECT:
			conn_handle, _, addr, = data

			self.__conn_handles.add(conn_handle)
			self.__ble.gap_advertise(None)

			printf(f'[{BLETools.decode_mac(addr)}] Connected [Handle: {conn_handle}]')

		elif event == IRQ.CENTRAL_DISCONNECT:
			conn_handle, _, addr, = data

			if conn_handle in self.__conn_handles:
				self.__conn_handles.remove(conn_handle)

			printf(f'[{BLETools.decode_mac(addr)}] Disconnected [Handle: {conn_handle}]')

			self.__advertise()

		elif event == IRQ.GATTS_READ_REQUEST:
			_, attr_handle = data

			if attr_handle == self.__handle_supported_new_alert_category:
				self.__ble.gatts_write(
					self.__handle_supported_new_alert_category,
					self.__alert_values.alert_notification_service.new_alert_category)
			elif attr_handle == self.__handle_supported_unread_alert_category:
				self.__ble.gatts_write(
					self.__handle_supported_unread_alert_category,
					self.__alert_values.alert_notification_service.unread_alert_category)

			return GATTSErrorCode.NO_ERROR

		elif event == IRQ.GATTS_WRITE:
			_, attr_handle = data

			if attr_handle == self.__handle_alert_notification_control_point:
				command, category = unpack(
					'<BB',self.__ble.gatts_read(self.__handle_alert_notification_control_point))

				if self.__control_point_cb:
					self.__control_point_cb(command, category)

		elif event == IRQ.CONNECTION_UPDATE:
			pass
		elif event == IRQ.GET_SECRET:
			return None
		elif event == IRQ.SET_SECRET:
			return False
		else:
			printf(f'Uncaught IRQ Event: {event}, Data: {data}')

	# region Class Methods
	def enable_new_alert(self, category: int):
		self.__alert_values.alert_notification_service.enable_category(category, True)

	def disable_new_alert(self, category: int):
		self.__alert_values.alert_notification_service.disable_category(category, True)

	def enable_unread_alert_status(self, category: int):
		self.__alert_values.alert_notification_service.enable_category(category, False)

	def disable_unread_alert_status(self, category: int):
		self.__alert_values.alert_notification_service.disable_category(category, False)

	def send_new_alert(self, category_id: int, number: int, text: str):
		if self.__alert_values.alert_notification_service.make_new_alert(category_id, number, text):
			self.__ble.gatts_write(
				self.__handle_new_alert,
				self.__alert_values.alert_notification_service.new_alert)

			for conn_handle in self.__conn_handles:
				self.__ble.gatts_notify(conn_handle, self.__handle_new_alert)

	def send_unread_alert_status(self, category_id: int, count: int):
		if self.__alert_values.alert_notification_service.make_unread_alert_status(category_id, count):
			self.__ble.gatts_write(
				self.__handle_unread_alert_status,
				self.__alert_values.alert_notification_service.unread_alert_status)

			for conn_handle in self.__conn_handles:
				self.__ble.gatts_notify(conn_handle, self.__handle_unread_alert_status)
	# endregion
