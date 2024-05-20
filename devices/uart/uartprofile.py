"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from ble import *


class UARTProfile(Profile):
	'''Nordic UART Profile'''
	def __init__(self):
		super().__init__()

		self.__make_profile()

	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

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
		super().__init__(UUID(UUIDS.NORDIC_UART))
# endregion Services


# region Characteristics
class RX(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.NORDIC_RX), Flag.WRITE)

class TX(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.NORDIC_TX), Flag.NOTIFY)
# endregion Characteristics


# region Descriptors
# endregion Descriptors
