"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from bluetooth import UUID
from ble import *


# Service UUIDs
UUID_NORDIC_UART = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'

# Characteristic UUIDs
UUID_NORDIC_RX = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
UUID_NORDIC_TX = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'


class UARTProfile(Profile):
	'''Nordic UART Profile'''
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self):
		super().__init__()
		self.__make_profile()

	def __make_profile(self):
		self.add_services(
			UART().add_characteristics(
				RX(),
				TX(),
			),
		)


# region Services
class UART(Service):
	def __init__(self):
		super().__init__(UUID(UUID_NORDIC_UART))
# endregion


# region Characteristics
class RX(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_NORDIC_RX), Flag.WRITE)

class TX(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUID_NORDIC_TX), Flag.NOTIFY)
# endregion


# region Descriptors
class ClientCC(Descriptor): # ClientCharacteristicConfiguration
	def __init__(self):
		super().__init__(UUID(UUID_CLIENT_CC), Flag.READ_WRITE)
# endregion
