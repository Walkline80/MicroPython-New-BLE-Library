"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
import io
import os
import machine
import micropython
from ble import *
from devices.uart.bleuart import BLEUART

__all__ = ['start']


# https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_uart_repl.py

__MP_STREAM_POLL = const(3)
__MP_STREAM_POLL_RD = const(0x0001)

__timer = machine.Timer(0) if hasattr(machine, "Timer") else None

def schedule_in(handler: function, delay_ms: int):
    def __wrap(_arg):
        handler()

    if __timer:
        __timer.init(
			mode=machine.Timer.ONE_SHOT,
			period=delay_ms,
			callback=__wrap)
    else:
        micropython.schedule(__wrap, None)


class BLEREPL(io.IOBase):
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self, device_name: str = 'ble-repl'):
		self.__ble_uart = BLEUART(
			device_name=device_name,
			rx_received_cb=self.__rx_received_cb
		)
		self.__tx_buffer = bytearray()

	def __rx_received_cb(self, data):
		if hasattr(os, 'dupterm_notify'):
			os.dupterm_notify(None)

	def read(self, count: int = None):
		return self.__ble_uart.read(count)

	def readinto(self, buf):
		data = self.__ble_uart.read(len(buf))

		if not data:
			return None

		for index in range(len(data)):
			buf[index] = data[index]

		return len(data)

	def ioctl(self, op, arg):
		if op == __MP_STREAM_POLL:
			if self.__ble_uart.any():
				return __MP_STREAM_POLL_RD

		return 0

	def __flush(self):
		data = self.__tx_buffer[0:200]

		self.__tx_buffer = self.__tx_buffer[200:]
		self.__ble_uart.write(data)

		if self.__tx_buffer:
			schedule_in(self.__flush, 30)

	def write(self, buf):
		empty = not self.__tx_buffer
		self.__tx_buffer += buf

		if empty:
			schedule_in(self.__flush, 30)


def start():
	ble_repl = BLEREPL()
	os.dupterm(ble_repl)
