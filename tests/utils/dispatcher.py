"""
Copyright © 2022 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-timer-dispatcher
"""
__version__ = 'v1.1'
__version_info__ = (1, 1)

from machine import Timer


class Worker(object):
	'''定时器任务'''
	def __init__(self, work:function, period:int, *params):
		self.__counter = 0
		self.__work = work
		self.__period = period
		self.__params = params

	@property
	def counter(self):
		return self.__counter
	
	@counter.setter
	def counter(self, count):
		self.__counter = count

	@property
	def period(self):
		return self.__period

	def do_work(self):
		self.__work(*self.__params)


class Dispatcher(object):
	'''定时器任务调度器'''
	__DEFAULT_PERIOD = 20

	def __init__(self, adjusting_rate=1, timer_id=0):
		'''
		初始化任务调度器

		参数：
		- adjusting_rate：时间间隔调整倍率，默认值 1。
		- timer_id：定时器 ID，默认值 0。
		'''
		if not isinstance(adjusting_rate, int) or adjusting_rate < 1:
			adjusting_rate = 1

		if not isinstance(timer_id, int):
			timer_id = 0

		self.__workers = {}
		self.__timer = Timer(timer_id)
		self.__adjusting_rate = adjusting_rate
		self.__paused = False

		self.__timer.init(
			mode=Timer.PERIODIC,
			period=Dispatcher.__DEFAULT_PERIOD,
			callback=self.__worker_callback
		)

	def deinit(self):
		self.__timer.deinit()
		self.__workers = {}

	def __worker_callback(self, _):
		if self.__paused: return

		for worker in self.__workers.values():
			if self.__paused: break

			worker.counter += 1

			if (worker.counter * Dispatcher.__DEFAULT_PERIOD * self.__adjusting_rate) % worker.period == 0:
				worker.counter = 0
				worker.do_work()

	def add_work(self, work:function, period:int, *params) -> bool:
		'''
		添加/更新一个调度任务

		参数：
		- work：任务函数
		- period：任务执行间隔，单位 毫秒
		- params：任务函数参数列表
		'''
		result = False

		if callable(work):
			self.__workers[id(work)] = Worker(work, period, *params)
			result = True
		else:
			print('work must be a function')

		return result

	def has_work(self, work:function) -> bool:
		'''
		判断任务是否在队列中

		参数：
		- work：任务函数
		'''
		result = False

		if callable(work):
			result = True if self.__workers.get(id(work)) is not None else False

		return result

	def del_work(self, work:function=None):
		'''
		删除指定或最后添加的任务

		参数：
		- work：任务函数，默认值 None
		'''
		if work is None:
			if len(self.__workers) > 0:
				self.pause()
				self.__workers.popitem()
				self.pause()
		elif callable(work):
			if self.has_work(work):
				self.pause()
				self.__workers.pop(id(work))
				self.pause()

	def del_works(self):
		'''删除所有任务'''
		self.pause()
		self.__workers.clear()
		self.pause()

	def pause(self):
		'''暂停/开启 所有任务'''
		self.__paused = not self.__paused
	
	def is_paused(self):
		'''判断所有任务是否正在运行'''
		return self.__paused


def run_test():
	from machine import RTC

	counter = 0

	class  Test(object):
		def __init__(self):
			self.__counter = 0

		def task3(self):
			self.__counter += 1
			print(f'\t\t\ttask 3 counter: {self.__counter}')

	def task1():
		nonlocal counter
		counter = (counter + 1) % 3

		if counter == 0:
			print('')
			tasks.del_work(task2) if tasks.has_work(task2) else tasks.add_work(task2, 3000, 'task', 2)

		print(f'\x1b[32m{rtc.datetime()[4:7]} task 1 (5s)\033[0m')

	def task2(prefix:str, index:int):
		print(f'\x1b[33m{rtc.datetime()[4:7]} {prefix} {index} (3s)\033[0m')

	rtc = RTC()
	rtc.init((2000, 1, 1, 0, 0, 0, 0, 8))

	test = Test()
	task3 = lambda : test.task3()

	tasks = Dispatcher()
	tasks.add_work(task1, 5000)
	tasks.add_work(task3, 1000)


if __name__ == '__main__':
	run_test()
