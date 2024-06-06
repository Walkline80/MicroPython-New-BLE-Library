"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import time
from profiles.findme import FindMeValues
from tests.utils.utilities import Utilities

import random
random.seed(random.randint(-2**16, 2**16))


MODE_FINDME_SERVER = 0
MODE_FINDME_CLIENT = 1

FINDME_SERVER_LOCAL_NAME = 'findme-target'

AlertLevel = FindMeValues.Consts.AlertLevel

def printf(msg, *args, **kwargs):
	print(f'\033[1;37m[INFO]\033[0m {msg}', *args, **kwargs)


def run_findme_server_test():
	from devices.findme.findme_server import FindMeServer

	def alert_level_cb(level: int):
		print(f'Received a new alert at level: {level} ({AlertLevel.LEVELS_MAP[level]})')

	findme_server = FindMeServer(
		device_name=FINDME_SERVER_LOCAL_NAME,
		alert_level_cb=alert_level_cb
	)

def run_findme_client_test():
	from devices.findme.findme_client import FindMeClient

	def found_target_cb():
		alert_level = random.choice(list(FindMeValues.Consts.AlertLevel.LEVELS_MAP))
		findme_client.set_alert_level(alert_level)

		printf(f'Set alert level to {alert_level} ({FindMeValues.Consts.AlertLevel.LEVELS_MAP[alert_level]})')

		time.sleep(1)
		findme_client.disconnect()

	findme_client = FindMeClient(found_target_cb=found_target_cb)
	findme_client.scan(0)


if __name__ == '__main__':
	options = [
		'Find Me Server: Acting as a Find Me Target',
		'Find Me Client: Acting as a Find Me Locator',
	]

	mode = Utilities.choose_an_option('Find Me Test Mode', options)

	if mode is not None:
		if mode == MODE_FINDME_SERVER:
			run_findme_server_test()
		else:
			run_findme_client_test()
