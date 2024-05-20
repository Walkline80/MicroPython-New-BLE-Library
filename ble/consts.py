"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from micropython import const


MAX_PAYLOAD_LENGTH = 31 # bytes


class UUIDS(object):
	# region Services UUIDs
	# https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/uuids/service_uuids.yaml
	GENERIC_ACCESS = const(0x1800)
	GENERIC_ATTRIBUTE = const(0x1801)
	DEVICE_INFORMATION = const(0x180A)
	BATTERY_SERVICE = const(0x180F)
	HUMAN_INTERFACE_DEVICE = const(0x1812)

	NORDIC_UART = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
	# endregion


	# region Characteristics UUIDs
	# https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/uuids/characteristic_uuids.yaml
	DEVICE_NAME = const(0x2A00)
	APPEARANCE = const(0x2A01)
	PERIPHERAL_PREFERRED_CONNECTION_PARAMETERS = const(0x2A04)

	SERVICE_CHANGED = const(0x2A05)

	MANUFACTURER_NAME_STRING = const(0x2A29)
	MODEL_NUMBER_STRING = const(0x2A24)
	SERIAL_NUMBER_STRING = const(0x2A25)
	HARDWARE_REVISION_STRING = const(0x2A27)
	FIRMWARE_REVISION_STRING = const(0x2A26)
	SOFTWARE_REVISION_STRING = const(0x2A28)
	PNP_ID = const(0x2A50)

	BATTERY_LEVEL = const(0x2A19)

	HID_INFORMATION = const(0x2A4A)
	BOOT_KEYBOARD_INPUT_REPORT = const(0x2A22)
	BOOT_KEYBOARD_OUTPUT_REPORT = const(0x2A32)
	BOOT_MOUSE_INPUT_REPORT = const(0x2A33)
	REPORT_MAP = const(0x2A4B)
	REPORT = const(0x2A4D)
	HID_CONTROL_POINT = const(0x2A4C)
	PROTOCOL_MODE = const(0x2A4E)

	NORDIC_RX = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
	NORDIC_TX = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
	# endregion


	# region Descriptors UUIDs
	# https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/uuids/descriptors.yaml
	REPORT_REFERENCE = const(0x2908)
	# endregion


class ADType(object):
	FLAGS = const(0x01)
	BIT16_SERVICE_UUID_COMPLETE = const(0x03)
	BIT32_SERVICE_UUID_COMPLETE = const(0x05)
	BIT128_SERVICE_UUID_COMPLETE = const(0x07)
	APPEARANCE_ = const(0x19)
	MANUFACTURER_SPECIFIC_DATA = const(0xFF)
	COMPLETE_LOCAL_NAME = const(0x09)

class IRQ(object):
	CENTRAL_CONNECT = const(1)
	CENTRAL_DISCONNECT = const(2)
	GATTS_WRITE = const(3)
	GATTS_READ_REQUEST = const(4)
	SCAN_RESULT = const(5)
	SCAN_DONE = const(6)
	PERIPHERAL_CONNECT = const(7)
	PERIPHERAL_DISCONNECT = const(8)
	GATTC_SERVICE_RESULT = const(9)
	GATTC_SERVICE_DONE = const(10)
	GATTC_CHARACTERISTIC_RESULT = const(11)
	GATTC_CHARACTERISTIC_DONE = const(12)
	GATTC_DESCRIPTOR_RESULT = const(13)
	GATTC_DESCRIPTOR_DONE = const(14)
	GATTC_READ_RESULT = const(15)
	GATTC_READ_DONE = const(16)
	GATTC_WRITE_DONE = const(17)
	GATTC_NOTIFY = const(18)
	GATTC_INDICATE = const(19)
	GATTS_INDICATE_DONE = const(20)
	MTU_EXCHANGED = const(21)
	L2CAP_ACCEPT = const(22)
	L2CAP_CONNECT = const(23)
	L2CAP_DISCONNECT = const(24)
	L2CAP_RECV = const(25)
	L2CAP_SEND_READY = const(26)
	CONNECTION_UPDATE = const(27)
	ENCRYPTION_UPDATE = const(28)
	GET_SECRET = const(29)
	SET_SECRET = const(30)
	PASSKEY_ACTION = const(31)

class IOCapabilities(object):
	DISPLAY_ONLY = const(0)
	DISPLAY_YESNO = const(1)
	KEYBOARD_ONLY = const(2)
	NO_INPUT_OUTPUT = const(3)
	KEYBOARD_DISPLAY = const(4)

class PasskeyAction(object):
	NONE = const(0)
	INPUT = const(2)
	DISPLAY = const(3)
	NUMERIC_COMPARISON = const(4)

class GATTSErrorCode(object):
	NO_ERROR = const(0x00)
	READ_NOT_PERMITTED = const(0x02)
	WRITE_NOT_PERMITTED = const(0x03)
	INSUFFICIENT_AUTHENTICATION = const(0x05)
	INSUFFICIENT_AUTHORIZATION = const(0x08)
	INSUFFICIENT_ENCRYPTION = const(0x0f)

class Flag(object):
	BROADCAST = const(0x0001)
	READ = const(0x0002)
	WRITE_NO_RESPONSE = const(0x0004)
	WRITE = const(0x0008)
	NOTIFY = const(0x0010)
	INDICATE = const(0x0020)
	AUTHENTICATED_SIGNED_WRITE = const(0x0040)
	AUX_WRITE = const(0x0100)
	READ_ENCRYPTED = const(0x0200)
	READ_AUTHENTICATED = const(0x0400)
	READ_AUTHORIZED = const(0x0800)
	WRITE_ENCRYPTED = const(0x1000)
	WRITE_AUTHENTICATED = const(0x2000)
	WRITE_AUTHORIZED = const(0x4000)

	READ_WRITE = const(READ | WRITE)
	READ_NOTIFY = const(READ | NOTIFY)
