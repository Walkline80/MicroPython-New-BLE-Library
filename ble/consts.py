"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from micropython import const


MAX_PAYLOAD_LENGTH = 31 # bytes


# Service UUIDs
# 	https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/uuids/service_uuids.yaml

# Characteristic UUIDs
# 	https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/uuids/characteristic_uuids.yaml

# Descriptor UUIDs
# 	https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/uuids/descriptors.yaml


class AddressMode(object):
	PUBLIC = const(0x00) # Use the controller’s public address
	RANDOM = const(0x01) # Use a generated static address
	RPA    = const(0x02) # Use resolvable private addresses
	NRPA   = const(0x03) # Use non-resolvable private addresses

class ADVType(object):
	IND         = const(0x00) # connectable and scannable undirected advertising
	DIRECT_IND  = const(0x01) # connectable directed advertising
	SCAN_IND    = const(0x02) # scannable undirected advertising
	NONCONN_IND = const(0x03) # non-connectable undirected advertising
	SCAN_RSP    = const(0x04) # scan response

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

class IOCapability(object):
	DISPLAY_ONLY     = const(0)
	DISPLAY_YESNO    = const(1)
	KEYBOARD_ONLY    = const(2)
	NO_INPUT_OUTPUT  = const(3)
	KEYBOARD_DISPLAY = const(4)

class PasskeyAction(object):
	NONE               = const(0)
	INPUT              = const(2)
	DISPLAY            = const(3)
	NUMERIC_COMPARISON = const(4)

class GATTSErrorCode(object):
	NO_ERROR                    = const(0x00)
	READ_NOT_PERMITTED          = const(0x02)
	WRITE_NOT_PERMITTED         = const(0x03)
	INSUFFICIENT_AUTHENTICATION = const(0x05)
	INSUFFICIENT_AUTHORIZATION  = const(0x08)
	INSUFFICIENT_ENCRYPTION     = const(0x0f)

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
