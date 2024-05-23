# 从头开始学习：如何根据规范文件编写设备代码

## 名词解释

开始之前先简单了解一下蓝牙规范中的一些名词。

<div class="grid cards" markdown>

- 

	=== "UUID"

		UUID 全称：Universally Unique Identifier，即通用唯一识别码。

		它的标准型式包含 32 个十六进制数，以连字号分为五段，形式为`8-4-4-4-12`的 32 个字符，如：9c80ace6-a25e-42c3-9ff4-fb43426c41dd。

		UUID 有 16bit 的，或者 128bit 的。 16bit 的 UUID 是官方通过认证的，需要花钱购买，128bit 是自定义的，这个就可以自己随便设置。

	=== "Profile (配置文件)"

		**配置文件**并不是实际存在于蓝牙设备上的，它只是一个被 Bluetooth SIG 预先定义的**服务**的集合。例如 Heart Rate Profile 就是结合了 Heart Rate 和 Device Information 两个**服务**。

	=== "Service (服务)"

		**服务**把数据分成一个个的独立逻辑项，它包含一个或者多个**特征**。每个**服务**都有一个 UUID。

	=== "Characteristic (特征)"

		**特征**是最小的逻辑数据单元。与**服务**类似，每个**特征**也有一个 UUID。

		你可以使用 Bluetooth SIG 官方定义的标准**特征**，这样可以确保软件和硬件能相互理解。

		实际上，和蓝牙外设打交道的主要使用的是**特征**，你可以通过它读写数据，这样就实现了双向通信。

	=== "Descriptor (描述符)"

		暂无。

	=== "蓝牙设备"

		本文中蓝牙设备指的是可以实现**配置文件**中指定的功能，并且可以和其它蓝牙设备进行通信的设备。

		软件方面，蓝牙设备主要包括以下两个部分：

		* **配置文件**类模块：

			* **配置文件**类：包含**服务**和**特征**集合的类模块，它定义了设备应该具备的功能

			* **特征值**类：用于设置和获取**特征值**的数据

		* **设备代码**类模块：包含**服务**和**特征**的实现代码，提供设备广播和数据交换等功能

</div>

## 网页和文档

提前打开下列网页和文档，方便后续查阅。

