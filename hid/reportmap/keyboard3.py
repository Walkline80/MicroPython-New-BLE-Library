"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ble-hid-controller
"""

'''
Key codes usage ids:
	https://www.usb.org/sites/default/files/hut1_21.pdf @ page 82
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
	0x81, 0x02,	# (M)     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)

	# 保留字节
	0x95, 0x01,	# (G)     Report Count (1)
	0x75, 0x08,	# (G)     Report Size (8)
	0x81, 0x03,	# (M)     Input (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)

	# 6 个按键键值
	0x05, 0x07,	# (G)   Usage Page (Kbrd/Keypad)
	0x19, 0x00,	# (L)     Usage Minimum (0x00)
	0x29, 0x65,	# (L)     Usage Maximum (0x65)
	0x15, 0x00,	# (G)     Logical Minimum (0)
	0x25, 0x65,	# (G)     Logical Maximum (101)
	0x95, 0x06,	# (G)     Report Count (6)
	0x75, 0x08,	# (G)     Report Size (8)
	0x81, 0x00,	# (M)     Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)

	0x05, 0x08,	# (G)   Usage Page (LEDs)
	0x95, 0x05,	# (G)   Report Count (5)
	0x75, 0x01,	# (G)   Report Size (1)
	0x19, 0x01,	# (L)   Usage Minimum (Num Lock)
	0x29, 0x05,	# (L)   Usage Maximum (Kana)
	0x91, 0x02,	# (M)   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)

	0x95, 0x01,	# (G)   Report Count (1)
	0x75, 0x03,	# (G)   Report Size (3)
	0x91, 0x03,	# (M)   Output (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)

	0xC0, 		# (M) End Collection


	0x05, 0x01,	# (G) Usage Page (Generic Desktop Ctrls)
	0x09, 0x06,	# (L) Usage (Keyboard)

	# 控制键
	0xA1, 0x01,	# (M) Collection (Application)
	0x85, 0x02, # (G)   Report ID (2)
	0x05, 0x07,	# (G)   Usage Page (Kbrd/Keypad)
	0x19, 0xE0,	# (L)     Usage Minimum (0xE0)
	0x29, 0xE7,	# (L)     Usage Maximum (0xE7)
	0x15, 0x00,	# (G)     Logical Minimum (0)
	0x25, 0x01,	# (G)     Logical Maximum (1)
	0x95, 0x08,	# (G)     Report Count (8)
	0x75, 0x01,	# (G)     Report Size (1)
	0x81, 0x02,	# (M)     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)

	# 保留字节
	0x95, 0x01,	# (G)     Report Count (1)
	0x75, 0x08,	# (G)     Report Size (8)
	0x81, 0x03,	# (M)     Input (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)

	# 6 个按键键值
	0x05, 0x07,	# (G)   Usage Page (Kbrd/Keypad)
	0x19, 0x00,	# (L)     Usage Minimum (0x00)
	0x29, 0x65,	# (L)     Usage Maximum (0x65)
	0x15, 0x00,	# (G)     Logical Minimum (0)
	0x25, 0x65,	# (G)     Logical Maximum (101)
	0x95, 0x06,	# (G)     Report Count (6)
	0x75, 0x08,	# (G)     Report Size (8)
	0x81, 0x00,	# (M)     Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)

	0x05, 0x08,	# (G)   Usage Page (LEDs)
	0x95, 0x05,	# (G)   Report Count (5)
	0x75, 0x01,	# (G)   Report Size (1)
	0x19, 0x01,	# (L)   Usage Minimum (Num Lock)
	0x29, 0x05,	# (L)   Usage Maximum (Kana)
	0x91, 0x02,	# (M)   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)

	0x95, 0x01,	# (G)   Report Count (1)
	0x75, 0x03,	# (G)   Report Size (3)
	0x91, 0x03,	# (M)   Output (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)

	0xC0, 		# (M) End Collection


	0x05, 0x01,	# (G) Usage Page (Generic Desktop Ctrls)
	0x09, 0x06,	# (L) Usage (Keyboard)

	# 控制键
	0xA1, 0x01,	# (M) Collection (Application)
	0x85, 0x03, # (G)   Report ID (3)
	0x05, 0x07,	# (G)   Usage Page (Kbrd/Keypad)
	0x19, 0xE0,	# (L)     Usage Minimum (0xE0)
	0x29, 0xE7,	# (L)     Usage Maximum (0xE7)
	0x15, 0x00,	# (G)     Logical Minimum (0)
	0x25, 0x01,	# (G)     Logical Maximum (1)
	0x95, 0x08,	# (G)     Report Count (8)
	0x75, 0x01,	# (G)     Report Size (1)
	0x81, 0x02,	# (M)     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)

	# 保留字节
	0x95, 0x01,	# (G)     Report Count (1)
	0x75, 0x08,	# (G)     Report Size (8)
	0x81, 0x03,	# (M)     Input (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)

	# 6 个按键键值
	0x05, 0x07,	# (G)   Usage Page (Kbrd/Keypad)
	0x19, 0x00,	# (L)     Usage Minimum (0x00)
	0x29, 0x65,	# (L)     Usage Maximum (0x65)
	0x15, 0x00,	# (G)     Logical Minimum (0)
	0x25, 0x65,	# (G)     Logical Maximum (101)
	0x95, 0x06,	# (G)     Report Count (6)
	0x75, 0x08,	# (G)     Report Size (8)
	0x81, 0x00,	# (M)     Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)

	0x05, 0x08,	# (G)   Usage Page (LEDs)
	0x95, 0x05,	# (G)   Report Count (5)
	0x75, 0x01,	# (G)   Report Size (1)
	0x19, 0x01,	# (L)   Usage Minimum (Num Lock)
	0x29, 0x05,	# (L)   Usage Maximum (Kana)
	0x91, 0x02,	# (M)   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)

	0x95, 0x01,	# (G)   Report Count (1)
	0x75, 0x03,	# (G)   Report Size (3)
	0x91, 0x03,	# (M)   Output (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)

	0xC0, 		# (M) End Collection
]
