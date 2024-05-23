"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from micropython import const
from struct import pack, unpack
from bluetooth import UUID


class ADType(object):
	FLAGS = const(0x01)
	BIT16_SERVICE_UUID_COMPLETE = const(0x03)
	BIT32_SERVICE_UUID_COMPLETE = const(0x05)
	BIT128_SERVICE_UUID_COMPLETE = const(0x07)
	COMPLETE_LOCAL_NAME = const(0x09)
	TX_POWER_LEVEL = const(0x0A)
	SERVICE_DATA = const(0x16) # Service Data - 16-bit UUID
	APPEARANCE_ = const(0x19)
	MANUFACTURER_SPECIFIC_DATA = const(0xFF)


class BLETools(object):
	@staticmethod
	def generate_advertising_payload(services: list = None, *, name: str = None, appearance: int = 0) -> bytearray:
		'''Generate paylaod for advertising and/or scan response'''
		payload = bytearray()

		def _append(adv_type, value):
			nonlocal payload
			payload += pack('BB', len(value) + 1, adv_type) + value

		_append(ADType.FLAGS, pack('B', 0x06))

		if services:
			for uuid in services:
				b = bytes(uuid)

				if len(b) == 2:
					_append(ADType.BIT16_SERVICE_UUID_COMPLETE, b)
				elif len(b) == 4:
					_append(ADType.BIT32_SERVICE_UUID_COMPLETE, b)
				elif len(b) == 16:
					_append(ADType.BIT128_SERVICE_UUID_COMPLETE, b)

		if name:
			_append(ADType.COMPLETE_LOCAL_NAME, name)

		if appearance:
			_append(ADType.APPEARANCE_, pack('<H', appearance))

		return payload

	@staticmethod
	def decode_mac(addr: bytes) -> str:
		'''Decode readable mac address from advertising addr'''
		if isinstance(addr, memoryview):
			addr = bytes(addr)

		assert isinstance(addr, bytes) and len(addr) == 6, ValueError('mac address value error')
		return ':'.join(['%02X' % byte for byte in addr])

	@staticmethod
	def decode_name(payload):
		n = BLETools.__decode_field(payload, ADType.COMPLETE_LOCAL_NAME)
		return str(n[0], "utf-8") if n else ""

	@staticmethod
	def decode_services(payload):
		services = []

		for u in BLETools.__decode_field(payload, ADType.BIT16_SERVICE_UUID_COMPLETE):
			services.append(UUID(unpack("<h", u)[0]))
		for u in BLETools.__decode_field(payload, ADType.BIT32_SERVICE_UUID_COMPLETE):
			services.append(UUID(unpack("<d", u)[0]))
		for u in BLETools.__decode_field(payload, ADType.BIT128_SERVICE_UUID_COMPLETE):
			services.append(UUID(u))

		return services

	@staticmethod
	def decode_services_data(payload):
		services = []
		data = []

		for u in BLETools.__decode_field(payload, ADType.SERVICE_DATA):
			services.append(UUID(u[:2]))
			data.append(u[2:])

		return services, data

	@staticmethod
	def __decode_field(payload, adv_type):
		i = 0
		result = []

		while i + 1 < len(payload):
			if payload[i + 1] == adv_type:
				result.append(payload[i + 2 : i + payload[i] + 1])

			i += 1 + payload[i]

		return result

	@staticmethod
	def make_appearance(category:int, subcategory:int) -> int:
		'''生成设备外观值'''
		return (category << 6) | subcategory
