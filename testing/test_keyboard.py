"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from time import sleep_ms
from random import randint
from testing.drivers.button import Button
from testing.utils.utilities import Utilities


MODE_ONE_REPORT      = 0
MODE_THREE_REPORTS   = 1
MODE_PRESS_18_KEYS   = 2
MODE_PRESS_95_KEYS   = 3
MODE_CONSUMER_VOLUME = 4


class KeyboardTest1(object):
	def __init__(self, mode: int = MODE_ONE_REPORT, button_pin: int = 9):
		self.__last_key_code  = None
		self.__last_key_index = None
		self.__last_report_id = None

		self.__report_count = 3 if mode in (MODE_THREE_REPORTS, MODE_PRESS_18_KEYS) else 1

		if self.__report_count == 3:
			from devices.hid.keyboard_1.reportmap.keyboard2 import REPORT_MAP_DATA

		self.__keyboard = BLEKeyboard104(
			report_map=REPORT_MAP_DATA if self.__report_count == 3 else None,
			report_count=self.__report_count,
			led_status_cb=self.__led_status_cb
		)

		self.__button = Button(
			pin=[button_pin],
			hold_cb=self.__button_down_cb if mode in (MODE_ONE_REPORT, MODE_THREE_REPORTS) else None,
			release_cb=self.__button_up_cb if mode in (MODE_ONE_REPORT, MODE_THREE_REPORTS) else None,
			click_cb=self.__button_click_cb if mode in (MODE_PRESS_18_KEYS,) else None
		)

		self.__keyboard.update_battery_level()

	def __button_down_cb(self, pin: int):
		self.__last_key_code  = randint(4, 39)
		self.__last_key_index = randint(2, 7)
		self.__last_report_id = randint(0, self.__report_count - 1)

		modifier  = 0b00000000 # RGUI, RAlt, RShift, RCtrl, LGUI, LAlt, LShift, LCtrl
		key_data  = bytearray([modifier, 0x00]) + bytes(6)

		print(f'[DN] report_id: {self.__last_report_id}, key_index: {self.__last_key_index}, key_code: {self.__last_key_code}')

		key_data[self.__last_key_index] = self.__last_key_code
		self.__keyboard.send_kb_key(key_data, self.__last_report_id)

	def __button_up_cb(self, pin: int):
		modifier = 0b00000000
		key_data = bytearray([modifier, 0x00]) + bytes(6)

		print(f'[UP] report_id: {self.__last_report_id}, key_index: {self.__last_key_index}, key_code: {self.__last_key_code}\n')

		self.__keyboard.send_kb_key(key_data, self.__last_report_id)

	def __button_click_cb(self, pin: int):
		modifier  = 0b00000000
		key_codes = bytes([keycode for keycode in range(4, 23)])
		key_data  = bytearray([modifier, 0x00]) + bytes(6)

		for count in range(self.__report_count):
			for index, key_index in enumerate(range(2, 8)):
				key_data[key_index] = key_codes[count * 6 + index]

			self.__keyboard.send_kb_key(key_data, count)

		key_data  = bytearray([modifier, 0x00]) + bytes(6)

		for count in range(self.__report_count):
			self.__keyboard.send_kb_key(key_data, count)

	def __led_status_cb(self, num_lock, caps_lock, scroll_lock):
		print('   num_lock:', num_lock)
		print('  caps_lock:', caps_lock)
		print('scroll_lock:', scroll_lock)


class KeyboardTest2(object):
	def __init__(self, button_pin: int = 9):
		self.__keyboard = BLEKeyboard104(
			led_status_cb=self.__led_status_cb
		)

		self.__button = Button(
			pin=[button_pin],
			hold_cb=self.__button_down_cb,
			release_cb=self.__button_up_cb,
		)

		self.__keyboard.update_battery_level()

	def __button_down_cb(self, pin: int):
		modifier  = 0b00000000
		key_data  = bytearray([modifier, 0x00]) + bytearray([0xff for _ in range(13)])

		# 排除一些按键
		key_data[8] = 0xdf # caps_lock
		key_data[10] = 0xf3 # scroll_lock & print_screen
		key_data[11] = 0x7f # num_lock

		self.__keyboard.send_kb_key(key_data)

	def __button_up_cb(self, pin: int):
		modifier  = 0b00000000
		key_data  = bytearray([modifier, 0x00]) + bytearray([0x00 for _ in range(13)])

		self.__keyboard.send_kb_key(key_data)

	def __led_status_cb(self, num_lock, caps_lock, scroll_lock):
		print('   num_lock:', num_lock)
		print('  caps_lock:', caps_lock)
		print('scroll_lock:', scroll_lock)


class ConsumerVolumeTest(object):
	def __init__(self, button_pin: int = 9):
		self.__volume = BLEVolumeKey(report_count=2)

		self.__button = Button(
			pin=[button_pin],
			click_cb=self.__button_click_cb,
		)

		self.__volume.update_battery_level()

	def __button_click_cb(self, pin: int):
		delay = 1000

		for report_id in range(2):
			print(f'Testing send volume keys via report {report_id + 1}')

			if report_id == 0:
				self.__volume.send_volume_up_1()
				sleep_ms(delay)
				self.__volume.send_volume_down_1()
				sleep_ms(delay)
				self.__volume.send_volume_release_1()

				self.__volume.send_volume(bytearray([self.__volume.REPORT_1_VOL_UP]), report_id)
				sleep_ms(delay)
				self.__volume.send_volume(bytearray([self.__volume.REPORT_1_VOL_DOWN]), report_id)
				sleep_ms(delay)
				self.__volume.send_volume(bytearray([0]), report_id)
				sleep_ms(delay)
			elif report_id == 1:
				# Report 2 只适用于 Windows
				self.__volume.send_volume_up_2()
				sleep_ms(delay)
				self.__volume.send_volume_down_2()
				sleep_ms(delay)
				self.__volume.send_volume_release_2()

				self.__volume.send_volume(bytearray([self.__volume.REPORT_2_VOL_UP]), report_id)
				sleep_ms(delay)
				self.__volume.send_volume(bytearray([self.__volume.REPORT_2_VOL_DOWN]), report_id)
				sleep_ms(delay)
				self.__volume.send_volume(bytearray([0]), report_id)
				sleep_ms(delay)


if __name__ == '__main__':
	button_pin = 9

	options = [
		'Using 1 HID report descriptor, randomly send a key code',
		'Using 3 HID report descriptors, randomly send a key code',
		'Using 3 HID report descriptors, send 18 key codes at once',
		'Using 1 HID report descriptor, send 95 key codes at once',
		'Using 2 HID report descriptors, send volume up/down'
	]

	mode = Utilities.choose_an_option('Keyboard Test Mode', options)

	if mode is not None:
		if mode == MODE_PRESS_95_KEYS:
			# 实际测试 92 键，测试时务必使用键盘检测工具
			# https://key.motsuni.cn/
			from devices.hid.keyboard_2.keyboard import BLEKeyboard104
			test = KeyboardTest2(button_pin=button_pin)
		elif mode == MODE_CONSUMER_VOLUME:
			from devices.hid.volume.volume import BLEVolumeKey
			test = ConsumerVolumeTest(button_pin=button_pin)
		else:
			from devices.hid.keyboard_1.keyboard import BLEKeyboard104
			test = KeyboardTest1(mode=mode, button_pin=button_pin)
