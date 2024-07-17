"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-batch-ble-config-device
"""
import time
import bluetooth
from ble.tools import BLETools, printf
from testing.utils.utilities import Utilities

import esp
esp.osdebug(None) # 注释此行可显示详细调试信息


MODE_SERVER = 0
MODE_CLIENT = 1

TARGET_DEVICE = 'ble-config'

SSID_PREFIX		= 'ssid_'
PASSWORD_PREFIX	= 'pswd_'

NORDIC_UART_UUID = bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
NORDIC_RX_UUID   = bluetooth.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')
NORDIC_TX_UUID   = bluetooth.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')

handle_rx = handle_tx = None

def run_bleconfig_server():
	from devices.scanner.scanner import Scanner

	def central_connected_cb(device):
		global handle_rx, handle_tx
		printf('Sending data')

		scanner.write(device, handle_rx, f'{SSID_PREFIX}{ssid}'.encode())
		scanner.write(device, handle_rx, f'{PASSWORD_PREFIX}{password}'.encode())

		printf('BLE config completed')
		scanner.disconnect(device)

	def scan_done_cb(devices:list):
		printf(f'Scan completed, {len(devices)} device(s) found')

		for device in devices:
			print(f'- [{device.name}] ({BLETools.decode_mac(device.addr)}), Connectable: {device.connectable}')

	def discover_done_cb(devices:list):
		global handle_rx, handle_tx

		for device in devices:
			if not device.connectable:
				continue

			service_uart = device.profile['services'].get(str(NORDIC_UART_UUID))

			if service_uart:
				characteristic_rx = service_uart['characteristics'].get(str(NORDIC_RX_UUID))
				characteristic_tx = service_uart['characteristics'].get(str(NORDIC_TX_UUID))

				handle_rx = characteristic_rx.get('value_handle')
				handle_tx = characteristic_tx.get('value_handle')

				if handle_rx and handle_tx:
					scanner.mode = Scanner.MODE_CENTRAL
					scanner.connect(device)

	ssid     = 'ssid_for_testing'
	password = 'password'

	scanner = Scanner(
		scan_done_cb=scan_done_cb,
		central_connected_cb=central_connected_cb,
		discover_done_cb=discover_done_cb
	)

	scanner.set_targets(TARGET_DEVICE)
	scanner.mode = Scanner.MODE_SCANNER
	scanner.scan(seconds=5)

def run_bleconfig_client():
	from devices.uart.bleconfig import BLEConfig

	def rx_received_cb(data: bytes):
		printf(f'Received Data: {data}')

	bleconfig = BLEConfig(device_name=TARGET_DEVICE, rx_received_cb=rx_received_cb)

	while not bleconfig.success():
		time.sleep_ms(100)

	printf(f'ssid: {bleconfig.ssid}, password: {bleconfig.password}')

def run_test():
	options = [
		'Server mode, broadcasts ssid & password to clients',
		'Client mode, receive ssid & password from server',
	]

	# 运行模式二选一
	mode = Utilities.choose_an_option('BLE Config Device Mode', options)
	# mode = MODE_SERVER
	# mode = MODE_CLIENT

	if mode is not None:
		if mode == MODE_SERVER:
			run_bleconfig_server()
		else:
			run_bleconfig_client()


if __name__ == '__main__':
	run_test()
