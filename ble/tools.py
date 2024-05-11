"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ble-hid-controller
"""
from .consts import *
from struct import pack


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
	def make_appearance(category:int, subcategory:int) -> int:
		'''生成设备外观值'''
		return (category << 6) | subcategory
