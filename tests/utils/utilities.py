"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
class Utilities(object):
	@staticmethod
	def choose_an_option(title, options):
		print(f'\n{title}:')

		for index, option in enumerate(options, start=1):
			if index == 1:
				print(f'\x1b[32m  [{index}] {option}\033[0m')
			else:
				print(f'  [{index}] {option}')

		selected = None

		while True:
			try:
				selected = input('Choose an option: ')

				if selected == '':
					return 0

				selected = int(selected)

				assert type(selected) is int and 0 < selected <= len(options)

				return selected - 1
			except KeyboardInterrupt:
				return
			except:
				pass
