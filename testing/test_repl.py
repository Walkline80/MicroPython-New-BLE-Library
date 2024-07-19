"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import devices.uart.blerepl as blerepl


def run_blerepl_test():
	print('Using ViperIDE (https://viper-ide.org/) connect to device via BLEREPL.')

	blerepl.start()


if __name__ == '__main__':
	run_blerepl_test()
