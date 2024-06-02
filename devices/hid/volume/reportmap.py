"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
REPORT_MAP_DATA = [
	0x05, 0x0C, # Usage Page (Consumer)
	0x09, 0x01, # Usage (Consumer Control)
	0xA1, 0x01, # Collection (Application)
	0x85, 0x01, #   Report ID (1)
	0x19, 0xE9, #   Usage Minimum (Volume Up)
	0x29, 0xEA, #   Usage Maximum (Volume Down)
	0x15, 0x01, #   Logical Minimum (1)
	0x25, 0x02, #   Logical Maximum (2)
	0x75, 0x08, #   Report Size (8)
	0x95, 0x01, #   Report Count (1)
	0x81, 0x00, #   Input (Data,Arr,Abs)
	0xC0,       # End Collection

	0x05, 0x0C, # Usage Page (Consumer)
	0x09, 0x01, # Usage (Consumer Control)
	0xA1, 0x01, # Collection (Application)
	0x85, 0x02, #   Report ID (2)
	0x09, 0xe0, #   Usage (Volume)
	0x15, 0x00, #   Logical Minimum (0)
	0x25, 0x64, #   Logical Maximum (100)
	0x75, 0x08, #   Report Size (8)
	0x95, 0x01, #   Report Count (1)
	0x81, 0x02, #   Input(Data,Var,Abs)
	0xC0,       # End Collection
]
