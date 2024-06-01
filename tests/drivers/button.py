"""
The MIT License (MIT)
Copyright © 2022 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-drivers

# IMPORTANT: THIS MODULE ONLY TESTED ON ESP32 & ESP32C3 BOARD
"""
__version__ = 'v1.2'

from machine import Pin, Timer
from utime import ticks_ms


class ButtonException(BaseException):
	pass


class Button(object):
	"""
	- 自定义按钮
	
	支持点击和长按两种模式，按键电路适配默认高电平或低电平

	长按模式分为：
	    1. 长按超时触发
	    2. 长按超时松开触发
	
	参数：
	    pin:		GPIO 引脚，可使用列表或元组批量添加
		hold_cb:	按键按下回调函数
		release_cb:	按键释放回调函数
	    click_cb:	单击事件回调函数
	    press_cb:	长按事件回调函数
	    timeout:	长按触发超时时间（ms）
		default:	按键未按下时状态，高电平或低电平
		behavior:	长按触发模式选择
	"""

	# __BUTTON_RESPONSE_INTERVAL = 20 # 目前使用定时器实现按钮点击并不需要消除抖动

	# low when button not pressed
	DEFAULT_LOW = 0

	# high when button not pressed
	DEFAULT_HIGH = 1

	# trigger long press while holding button
	BEHAVIOR_HOLD = 0

	# trigger long press after release button
	BEHAVIOR_RELEASE = 1

	def __init__(self, pin=None, hold_cb=None, release_cb=None, click_cb=None, press_cb=None,
				 timeout=3000,
				 default=DEFAULT_HIGH,
				 behavior=BEHAVIOR_HOLD,
				 timer_id=10):
		assert pin is not None, ButtonException('pin must be specified')
		assert hold_cb is not None or \
			   release_cb is not None or\
			   click_cb is not None or\
			   press_cb is not None, ButtonException('at least set one event callback')

		self.button_list = []
		self.__pin_list = []
		self.__button_holding_list = []
		self.__button_status_list = []
		self.__is_button_holding_list = []
		self.__button_pressed_list = []
		self.__last_ticks_list = []

		self.__default = default

		if isinstance(pin, (list, tuple)):
			for _ in pin:
				self.button_list.append(Pin(_, Pin.IN, Pin.PULL_UP if self.__default else Pin.PULL_DOWN))
				self.__pin_list.append(_)
				self.__button_holding_list.append(False)	# true: holding, false: releasing
				self.__button_status_list.append(False)		# true: holded, false: released
				self.__button_pressed_list.append(False)	# true: pressed once, false: never pressed
				self.__is_button_holding_list.append(False)	# true: holded, false: released
				self.__last_ticks_list.append(ticks_ms())
		else:
			self.button_list.append(Pin(pin, Pin.IN, Pin.PULL_UP if self.__default else Pin.PULL_DOWN))
			self.__pin_list.append(pin)
			self.__button_holding_list.append(False)
			self.__button_status_list.append(False)
			self.__button_pressed_list.append(False)
			self.__is_button_holding_list.append(False)
			self.__last_ticks_list.append(ticks_ms())

		self.__click_cb = click_cb		# button clicked callback
		self.__press_cb = press_cb		# button pressed callback
		self.__hold_cb = hold_cb		# button holding callback
		self.__release_cb = release_cb	# button released callback
		self.__timeout = timeout		# press callback acting if timed out
		self.__behavior = behavior

		if timer_id is not None:
			self.__timer = Timer(timer_id)

			self.__timer.init(
				mode=Timer.PERIODIC,
				period=20,
				callback=self.timer_callback
			)

	def deinit(self):
		for _ in self.button_list:
			_ = None

		if self.__timer is not None:
			self.__timer.deinit()
			self.__timer = None

	def add_button(self, pin):
		self.button_list.append(Pin(pin, Pin.IN, Pin.PULL_UP if self.__default else Pin.PULL_DOWN))
		self.__pin_list.append(pin)
		self.__button_holding_list.append(False)
		self.__button_status_list.append(False)
		self.__button_pressed_list.append(False)
		self.__is_button_holding_list.append(False)
		self.__last_ticks_list.append(ticks_ms())

	def __time_diff(self, index):
		return ticks_ms() - self.__last_ticks_list[index]

	def timer_callback(self, timer=None):
		for index in range(len(self.button_list)):
			self.__button_holding_list[index] = abs(self.__default - self.button_list[index].value())
			# print("hold" if self.__button_holding_list[index] else "release")

			if self.__button_holding_list[index]:
				if self.__hold_cb is not None and not self.__is_button_holding_list[index]:
					self.__hold_cb(self.__pin_list[index])
					self.__is_button_holding_list[index] = True
			else:
				if self.__release_cb is not None and self.__is_button_holding_list[index]:
					self.__release_cb(self.__pin_list[index])
					self.__is_button_holding_list[index] = False

			if self.__button_holding_list[index]:
				if self.__button_status_list[index] == self.__button_holding_list[index]:
					if self.__time_diff(index) >= self.__timeout and self.__behavior == self.BEHAVIOR_HOLD:
						if self.__press_cb is not None:
							self.__press_cb(self.__time_diff(index), self.__pin_list[index])

						self.__button_status_list[index] = False
						self.__button_pressed_list[index] = True

						self.__last_ticks_list[index] = ticks_ms()
				else:
					if not self.__button_pressed_list[index]:
						self.__button_status_list[index] = True
			else:
				if self.__button_status_list[index]:
					if self.__time_diff(index) >= self.__timeout and self.__behavior == self.BEHAVIOR_RELEASE:
						if self.__press_cb is not None:
							self.__press_cb(self.__time_diff(index), self.__pin_list[index])
					else:
						if self.__click_cb is not None:
							self.__click_cb(self.__pin_list[index])

					self.__button_status_list[index] = False
				else:
					self.__last_ticks_list[index] = ticks_ms()
					self.__button_pressed_list[index] = False

	@property
	def timeout(self):
		return self.__timeout

	@timeout.setter
	def timeout(self, value):
		if isinstance(value, int):
			self.__timeout = value


__press_counts = 0
__led = None

def run_test():
	global __led

	__led = Pin(2, Pin.OUT, value=0)

	from utime import sleep_ms
	import urandom

	def button_hold_cb(pin):
		global __led

		__led.value(not __led.value())
		print(f'button {pin} holding')

	def button_release_cb(pin):
		global __led

		__led.value(not __led.value())
		print(f'button {pin} released')

	def button_click_cb(pin):
		print(f'button {pin} clicked {urandom.randint(0, 65535)}')

	def button_press_cb(duration, pin):
		global __press_counts

		__press_counts += 1
		print(f'button {pin} pressed over {duration} ms')

	button = Button(
		pin=[0, 5],
		hold_cb=button_hold_cb,
		release_cb=button_release_cb,
		click_cb=button_click_cb,
		press_cb=button_press_cb,
		timeout=3000,
		behavior=Button.BEHAVIOR_HOLD
	)

	print(
f'''
==========================================
       Running button test unit

  Supports:
      1. click
      2. long press (over {button.timeout} ms)

  Tips:
      Try to click the BOOT button
      Take long press third times to end
==========================================
''')

	while __press_counts < 3:
		sleep_ms(500)

	button.deinit()
	__led.value(0)

	print(
"""
==========================
    Unit test complete
==========================
"""
	)


if __name__ == "__main__":
	try:
		run_test()
	except KeyboardInterrupt:
		pass
