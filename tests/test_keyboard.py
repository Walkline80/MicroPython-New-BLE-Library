"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ble-hid-controller
"""
import random
from devices.keyboard import BLEKeyboard104
from drivers.button import Button


class KeyboardTest(object):
	MODE_ONE_REPORT    = 0
	MODE_THREE_REPORTS = 1
	MODE_PRESS_18_KEYS = 2

	def __init__(self, mode: int = MODE_THREE_REPORTS, button_pin: int = 9):
		self.__last_key_code  = None
		self.__last_key_index = None
		self.__last_report_id = None

		self.__report_count = 3 if mode in (self.MODE_THREE_REPORTS, self.MODE_PRESS_18_KEYS) else 1

		if self.__report_count == 3:
			from hid.reportmap.keyboard3 import REPORT_MAP_DATA

		self.__keyboard = BLEKeyboard104(
			report_map=REPORT_MAP_DATA if self.__report_count == 3 else None,
			report_count=self.__report_count
		)

		self.__button = Button(
			pin=[button_pin],
			hold_cb=self.__button_down_cb if mode in (self.MODE_ONE_REPORT, self.MODE_THREE_REPORTS) else None,
			release_cb=self.__button_up_cb if mode in (self.MODE_ONE_REPORT, self.MODE_THREE_REPORTS) else None,
			click_cb=self.__button_click_cb if mode in (self.MODE_PRESS_18_KEYS,) else None
		)

		self.__keyboard.update_battery_level()

	def __button_down_cb(self, pin: int):
		self.__last_key_code  = random.randint(4, 39)
		self.__last_key_index = random.randint(2, 7)
		self.__last_report_id = random.randint(0, self.__report_count - 1)

		modifier  = 0b00000000 # RGUI, RAlt, RShift, RCtrl, LGUI, LAlt, LShift, LCtrl
		key_data  = bytearray([modifier, 0x00]) + bytes(6)

		print(f'[DN] report_id: {self.__last_report_id}, key_index: {self.__last_key_index}, key_code: {self.__last_key_code}')

		key_data[self.__last_key_index] = self.__last_key_code
		self.__keyboard.send_kb_key_down(key_data, self.__last_report_id)

	def __button_up_cb(self, pin: int):
		modifier = 0b00000000
		key_data = bytearray([modifier, 0x00]) + bytes(6)

		print(f'[UP] report_id: {self.__last_report_id}, key_index: {self.__last_key_index}, key_code: {self.__last_key_code}\n')

		self.__keyboard.send_kb_key_up(key_data, self.__last_report_id)

	def __button_click_cb(self, pin: int):
		modifier  = 0b00000000
		key_codes = bytes([keycode for keycode in range(4, 23)])
		key_data  = bytearray([modifier, 0x00]) + bytes(6)

		for count in range(self.__report_count):
			for index, key_index in enumerate(range(2, 8)):
				key_data[key_index] = key_codes[count * 6 + index]

			self.__keyboard.send_kb_key_down(key_data, count)

		key_data  = bytearray([modifier, 0x00]) + bytes(6)

		for count in range(self.__report_count):
			self.__keyboard.send_kb_key_up(key_data, count)


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
		'Using 1 HID report descriptor, randomly send a key code',
		'Using 3 HID report descriptors, randomly send a key code',
		'Using 3 HID report descriptors, send 18 key codes at once'
	]

	mode = choose_an_option('Keyboard Test Mode', options)

	if mode is not None:
		test = KeyboardTest(
			mode=mode,
			button_pin=9
		)