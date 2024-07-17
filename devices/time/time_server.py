"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import bluetooth
from ble import *
from profiles.time import TimeProfile, TimeValues


class TimeServer(object):
	'''Time Server'''
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self, device_name: str = 'time-server'):
		self.__ble          = bluetooth.BLE()
		self.__conn_handles = set()

		self.__ble.config(gap_name=device_name)
		self.__ble.irq(self.__irq_callback)

		self.__ble.active(False)
		printf('Activating BLE...')
		self.__ble.active(True)
		printf(f'BLE Activated [{BLETools.decode_mac(self.__ble.config('mac')[1])}]')

		self.__ble.config(addr_mode=AddressMode.RPA, mtu=256)

		time_profile = TimeProfile()

		self.__time_values = TimeValues()

		self.__register_services(time_profile.get_services())
		self.__setup_time_values()

		adv_payload = BLETools.generate_advertising_payload(
			time_profile.get_services_uuid(),
			appearance=256 # (0x004, 0x00)
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
				self.__handle_current_time,
				self.__handle_local_time_information,
			),
		) = self.__ble.gatts_register_services(services)

		printf('Services Registered')

		if False:
			printf('- current time:', self.__handle_current_time)
			printf('- local time information:', self.__handle_local_time_information)

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

		elif event == IRQ.GATTS_READ_REQUEST:
			_, attr_handle = data

			if attr_handle == self.__handle_current_time:
				self.__time_values.current_time_service.fractions256 = 0
				self.__ble.gatts_write(attr_handle,
					self.__time_values.current_time_service.current_time)
			elif attr_handle == self.__handle_local_time_information:
				self.__ble.gatts_write(attr_handle,
					self.__time_values.current_time_service.local_time_information)

			return GATTSErrorCode.NO_ERROR

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

	def __setup_time_values(self):
		self.__time_values.current_time_service.adjust_reason = self.__time_values.Consts.AdjustReason.MANUAL
		self.__time_values.current_time_service.fractions256  = 0
		self.__time_values.current_time_service.time_zone     = 8.0 # UTC+8:00
		self.__time_values.current_time_service.dst_offset    = self.__time_values.Consts.DSTOffset.STANDARD

		self.__ble.gatts_write(self.__handle_current_time,
			self.__time_values.current_time_service.current_time)
		self.__ble.gatts_write(self.__handle_local_time_information,
			self.__time_values.current_time_service.local_time_information)


	# region Properties
	@property
	def adjust_reason(self) -> int:
		return self.__time_values.current_time_service.adjust_reason

	@adjust_reason.setter
	def adjust_reason(self, value: int):
		self.__time_values.current_time_service.adjust_reason = value

	@property
	def fractions256(self) -> int:
		return self.__time_values.current_time_service.fractions256

	@fractions256.setter
	def fractions256(self, value: int):
		self.__time_values.current_time_service.fractions256 = value

	@property
	def time_zone(self) -> int:
		return self.__time_values.current_time_service.time_zone

	@time_zone.setter
	def time_zone(self, value: int):
		self.__time_values.current_time_service.time_zone = value

	@property
	def dst_offset(self) -> int:
		return self.__time_values.current_time_service.dst_offset

	@dst_offset.setter
	def dst_offset(self, value: int):
		self.__time_values.current_time_service.dst_offset = value
	# endregion
