"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import bluetooth
from ble import *
from profiles.uart import UARTProfile


def printf(msg, *args, **kwargs):
	print(f'\033[1;37m[INFO]\033[0m {msg}', *args, **kwargs)


class BLEUART(object):
	'''主、从机数据交换'''
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self, device_name: str = 'ble-uart', rx_received_cb: function = None):
		self.__ble            = bluetooth.BLE()
		self.__rx_received_cb = rx_received_cb
		self.__conn_handles   = set()

		appearance = 384 # (0x006, 0x00)

		self.__write    = self.__ble.gatts_write
		self.__read     = self.__ble.gatts_read
		self.__notify   = self.__ble.gatts_notify
		self.__indicate = self.__ble.gatts_indicate

		self.__ble.config(gap_name=device_name)
		self.__ble.irq(self.__irq_callback)

		self.__ble.active(False)
		printf('Activating BLE...')
		self.__ble.active(True)
		printf(f'BLE Activated [{BLETools.decode_mac(self.__ble.config('mac')[1])}]')

		self.__ble.config(addr_mode=AddressMode.RPA, mtu=256)

		uart_profile = UARTProfile()

		self.__register_services(uart_profile.get_services())

		adv_payload = BLETools.generate_advertising_payload(
			uart_profile.get_services_uuid(),
			appearance=appearance
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
				self.__handle_rx,
				self.__handle_tx,
			),
		) = self.__ble.gatts_register_services(services)

		printf('Services Registered')

		if False:
			printf('- rx:', self.__handle_rx)
			printf('- tx:', self.__handle_tx)

	def __advertise(self, adv_payload: bytes = None, resp_payload: bytes = None, interval_us: int = 100000):
		self.__ble.gap_advertise(None)
		self.__ble.gap_advertise(interval_us, adv_data=adv_payload, resp_data=resp_payload)

		printf('Advertising Payload...')

	def __irq_callback(self, event, data):
		if event == IRQ.CENTRAL_CONNECT:
			conn_handle, _, addr, = data # _: addr_type

			self.__conn_handles.add(conn_handle)
			self.__ble.gap_advertise(None)

			printf(f'[{BLETools.decode_mac(addr)}] Connected [Handle: {conn_handle}]')
		elif event == IRQ.CENTRAL_DISCONNECT:
			conn_handle, _, addr, = data # _: addr_type

			if conn_handle in self.__conn_handles:
				self.__conn_handles.remove(conn_handle)

			printf(f'[{BLETools.decode_mac(addr)}] Disconnected [Handle: {conn_handle}]')

			self.__advertise()
		elif event == IRQ.GATTS_WRITE:
			conn_handle, attr_handle = data

			# printf(f'GATTS Write [Handle: {conn_handle}, Attr_Handle: {attr_handle}]')

			if attr_handle == self.__handle_rx:
				if self.__rx_received_cb:
					self.__rx_received_cb(bytes(self.__read(self.__handle_rx)))
		elif event == IRQ.CONNECTION_UPDATE:
			conn_handle, interval, latency, supervision_timeout, status = data

			printf(f'Connection Update [Handle: {conn_handle}, Interval: {interval}, Latency: {latency}, Supervision_Timeout: {supervision_timeout}, Status: {status}]')
		elif event == IRQ.GATTC_INDICATE:
			conn_handle, value_handle, data = data

			printf(f'GATTC Indicate [Handle: {conn_handle}, Value_Handle: {value_handle}, Data: {bytes(data)}]')
		elif event == IRQ.SET_SECRET:
			return False
		elif event == IRQ.GET_SECRET:
			return None
		else:
			printf(f'Uncaught IRQ Event: {event}, Data: {data}')

	def send(self, data: bytes):
		'''将数据写入本地缓存，并推送到中心设备'''
		if self.__conn_handles is None:
			return

		self.__write(self.__handle_tx, data)

		for conn_handle in self.__conn_handles:
			self.__notify(conn_handle, self.__handle_tx, data)
