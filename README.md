<h1 align="center">MicroPython BLE HID 控制器</h1>

<p align="center"><img src="https://img.shields.io/badge/Licence-MIT-green.svg?style=for-the-badge" /></p>

## 项目介绍

## 测试方法

### 键盘测试

使用`ab 工具`上传键盘所需文件，然后运行`tests/test_keyboard.py`文件

```bash
# 上传文件
$ ab abconfig_kbd104

# 进入交互模式
$ ab --repl

# 运行测试脚本
# ctrl + r，输入 test\test_keyboard.py 前边的序号并回车
```

之后使用电脑或手机正常搜索连接键盘，连接成功后使用开发板上的`BOOT`按键模拟键盘按键操作即可。

> 默认设备名称：`MP_KB104`

也可以自行修改`tests/test_keyboard.py`文件对应内容以修改按键引脚。

## 参考资料

* `ab 工具`安装及使用说明请访问 [AMPY Batch Tool](https://gitee.com/walkline/a-batch-tool) 查看

## 合作交流

* 联系邮箱：<walkline@163.com>
* QQ 交流群：
	* 走线物联：[163271910](https://jq.qq.com/?_wv=1027&k=xtPoHgwL)
	* 扇贝物联：[31324057](https://jq.qq.com/?_wv=1027&k=yp4FrpWh)

<p align="center"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_walkline.png" width="300px" alt="走线物联"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_bigiot.png" width="300px" alt="扇贝物联"></p>
