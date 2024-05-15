"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ble-hid-controller
"""
from ble import *


class HIDProfile(Profile):
	'''只包含 HID 所需的三个服务'''
	def __init__(self):
		super().__init__()

		self.__make_profile()

	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __make_profile(self):
		self.add_services(
			DeviceInformation().add_characteristics(
				ManufacturerNameString(),
				ModelNumberString(),
				SerialNumberString(),
				HardwareRevisionString(),
				FirmwareRevisionString(),
				SoftwareRevisionString(),
				PNPID(),
			),
			BatteryService().add_characteristics(
				BatteryLevel(),
			),
			HumanInterfaceDevice().add_characteristics(
				HIDInformation(),
				BootKeyboardInputReport(),
				BootKeyboardOutputReport(),
				BootMouseInputReport(),
				ReportMap(),
				HIDControlPoint(),
				ProtocolMode(),
			),
		)


class KeyboardProfile(HIDProfile):
	def __init__(self, report_count: int = 1):
		super().__init__()

		self.__report_count = report_count
		device = HumanInterfaceDevice()

		device.add_characteristics(
			Report().add_descriptors(
				ReportReference(), # input
			),
			Report().add_descriptors(
				ReportReference(), # output
			),
		)

		for _ in range(self.__report_count - 1):
			device.add_characteristics(
				Report().add_descriptors(
					ReportReference(), # input
				),
			)

		self.add_services(device)

	@property
	def report_count(self):
		return self.__report_count


# region Services
class DeviceInformation(Service):
	def __init__(self):
		super().__init__(UUID(UUIDS.DEVICE_INFORMATION))

class BatteryService(Service):
	def __init__(self):
		super().__init__(UUID(UUIDS.BATTERY_SERVICE))

class HumanInterfaceDevice(Service):
	def __init__(self):
		super().__init__(UUID(UUIDS.HUMAN_INTERFACE_DEVICE))
# endregion Services


# region Characteristics

# region DeviceInformation's Characteristics
class ManufacturerNameString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.MANUFACTURER_NAME_STRING), Flag.READ)

class ModelNumberString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.MODEL_NUMBER_STRING), Flag.READ)

class SerialNumberString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.SERIAL_NUMBER_STRING), Flag.READ)

class HardwareRevisionString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.HARDWARE_REVISION_STRING), Flag.READ)

class FirmwareRevisionString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.FIRMWARE_REVISION_STRING), Flag.READ)

class SoftwareRevisionString(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.SOFTWARE_REVISION_STRING), Flag.READ)

class PNPID(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.PNP_ID), Flag.READ)
# endregion DeviceInformation's Characteristics


# region BatteryService's Characteristics
class BatteryLevel(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.BATTERY_LEVEL), Flag.READ) # | Flag.NOTIFY
# endregion BatteryService's Characteristics


# region HumanInterfaceDevice's Characteristics
class HIDInformation(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.HID_INFORMATION), Flag.READ)

class BootKeyboardInputReport(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.BOOT_KEYBOARD_INPUT_REPORT), Flag.READ_NOTIFY)

class BootKeyboardOutputReport(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.BOOT_KEYBOARD_OUTPUT_REPORT), Flag.READ_WRITE | Flag.WRITE_NO_RESPONSE)

class BootMouseInputReport(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.BOOT_MOUSE_INPUT_REPORT), Flag.READ_WRITE)

class ReportMap(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.REPORT_MAP), Flag.READ)

class Report(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.REPORT), Flag.READ_WRITE | Flag.NOTIFY | Flag.WRITE_NO_RESPONSE)

class HIDControlPoint(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.HID_CONTROL_POINT), Flag.WRITE_NO_RESPONSE)

class ProtocolMode(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.PROTOCOL_MODE), Flag.READ | Flag.WRITE_NO_RESPONSE)
# endregion HumanInterfaceDevice's Characteristics

# endregion Characteristics


# region Descriptors

# region Report Characteristic's Descriptors
class ReportReference(Descriptor):
	def __init__(self):
		Descriptor.__init__(self, UUID(UUIDS.REPORT_REFERENCE), Flag.READ_WRITE | Flag.WRITE_NO_RESPONSE)
# endregion Report Characteristic's Descriptors

# endregion Descriptors
