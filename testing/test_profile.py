"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from ble.tools import printf
from ble.profile import Profile
from profiles.hid import *
from testing.utils.utilities import Utilities


MODE_MAKE_PROFILE = 0
MODE_ADD_SERVICES = 1

def preview(profile: Profile):
	print('Preview', profile.__qualname__)

	for service in profile.get_services():
		printf(service[0])

		for characteristic in service[1]:
			printf(f'  - {characteristic[0]}, FLAGS({characteristic[1]})')

			if len(characteristic) == 3:
				for descriptor in characteristic[2]:
					printf(f'      - {descriptor[0]}, FLAGS({descriptor[1]})')

		printf(f'Services: {profile.get_services()}')
		printf(f'UUIDs: {profile.get_services_uuid()}\n')

def run_make_profile_test():
	customized_profile = Profile()
	customized_profile.add_services(
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
			Report().add_descriptors(
				ReportReference(),
			),
			HIDControlPoint(),
			ProtocolMode(),
		),
	)

	hid_profile = HIDProfile()

	preview(customized_profile)
	preview(hid_profile)

def run_add_services_test():
	profile = Profile()
	profile.add_services(
		DeviceInformation().add_characteristics(
			ManufacturerNameString(),
		),
	)

	preview(profile)

	profile.add_services(
		DeviceInformation().add_characteristics(
			SerialNumberString(),
			PNPID().add_descriptors(
				ReportReference(),
			),
		),
	)

	preview(profile)

	profile = KeyboardProfile(report_count=5)

	preview(profile)


if __name__ == '__main__':
	options = [
		'Make a profile',
		'Add services to profile',
	]

	mode = Utilities.choose_an_option('Profile Test Mode', options)

	if mode is not None:
		if mode == MODE_MAKE_PROFILE:
			run_make_profile_test()
		else:
			run_add_services_test()
