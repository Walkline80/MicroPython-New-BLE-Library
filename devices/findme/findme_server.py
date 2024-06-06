"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import bluetooth
from ble import *
from profiles.findme import FindMeProfile


def printf(msg, *args, **kwargs):
	print(f'\033[1;37m[INFO]\033[0m {msg}', *args, **kwargs)


class FindMeServer(object):
	'''Find Me Server'''
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self,
			device_name: str = 'findme-server',
			alert_level_cb: function = None):
		self.__ble              = bluetooth.BLE()
		self.__alert_level_cb   = alert_level_cb
		self.__conn_handles     = set()
		self.__last_alert_level = 0

		self.__ble.config(gap_name=device_name)
		self.__ble.irq(self.__irq_callback)

		self.__ble.active(False)
		printf('Activating BLE...')
		self.__ble.active(True)
		printf(f'BLE Activated [{BLETools.decode_mac(self.__ble.config('mac')[1])}]')

		self.__ble.config(addr_mode=AddressMode.RPA, mtu=256)

		findme_profile = FindMeProfile()

		self.__register_services(findme_profile.get_services())

		adv_payload = BLETools.generate_advertising_payload(
			findme_profile.get_services_uuid(),
			appearance=512, # (0x008, 0x00)
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
				self.__handle_alert_level,
			),
		) = self.__ble.gatts_register_services(services)

		printf('Services Registered')

		if True:
			printf('- alert level:', self.__handle_alert_level)

	def __advertise(self, adv_payload: bytes = None, resp_payload: bytes = None, interval_us: int = 100000):
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

		elif event == IRQ.GATTS_WRITE:
			_, attr_handle = data

			if attr_handle == self.__handle_alert_level:
				self.__last_alert_level = int.from_bytes(
					bytes(self.__ble.gatts_read(self.__handle_alert_level)), 'little'
				)

				if self.__alert_level_cb:
					self.__alert_level_cb(self.__last_alert_level)

		elif event == IRQ.GATTC_INDICATE:
			conn_handle, value_handle, data = data
			printf(f'GATTC Indicate [Handle: {conn_handle}, Value_Handle: {value_handle}, Data: {bytes(data)}]')

		elif event == IRQ.CONNECTION_UPDATE:
			pass
		elif event == IRQ.GET_SECRET:
			return None
		elif event == IRQ.SET_SECRET:
			return False
		else:
			printf(f'Uncaught IRQ Event: {event}, Data: {data}')


	# region Properties
	@property
	def last_alert_level(self) -> int:
		return self.__last_alert_level
	# endregion
