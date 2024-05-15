"""
Copyright © 2024 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-ble-hid-controller
"""
from .consts import *
from . import bluetooth


UUID = bluetooth.UUID


# region Base Classes
class Profile(object):
	def __init__(self):
		self.__services = []

	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def add_services(self, *services):
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
		return [service.get_service() for service in self.__services]

	def get_services_uuid(self) -> list:
		return [service.__uuid for service in self.__services]

class Service(object):
	def __init__(self, uuid):
		self.__uuid = uuid
		self.__characteristics = []

	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def add_characteristics(self, *characteristics):
		for characteristic in characteristics:
			self.__characteristics.append(characteristic)
		return self

	def get_service(self) -> list:
		return [self.__uuid, [char.get_characteristic() for char in self.__characteristics]]

class Characteristic(object):
	def __init__(self, uuid, flags):
		self.__descriptors = []
		self.__uuid = uuid
		self.__flags = flags

	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def add_descriptors(self, *descriptors):
		for descriptor in descriptors:
			self.__descriptors.append(descriptor)
		return self

	def get_characteristic(self) -> list:
		if self.__descriptors:
			return [self.__uuid, self.__flags, [descriptor.get_descriptor() for descriptor in self.__descriptors]]
		else:
			return [self.__uuid, self.__flags]

class Descriptor(object):
	def __init__(self, uuid, flags):
		self.__uuid = uuid
		self.__flags = flags

	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def get_descriptor(self) -> list:
		return [self.__uuid, self.__flags]
# endregion Base Classes


class GenericProfile(Profile):
	'''只包含蓝牙必须的两个服务'''
	def __init__(self):
		super().__init__()

		self.__make_profile()

	def __dir__(self):
		return [attr for attr in dir(type(self)) if not attr.startswith('_')]

	def __make_profile(self):
		self.add_services(
			GenericAccess().add_characteristics(
				DeviceName(),
				Appearance(),
				PeripheralPreferredConnectionParameters(),
			),
			GenericAttribute().add_characteristics(
				ServiceChanged(),
			),
		)


# region Services
class GenericAccess(Service):
	def __init__(self):
		super().__init__(UUID(UUIDS.GENERIC_ACCESS))

class GenericAttribute(Service):
	def __init__(self):
		super().__init__(UUID(UUIDS.GENERIC_ATTRIBUTE))
# endregion Services


# region Characteristics

# region GenericAccess's Characteristics
class DeviceName(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.DEVICE_NAME), Flag.READ_WRITE)

class Appearance(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.APPEARANCE), Flag.READ)

class PeripheralPreferredConnectionParameters(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.PERIPHERAL_PREFERRED_CONNECTION_PARAMETERS), Flag.READ)
# endregion GenericAccess's Characteristics


# region GenericAttribute's Characteristics
class ServiceChanged(Characteristic):
	def __init__(self):
		super().__init__(UUID(UUIDS.SERVICE_CHANGED), Flag.INDICATE)
# endregion GenericAttribute's Characteristics

# endregion Characteristics


# region Descriptors

# region Report Characteristic's Descriptors
class ReportReference(Descriptor):
	def __init__(self):
		Descriptor.__init__(self, UUID(UUIDS.REPORT_REFERENCE), Flag.READ_WRITE | Flag.WRITE_NO_RESPONSE)
# endregion

# endregion
