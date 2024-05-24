"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import time


MODE_UART      = 0
MODE_BLECONFIG = 1


def run_bleuart_test():
	try:
		from devices.uart.bleuart import BLEUART
	except ImportError:
		from ..devices.uart.bleuart import BLEUART

	def rx_received_cb(data: bytes):
		echo = bytes(reversed(data))
		print(f'received data: {data}, sending back: {echo}')
		bleuart.send(echo)

	bleuart = BLEUART(rx_received_cb=rx_received_cb)

def run_bleconfig_test():
	try:
		from devices.uart.bleconfig import BLEConfig
	except ImportError:
		from ..devices.uart.bleconfig import BLEConfig

	def rx_received_cb(data: bytes):
		print(f'received data: {data}')

	bleconfig = BLEConfig(rx_received_cb=rx_received_cb)

	while not bleconfig.success():
		time.sleep(0.1)

	print(f'ssid: {bleconfig.ssid}, password: {bleconfig.password}')

def choose_an_option(title, options):
	print(f'\n{title}:')

	for index, option in enumerate(options, start=1):
		if index == 1:
			print(f'\x1b[32m  [{index}] {option}\033[0m')
		else:
			print(f'  [{index}] {option}')

	selected = None

	while True:
		try:
			selected = input('Choose an option: ')

			if selected == '':
				return 0

			selected = int(selected)

			assert type(selected) is int and 0 < selected <= len(options)

			return selected - 1
		except KeyboardInterrupt:
			return
		except:
			pass


if __name__ == '__main__':
	options = [
		'BLE UART,   details: https://gitee.com/walkline/esp32-ble-uart',
		'BLE Config, details: https://gitee.com/walkline/micropython_ble_config',
	]

	mode = choose_an_option('UART Test Mode', options)

	if mode is not None:
		if mode == MODE_UART:
			run_bleuart_test()
		else:
			run_bleconfig_test()
