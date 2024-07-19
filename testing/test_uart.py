"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import time
from testing.utils.utilities import Utilities


MODE_BLE_UART   = 0
MODE_BLE_CONFIG = 1

def run_bleuart_test():
	from devices.uart.bleuart import BLEUART

	def rx_received_cb(data: bytes):
		echo = bytes(reversed(data))
		print(f'received data: {data}, sending back: {echo}')
		bleuart.write(echo)

	bleuart = BLEUART(rx_received_cb=rx_received_cb)

def run_bleconfig_test():
	from devices.uart.bleconfig import BLEConfig

	def rx_received_cb(data: bytes):
		print(f'received data: {data}')

	bleconfig = BLEConfig(rx_received_cb=rx_received_cb)

	while not bleconfig.success():
		time.sleep(0.1)

	print(f'ssid: {bleconfig.ssid}, password: {bleconfig.password}')


if __name__ == '__main__':
	options = [
		'BLE UART,   details: https://gitee.com/walkline/esp32-ble-uart',
		'BLE Config, details: https://gitee.com/walkline/micropython_ble_config',
	]

	mode = Utilities.choose_an_option('UART Test Mode', options)

	if mode is not None:
		if mode == MODE_BLE_UART:
			run_bleuart_test()
		else:
			run_bleconfig_test()
