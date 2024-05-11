"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ble-hid-controller
"""
import random
from devices.keyboard import BLEKeyboard104
from drivers.button import Button


def press_18_keys():
	if report_count == 3:
		modifier  = 0b00000000
		key_codes = bytes([keycode for keycode in range(4, 23)])
		key_data  = bytearray([modifier, 0x00]) + bytes(6)

		for count in range(report_count):
			for index, key_index in enumerate(range(2, 8)):
				key_data[key_index] = key_codes[count * 6 + index]

			keyboard.send_kb_key_down(key_data, count)

		key_data  = bytearray([modifier, 0x00]) + bytes(6)

		for count in range(report_count):
			keyboard.send_kb_key_up(key_data, count)

def press_random_key():
	modifier  = 0b00000000 # RGUI, RAlt, RShift, RCtrl, LGUI, LAlt, LShift, LCtrl
	key_code  = random.randint(4, 39)
	key_index = random.randint(2, 7)
	key_data  = bytearray([modifier, 0x00]) + bytes(6)
	report_id = random.randint(0, report_count - 1)

	print(f'report_id: {report_id}, key_index: {key_index}, key_code: {key_code}')

	key_data[key_index] = key_code
	keyboard.send_kb_key_down(key_data, report_id)

	key_data[key_index] = 0x00
	keyboard.send_kb_key_up(key_data, report_id)

def button_click_cb(pin: int):
	if pin == 9:
		if True:
			press_random_key()
		else:
			press_18_keys()


if __name__ == '__main__':
	report_count = 3

	if report_count == 3:
		from hid.reportmap.keyboard3 import REPORT_MAP_DATA

	keyboard = BLEKeyboard104(
		report_map=REPORT_MAP_DATA if report_count == 3 else None,
		report_count=report_count
	)
	button   = Button(
		pin=[9],
		click_cb=button_click_cb,
	)

	keyboard.update_battery_level()
