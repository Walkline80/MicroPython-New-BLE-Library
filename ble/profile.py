"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-ble-library
"""
class Profile(object):
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self):
		self.__services = []

	def add_services(self, *services):
		'''添加服务'''
		for service in services:
			update = False

			for old_service in self.__services:
				if service.__uuid == old_service.__uuid:
					old_service.__characteristics += service.__characteristics
					update = True
					break

			if not update:
				self.__services.append(service)

	def get_services(self) -> list:
		'''获取配置文件的服务、特征和描述符列表'''
		return [service.get_service() for service in self.__services]

	def get_services_uuid(self) -> list:
		'''获取配置文件的服务、特征和描述符 UUID 列表'''
		return [service.__uuid for service in self.__services]


class Service(object):
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self, uuid):
		self.__uuid = uuid
		self.__characteristics = []

	def add_characteristics(self, *characteristics):
		'''添加特征'''
		for characteristic in characteristics:
			self.__characteristics.append(characteristic)
		return self

	def get_service(self) -> list:
		'''获取当前服务列表'''
		return [self.__uuid, [char.get_characteristic() for char in self.__characteristics]]


class Characteristic(object):
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self, uuid, flags):
		self.__descriptors = []
		self.__uuid = uuid
		self.__flags = flags

	def add_descriptors(self, *descriptors):
		'''添加描述符'''
		for descriptor in descriptors:
			self.__descriptors.append(descriptor)
		return self

	def get_characteristic(self) -> list:
		'''获取当前特征列表'''
		if self.__descriptors:
			return [self.__uuid, self.__flags, [descriptor.get_descriptor() for descriptor in self.__descriptors]]
		else:
			return [self.__uuid, self.__flags]


class Descriptor(object):
	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __init__(self, uuid, flags):
		self.__uuid = uuid
		self.__flags = flags

	def get_descriptor(self) -> list:
		'''获取当前描述符列表'''
		return [self.__uuid, self.__flags]
