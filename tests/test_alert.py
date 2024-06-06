"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
from profiles.alert import AlertNotificationValues
from tests.utils.utilities import Utilities
from tests.utils.dispatcher import Dispatcher

import random
random.seed(random.randint(-2**16, 2**16))


MODE_ALERT_SERVER = 0
MODE_ALERT_CLIENT = 1

ALERT_SERVER_LOCAL_NAME = 'alert-server'

AlertCategory = AlertNotificationValues.Consts.AlertCategory
AlertCommand  = AlertNotificationValues.Consts.AlertCommand

def printf(msg, *args, **kwargs):
	print(f'\033[1;37m[INFO]\033[0m {msg}', *args, **kwargs)

def run_alert_server_test():
	from devices.alert.alert_server import AlertNotificationServer

	def task_send_alert():
		alert_type = random.randint(1, 2)
		category   = random.choice(list(AlertCategory.CATEGORIES))
		number     = random.randint(0, 255)

		if alert_type == 1:
			text = f'{number} new messages'
			alert.send_new_alert(category, number, text)
		else:
			alert.send_unread_alert_status(category, number)

	def task_response_control_point():
		nonlocal category_id, command_id

		if category_id is None or command_id is None:
			return

		if command_id == AlertCommand.ENABLE_NEW_ALERT:
			alert.enable_new_alert(category_id)
		elif command_id == AlertCommand.ENABLE_UNREAD_STATUS:
			alert.enable_unread_alert_status(category_id)
		elif command_id == AlertCommand.DISABLE_NEW_ALERT:
			alert.disable_new_alert(category_id)
		elif command_id == AlertCommand.DISABLE_UNREAD_STATUS:
			alert.disable_unread_alert_status(category_id)
		elif command_id == AlertCommand.NOTIFY_NEW_ALERT_IMMEDIATELY:
			alert.send_new_alert(category_id, 5, 'Hello, MicroPython')
		elif command_id == AlertCommand.NOTIFY_UNREAD_STATUS_IMMEDIATELY:
			alert.send_unread_alert_status(category_id, 15)

		category_id = command_id = None

	def control_point_cb(command, category):
		nonlocal command_id, category_id

		command_id, category_id = command, category
		printf(f'{AlertCommand.COMMANDS_MAP[command]}: {AlertCategory.CATEGORIES_MAP[category]}')

	category_id = command_id = None

	alert = AlertNotificationServer(
		device_name=ALERT_SERVER_LOCAL_NAME,
		control_point_cb=control_point_cb
	)

	tasks = Dispatcher()
	tasks.add_work(task_response_control_point, 20)
	tasks.add_work(task_send_alert, 2000)

	categories_new_alert    = set()
	categories_unread_alert = set()

	for _ in range(5):
		categories_new_alert.add(random.choice(list(AlertCategory.CATEGORIES)))
		categories_unread_alert.add(random.choice(list(AlertCategory.CATEGORIES)))

	printf('Supported New Alert Categoy:')
	for category_id in categories_new_alert:
		alert.enable_new_alert(category_id)
		printf(f'- {AlertCategory.CATEGORIES_MAP[category_id]}')

	printf('Supported Unread Alert Status Categoy:')
	for category_id in categories_unread_alert:
		alert.enable_unread_alert_status(category_id)
		printf(f'- {AlertCategory.CATEGORIES_MAP[category_id]}')

def run_alert_client_test():
	from devices.alert.alert_client import AlertNotificationClient

	def task_send_command():
		category = random.choice(list(AlertCategory.CATEGORIES))
		command  = random.choice(list(AlertCommand.COMMANDS))
		alert_client.send_command(category, command)

	def request_alert_category_cb(new_alert_category: int, unread_alert_category: int):
		printf('Supported New Alert Categoy:')
		for category_id, status in enumerate(new_alert_category, start=0):
			if status:
				printf(f'- {AlertCategory.CATEGORIES_MAP[category_id]}')

		printf('Supported Unread Alert Status Categoy:')
		for category_id, status in enumerate(unread_alert_category, start=0):
			if status:
				printf(f'- {AlertCategory.CATEGORIES_MAP[category_id]}')

	def unread_alert_status_cb(category_id: int, count: int):
		printf(f'Unread Alert Status: {AlertCategory.CATEGORIES_MAP[category_id]} ({count})')

	def new_alert_cb(category_id: int, number: int, text: str = ''):
		printf(f'New Alert: {AlertCategory.CATEGORIES_MAP[category_id]} ({number}) | {text}')

	def found_target_cb():
		tasks.add_work(task_send_command, 3000)

	tasks = Dispatcher()

	alert_client = AlertNotificationClient(
		target_name=ALERT_SERVER_LOCAL_NAME,
		found_target_cb=found_target_cb,
		new_alert_cb=new_alert_cb,
		unread_alert_status_cb=unread_alert_status_cb,
		request_alert_category_cb=request_alert_category_cb
	)
	alert_client.scan(0)


if __name__ == '__main__':
	options = [
		'Alert Notification Server',
		'Alert Notification Client',
	]

	mode = Utilities.choose_an_option('Alert Notification Test Mode', options)

	if mode is not None:
		if mode == MODE_ALERT_SERVER:
			run_alert_server_test()
		else:
			run_alert_client_test()