* [Specifications and Documents](https://www.bluetooth.com/specifications/specs/) 网站：用于查找官方定义好的**配置文件**

* [Assigned Numbers](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/Assigned_Numbers.pdf?v=1715845995958)：用于查找**服务**、**特征**和**描述符**的 UUID ，以及所有定义好的常量值

* [GATT Specification Supplement](https://btprodspecificationrefs.blob.core.windows.net/gatt-specification-supplement/GATT_Specification_Supplement.pdf)：用于查找**特征值**的数据类型

## 编写配置文件类 (CTSProfile)

我们以 Current Time Service (CTS) 为例开始编写代码。

!!! tip "提示"
	在开始之前我们需要在`/ble/profiles`目录下新建`cts.py`文件，并导入必要的模块。

??? quote "View Code"

	```py linenums="1" title="/profiles/cts.py"
	from micropython import const
	from struct import pack
	from bluetooth import UUID
	from time import localtime
	from ble import *
	```

### 1. 下载配置文件文档

在 Specifications and Documents 网站搜索`CTS`，点开链接下载 [Current Time Service v1.1](https://www.bluetooth.org/docman/handlers/downloaddoc.ashx?doc_id=292957) 文档。

### 2. 查找服务包含的特征

在文档第 9 页 Service Characteristics 章节中，可以看到 CTS **服务**包含的**特征**，如下表所示：

| 特征 | 必选 / 可选 |
| :- | :-: |
| Current Time | 必选 |
| Local Time Information | 可选 |
| Reference Time Information | 可选 |

!!! tip "提示"
	CTS **服务**不添加可选**特征**也可以正常使用，这里我们选择添加前两个**特征**。

到这里需要先暂停一下，等收集完必要的 UUID 之后再继续。

### 3. 查找服务和特征的 UUID

在 Assigned Numbers 文档中找到以下内容并记录它们的 UUID：

* Current Time Service @page_66
* Current Time @page_85
* Local Time Information @page_89

??? quote "View Code"

	```py linenums="1" title="/profiles/cts.py"
	UUID_CURRENT_TIME_SERVICE = const(0x1805)
	UUID_CURRENT_TIME = const(0x2A2B)
	UUID_LOCAL_TIME_INFORMATION = const(0x2A0F)
	```

### 4. 编写服务和特征类

返回刚刚暂停的文档处，继续查看各个**特征**的**属性**，如下表所示：

| 特征 | 读 | 写 | 通知 |
| :- | :-: | :-: | :-: |
| Current Time | 必选 | 可选 | 必选|
| Local Time Information | 必选 | 可选 | 无关 |

根据以上获取到的信息就可以开始编写 CTS Profile 所需的**服务**和**特征**类了。需要注意的是，这里只给**特征**添加了必选**属性**。

??? quote "View Code"

	```py linenums="1" title="/profiles/cts.py"
	# Service
	class CurrentTimeService(Service):
		def __init__(self):
			super().__init__(UUID(UUID_CURRENT_TIME_SERVICE))

	# Characteristics
	class CurrentTime(Characteristic):
		def __init__(self):
			super().__init__(UUID(UUID_CURRENT_TIME), Flag.READ_NOTIFY)

	class LocalTimeInformation(Characteristic):
		def __init__(self):
			super().__init__(UUID(UUID_LOCAL_TIME_INFORMATION), Flag.READ)
	```

### 5. 编写配置文件类

??? quote "View Code"

	```py linenums="1" title="/profiles/cts.py"
	class CTSProfile(Profile):
		def __dir__(self):
			return [attr for attr in dir(type(self)) if not attr.startswith('_')]

		def __init__(self):
			super().__init__()
			self.__make_profile()

		def __make_profile(self):
			self.add_services(
				CurrentTimeService().add_characteristics(
					CurrentTime(),
					LocalTimeInformation(),
				),
			)
	```

在`__make_profile()`函数中，我们可以使用较为直观的方式添加**配置文件**的**服务**和**特征**。

## 编写特征值类 (CTSValues)

**特征值**类用于设置**特征**的值并返回符合要求的字节数据。

在开始之前我们需要在`cts.py`文件中增加 CTSValues 类定义。

??? quote "View Code"

	```py linenums="1" title="/profiles/cts.py"
	class CTSValues(object):
		def __init__(self):
			self.current_time_service = self.CurrentTimeService()

		class CurrentTimeService(object):
			def __dir__(self):
				return [attr for attr in dir(type(self)) if not attr.startswith('_')]
	```

在 GATT Specification Supplement 文档中找到**特征值**说明，并记录它们的数据格式，包括字段名称、数据类型和数据大小等。

### 1. 编写 Current Time 特征值代码

<div class="grid cards" markdown>

- 

	=== "Current Time @page_74"

		| 字段 | 数据类型 | 大小 | 内容描述 |
		| :- | :-: | :-: | :- |
		| Exact Time 256 | struct | 9 |  参考 Exact Time 256 **特征**。 |
		| Adjust Reason | boolean[8] | 1 | 此字段表示调整时间的原因：<br><br>0：手动时间更新<br>1：外部参考时间更新<br>2：时区变更<br>3：夏令时变更<br>4–7：保留以备将来使用 |

		* Exact Time 256 字段是一个结构体，需要参考 Exact Time 256 **特征**的数据格式，暂时跳过。

		* Adjust Reason 字段是一个布尔数组，列出了 4 种调整原因，要将它们作为常量进行记录，并增加类属性代码。

			??? quote "View Code"

				```py linenums="1" title="/profiles/cts.py"
				class CurrentTimeService(object):
					ADJUST_REASON_MANUAL   = 0b0001
					ADJUST_REASON_EXTERNAL = 0b0010
					ADJUST_REASON_TIMEZONE = 0b0100
					ADJUST_REASON_DST      = 0b1000
					ADJUST_REASONS = (
						ADJUST_REASON_MANUAL,
						ADJUST_REASON_EXTERNAL,
						ADJUST_REASON_TIMEZONE,
						ADJUST_REASON_DST,
					)

					def __init__(self):
						self.__adjust_reason = self.ADJUST_REASON_MANUAL

					@property
					def adjust_reason(self) -> int:
						return self.__adjust_reason

					@adjust_reason.setter
					def adjust_reason(self, value: int):
						if isinstance(value, int) and value in self.ADJUST_REASONS:
							self.__adjust_reason = value
				```

		继续查看 Exact Time 256 **特征值**说明。

	=== "Exact Time 256 @page_100"

		| 字段 | 数据类型 | 大小 | 内容描述 |
		| :- | :-: | :-: | :- |
		| Day Date Time | struct | 8 | 参考 Day Date Time **特征**。 |
		| Fractions256 | uint8 | 1 | 1/256 秒的分数，有效范围 0–255。 |

		!!! question "Fractions256"
			个人理解这个字段表示当前时间的毫秒数，为了节省空间所以采用 1/256 计数。

			假设当前时间毫秒数为 900，那么对应 Fractions256 的值应为 900 / 1000 * 255，取整为 229。

		* Day Date Time 字段需要参考 Day Date Time **特征**的数据格式，暂时跳过。
		* Fractions256 字段取值范围 0~255，给它增加类属性代码。

			??? quote "View Code"

				```py linenums="1" title="/profiles/cts.py"
				class CurrentTimeService(object):
					def __init__(self):
						self.__fractions256  = 0

					@property
					def fractions256(self) -> int:
						return self.__fractions256

					@fractions256.setter
					def fractions256(self, value: int):
						if isinstance(value, int) and 0 <= value <= 1000:
							self.__fractions256 = int(value / 1000 * 255)
				```

		继续查看 Day Date Time **特征值**说明。

	=== "Day Date Time @page_88"

		| 字段 | 数据类型 | 大小 | 内容描述 |
		| :- | :-: | :-: | :- |
		| Date Time | struct | 7 | 参考 Date Time **特征**。 |
		| Day of Week | struct | 1 | 参考 Day of Week **特征**。 |

		Day Date Time **特征**的两个字段都是结构体，直接查看它们的**特征值**说明。

	=== "Date Time @page_87"

		| 字段 | 数据类型 | 大小 | 内容描述 |
		| :- | :-: | :-: | :- |
		| Year | uint16 | 2 | 公历年份，有效范围 1582 到 9999，0 表示年份未知。 |
		| Month | uint8 | 1 | 公历年份中的某一月份，有效范围 1（月）到 12（月），0 表示月份未知。 |
		| Day | uint8 | 1 | 公历月份中的某一天，有效范围 1 到 31，0 表示日期未知。 |
		| Hours | uint8 | 1 | 午夜过后的小时数，有效范围 0 到 23。 |
		| Minutes | uint8 | 1 | 自整点开始以来的分钟数，有效范围 0 到 59。 |
		| Seconds | uint8 | 1 | 自分钟开始以来的秒数，有效范围 0 到 59。 |

	=== "Day of Week @page_89"

		| 字段 | 数据类型 | 大小 | 内容描述 |
		| :- | :-: | :-: | :- |
		| Day of Week | uint8 | 1 | 0：未知<br>1：星期一<br>2：星期二<br>3：星期三<br>4：星期四<br>5：星期五<br>6：星期六<br>7：星期日<br>8–255：保留以备将来使用 |

		Date Time 和 Day of Week **特征值**所有字段的值都可以使用`time.localtime()`获取。

</div>

至此我们已经得到 Current Time **特征**全部的**特征值**。

根据上述**特征值**信息可以得到如下分解公式：

| | | | | | | | | | | | | | | | | | | |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Current Time | = | Exact Time 256 | + | Adjust Reason |
| | = | Day Date Time | + | Fractions256 | + | Adjust Reason |
| | = | Date Time | + | Day of Week | + | Fractions256 | + | Adjust Reason |
| | = | Year | + | Month | + | Day | + | Hours | + | Minutes | + | Seconds | + | Day of Week | + | Fractions256 | + | Adjust Reason |

整理后得到数组示意表格：

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Year | Year | Month | Day | Hours | Minutes | Seconds | Day of Week | Fractions256 | Adjust Reason |

根据表格内容增加类属性代码。

??? quote "View Code"

	```py linenums="1" title="/profiles/cts.py"
	class CurrentTimeService(object):
		@property
		def current_time(self) -> bytes:
			datetime = list(localtime())
			datetime[6] += 1 # week of day
			return pack('<H8B', *datetime[:7], self.__fractions256, self.__adjust_reason)
	```

### 2. 编写 Local Time Information 特征值代码

有了上面编写 Current Time **特征值**代码的经验，下面都是大同小异，也就一带而过了。

<div class="grid cards" markdown>

- 

	=== "Local Time Information @page_132"

		| 字段 | 数据类型 | 大小 | 内容描述 |
		| :- | :-: | :-: | :- |
		| Time Zone | struct | 1 | 参考 Time Zone **特征**。 |
		| DST Offset | struct | 1 | 参考 DST Offset **特征**。 |

	=== "Time Zone @page_182"

		| 字段 | 数据类型 | 大小 | 内容描述 |
		| :- | :-: | :-: | :- |
		| Time Zone | sint8 | 1 | 此字段表示与 UTC 的偏移量，以 15 分钟为增量，有效范围从 -48 到 +56，-128 表示时区偏移量未知。<br>无论夏令时是否生效，此特性中定义的偏移量都是恒定的。 |

		!!! info "UTC 偏移量"
			-48 表示：UTC-12:00

			+56 表示：UTC+14:00

		为 Time Zone 字段增加类属性代码。

		??? quote "View Code"

			```py linenums="1" title="/profiles/cts.py"
			class CurrentTimeService(object):
				def __init__(self):
					self.__time_zone = 8 * 4 # UTC+8

				@property
				def time_zone(self) -> int:
					return self.__time_zone

				@time_zone.setter
				def time_zone(self, value: int):
					if isinstance(value, int) and -48 <= value <= 56:
						self.__time_zone = value
			```

	=== "DST Offset @page_91"

		| 字段 | 数据类型 | 大小 | 内容描述 |
		| :- | :-: | :-: | :- |
		| DST Offset | uint8 | 1 | 0：标准时间<br>2：半小时夏令时（+0.5h）<br>4：夏令时（+1h）<br>8：双夏令时（+2h）<br>255：DST 偏移未知<br>其它：保留以备将来使用 |

		为 DST Offset 字段增加类常量和类属性代码。

		??? quote "View Code"

			```py linenums="1" title="/profiles/cts.py"
			class CurrentTimeService(object):
				DST_OFFSET_STANDARD       = 0
				DST_OFFSET_HALF_DAYLIGHT  = 2 # (+ 0.5h)
				DST_OFFSET_DAYLIGHT       = 4 # (+ 1h)
				DST_OFFSET_DOUBLEDAYLIGHT = 8 # (+ 2h)
				DST_OFFSETS = (
					DST_OFFSET_STANDARD,
					DST_OFFSET_HALF_DAYLIGHT,
					DST_OFFSET_DAYLIGHT,
					DST_OFFSET_DOUBLEDAYLIGHT,
				)

				def __init__(self):
					self.__dst_offset = self.DST_OFFSET_STANDARD

				@property
				def dst_offset(self) -> int:
					return self.__dst_offset

				@dst_offset.setter
				def dst_offset(self, value: int):
					if isinstance(value, int) and value in self.DST_OFFSETS:
						self.__dst_offset = value
			```

</div>

至此我们已经得到 Local Time Information **特征**全部的**特征值**，为其增加类属性代码。

??? quote "View Code"

	```py linenums="1" title="/profiles/cts.py"
	class CurrentTimeService(object):
		@property
		def local_time_information(self) -> bytes:
			return pack('<bB', self.__time_zone, self.__dst_offset)
	```

## 编写设备类 (CTSServer)

!!! tip "提示"
	在开始之前我们需要在`/devices/cts`目录下新建`ctsserver.py`文件。

编写 CTS Server 设备类，大致分为以下几个步骤，每一步中只给出关键示例（伪）代码。

### 1. 导入 CTSProfile 及相关模块

??? quote "View Code"

	```py linenums="1" title="/devices/cts/ctsserver.py"
	import bluetooth
	from ble import *
	from ble.profiles.cts import CTSProfile, CTSValues
	```

### 2. 生成 CTSProfile 实例

新建一个 CTSServer 类，在其中初始化蓝牙 BLE 外设，并实例化 CTSProfile 和 CTSValues 类。

??? quote "View Code"

	```py linenums="1" title="/devices/cts/ctsserver.py"
	class CTSServer(object):
		def __init__(self, device_name):
			self.__ble        = bluetooth.BLE()
			self.__cts_values = CTSValues()

			cts_profile = CTSProfile()
			appearance  = 256 # (0x004, 0x00)
	```

### 3. 注册服务，初始化特征值

注册**服务**并获取**特征**操作句柄。

??? quote "View Code"

	```py linenums="1" title="/devices/cts/ctsserver.py"
	(
		(
			self.__handle_current_time,
			self.__handle_local_time_information,
		),
	) = self.__ble.gatts_register_services(cts_profile.get_services())

	self.__cts_values.current_time_service.adjust_reason = self.__cts_values.current_time_service.ADJUST_REASON_MANUAL
	self.__cts_values.current_time_service.fractions256  = 0
	self.__cts_values.current_time_service.time_zone     = 8 * 4 # UTC+8
	self.__cts_values.current_time_service.dst_offset    = self.__cts_values.current_time_service.DST_OFFSET_STANDARD

	self.__write(self.__handle_current_time,           self.__cts_values.current_time_service.current_time)
	self.__write(self.__handle_local_time_information, self.__cts_values.current_time_service.local_time_information)
	```

### 4. 生成广播数据并启动广播

??? quote "View Code"

	```py linenums="1" title="/devices/cts/ctsserver.py"
	adv_payload = BLETools.generate_advertising_payload(
		cts_profile.get_services_uuid(),
		appearance=appearance
	)

	resp_payload = BLETools.generate_advertising_payload(
		name=device_name
	)

	self.__ble.gap_advertise(100000, adv_data=adv_payload, resp_data=resp_payload)
	```

### 5. 监听中心设备读取请求

一旦有中心设备成功连接，就可以读取 CTS Server 的日期时间等数据，需要在读取请求回调中进行响应处理。

??? quote "View Code"

	```py linenums="1" title="/devices/cts/ctsserver.py"
	if event == IRQ.GATTS_READ_REQUEST:
		conn_handle, attr_handle = data

		printf(f'GATTS Read Request [Handle: {conn_handle}, Attr_Handle: {attr_handle}]')

		if attr_handle == self.__handle_current_time:
			self.__cts_values.current_time_service.fractions256 = 0
			self.__write(attr_handle, self.__cts_values.current_time_service.current_time)
		elif attr_handle == self.__handle_local_time_information:
			self.__write(attr_handle, self.__cts_values.current_time_service.local_time_information)

		return GATTSErrorCode.NO_ERROR
	```

## 获取完整代码

* cts.py (CTSProfile, CTSValues)：[gitee](https://gitee.com/walkline/micropython-new-ble-library/blob/main/ble/profiles/cts.py) | [github](https://github.com/Walkline80/micropython-new-ble-library/blob/main/ble/profiles/cts.py)

* ctsserver.py (CTSServer)：[gitee](https://gitee.com/walkline/micropython-new-ble-library/blob/main/devices/cts/ctsserver.py) | [github](https://github.com/Walkline80/micropython-new-ble-library/blob/main/devices/cts/ctsserver.py)

* test_cts.py (Server, Client)：[gitee](https://gitee.com/walkline/micropython-new-ble-library/blob/main/tests/test_cts.py) | [github](https://github.com/Walkline80/micropython-new-ble-library/blob/main/tests/test_cts.py)

## 附录1：特征值数据类型和大小

* 数据大小单位是 Octet，即 8 位字节。

* 数据类型：

	| 数据类型 | 大小 | 说明 |
	| :- | :-: | :- |
	| struct | 不定 | 表示一个可变长度的字节数组，其长度和内部格式与值单独指定。 |
	| boolean[8] | 1 | 表示一个由 8 个布尔值组成的数组。 |
	| uint8 | 1 | 表示一个 8 位无符号整数。 |
	| sint8 | 1 | 表示一个 8 位有符号整数。 |

## 附录2：参考内容

* [蓝牙BLE: GATT Profile 简介(GATT 与 GAP) ](https://www.cnblogs.com/yongdaimi/p/11507397.html)

* [小科普：通用唯一标识码UUID的介绍及使用](https://zhuanlan.zhihu.com/p/438580928)

*  [time.localtime()](https://docs.micropython.org/en/latest/library/time.html#time.localtime)

* [Where is BLE Current Time Service Data format?](https://iot.stackexchange.com/questions/7885/where-is-ble-current-time-service-data-format)

* [Octet 和 Byte 的区别](https://blog.csdn.net/u010931294/article/details/37690071)

* [Python基础教程— Struct模块](https://blog.csdn.net/qdPython/article/details/115550281)
