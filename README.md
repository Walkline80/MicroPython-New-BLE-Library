<h1 align="center">MicroPython New BLE Library</h1>

<p align="center"><img src="https://img.shields.io/badge/Licence-MIT-green.svg?style=for-the-badge" /></p>

## 项目介绍

## 测试方法

	特别注意：每做一次不同类型的测试时，必须取消配对后再运行测试程序。

### 键盘测试

使用`ab 工具`上传键盘所需文件，然后运行`tests/test_keyboard.py`文件。

```bash
# 上传文件
$ ab abconfig_kbd104

# 进入交互模式
$ ab --repl

# 运行测试脚本
# ctrl + r，输入 test\test_keyboard.py 前边的序号并回车
```

使用电脑或手机搜索并连接键盘，连接成功后使用开发板上的`BOOT`按键模拟键盘按键操作即可。

> 默认设备名称：`MP_KB104`

可以自行修改`tests/test_keyboard.py`文件对应内容以修改按键引脚。

### UART 测试

使用`ab 工具`上传`UART`所需文件，然后运行`tests/test_uart.py`文件。

```bash
# 上传文件
$ ab abconfig_uart

# 进入交互模式
$ ab --repl

# 运行测试脚本
# ctrl + r，输入 test\test_uart.py 前边的序号并回车
```

* `BLE UART`测试方法：参考 [ESP32 BLE - UART](https://gitee.com/walkline/esp32-ble-uart) 说明文档中关于`nRF Connect`的操作说明

	> 默认设备名称：`ble_uart`

* `BLE Config`测试方法：参考 [MicroPython BLE 配网](https://gitee.com/walkline/micropython_ble_config) 说明文档中关于小程序的操作说明

	> 默认设备名称：`ble_config`

## 参考资料

* `ab 工具`安装及使用说明请访问 [AMPY Batch Tool](https://gitee.com/walkline/a-batch-tool) 查看

## 合作交流

* 联系邮箱：<walkline@163.com>
* QQ 交流群：
	* 走线物联：[163271910](https://jq.qq.com/?_wv=1027&k=xtPoHgwL)
	* 扇贝物联：[31324057](https://jq.qq.com/?_wv=1027&k=yp4FrpWh)

<p align="center"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_walkline.png" width="300px" alt="走线物联"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_bigiot.png" width="300px" alt="扇贝物联"></p>
