"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ble-hid-controller
"""
'''
Main Item:
	Input, Output, Feature, Collection, End Collection

Global Item:
	Usage Page, Logical Min/Max, Physical Min/Max,
	Unit Exponent, Unit, Report ID/Size/Count, Push, Pop

Local Item:
	Usage, Usage Min/Max,
	Designator Index/Min/Max,
	String Index/Min/Max, Delimiter
'''

'''
Keycode Usage ID:
	https://www.usb.org/sites/default/files/hut1_5.pdf#page=90 @ page 90
'''
REPORT_MAP_DATA = [
	0x05, 0x01,	# (G) Usage Page (Generic Desktop Ctrls)
	0x09, 0x06,	# (L) Usage (Keyboard)

	# 控制键
	0xA1, 0x01,	# (M) Collection (Application)
	0x85, 0x01, # (G)   Report ID (1)
	0x05, 0x07,	# (G)   Usage Page (Kbrd/Keypad)
	0x19, 0xE0,	# (L)     Usage Minimum (0xE0)
	0x29, 0xE7,	# (L)     Usage Maximum (0xE7)
	0x15, 0x00,	# (G)     Logical Minimum (0)
	0x25, 0x01,	# (G)     Logical Maximum (1)
	0x95, 0x08,	# (G)     Report Count (8)
	0x75, 0x01,	# (G)     Report Size (1)
	0x81, 0x02,	# (M)     Input (Data,Var,Abs)

	# 保留字节
	0x95, 0x01,	# (G)     Report Count (1)
	0x75, 0x08,	# (G)     Report Size (8)
	0x81, 0x03,	# (M)     Input (Const,Var,Abs)

	# 6 个按键键值
	0x05, 0x07,	# (G)   Usage Page (Kbrd/Keypad)
	0x19, 0x00,	# (L)     Usage Minimum (0x00)
	0x29, 0x65,	# (L)     Usage Maximum (0x65)
	0x15, 0x00,	# (G)     Logical Minimum (0)
	0x25, 0x65,	# (G)     Logical Maximum (101)
	0x95, 0x06,	# (G)     Report Count (6)
	0x75, 0x08,	# (G)     Report Size (8)
	0x81, 0x00,	# (M)     Input (Data,Array,Abs)

	0x05, 0x08,	# (G)   Usage Page (LEDs)
	0x95, 0x05,	# (G)   Report Count (5)
	0x75, 0x01,	# (G)   Report Size (1)
	0x19, 0x01,	# (L)   Usage Minimum (Num Lock)
	0x29, 0x05,	# (L)   Usage Maximum (Kana)
	0x91, 0x02,	# (M)   Output (Data,Var,Abs)

	0x95, 0x01,	# (G)   Report Count (1)
	0x75, 0x03,	# (G)   Report Size (3)
	0x91, 0x03,	# (M)   Output (Const,Var,Abs)
	0xC0, 		# (M) End Collection
]
