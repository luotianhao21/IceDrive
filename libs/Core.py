import typing
import os
import winreg
import time
import asyncio
import json
import threading
from bleak import BleakScanner, BleakClient

DEBUG = False


# 创建一个全局的、持续运行的事件循环线程
class EventLoopThread(threading.Thread):
    """在单独线程中运行一个永久的事件循环"""

    def __init__(self):
        super().__init__(daemon=True)
        self.loop: asyncio.AbstractEventLoop | None = None
        self.ready = threading.Event()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.ready.set()  # 通知主线程 loop 已准备好
        self.loop.run_forever()

    def create_task(self, coro):
        """线程安全地提交协程任务"""
        self.ready.wait()
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def call_soon(self, callback, *args):
        """线程安全地调度普通函数"""
        self.ready.wait()
        self.loop.call_soon_threadsafe(callback, *args)


# 实例化全局事件循环线程
_loop_thread = EventLoopThread()
_loop_thread.start()


# ---------------------------------------------------------

def Debug(is_debug: bool = True):
    global DEBUG
    DEBUG = is_debug


def log(info_head, *args: str | typing.List[str] | typing.Tuple[str] | typing.Any):
    global DEBUG
    if not DEBUG:
        return None
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    info_body = " ".join(str(arg) for arg in args)
    print(f"[{current_time}] [{info_head}] {info_body}")
    return None


class DynamicSemaphore:
    """可动态调整最大并发数的信号量"""

    def __init__(self, initial_value: int = 4):
        self._lock = threading.Lock()
        self._max_value = initial_value
        self._semaphore = threading.Semaphore(1000)

    def acquire(self):
        self._semaphore.acquire()
        with self._lock:
            current = self._semaphore._value
            active = 1000 - current
            if active > self._max_value:
                self._semaphore.release()
                self.acquire()

    def release(self):
        self._semaphore.release()

    def set_max_value(self, max_value: int):
        with self._lock:
            self._max_value = max_value

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class Signal:
    def __init__(self, *args):
        self._type: tuple[type, ...] = args
        self._enabled: bool = True
        self._threads_enabled: bool = False
        self._thread_semaphore = DynamicSemaphore(4)
        self._slots: list[typing.Callable[..., typing.Any]] = []

    def _run_slot(self, slot: typing.Callable[..., typing.Any], *args, **kwargs):
        with self._thread_semaphore:
            try:
                slot(*args, **kwargs)
            except Exception as e:
                log("Signal", f"槽函数 {slot} 执行时发生异常: {str(e)}")

    def connect(self, slot: (typing.Callable | 'Signal')) -> bool:
        if not callable(slot) and not isinstance(slot, Signal):
            raise TypeError("信号槽必须是可调用对象或另一个Signal实例")
        if isinstance(slot, Signal):
            if slot._type != self._type:
                raise TypeError(f"传递的信号实例需求的参数类型不匹配，预期 {self._type}，实际 {slot._type}")
            self._slots.append(slot.emit)
            return True
        self._slots.append(slot)
        return True

    def emit(self, *args, **kwargs) -> bool:
        if not self._enabled:
            return False
        types = tuple(type(arg) for arg in args)
        if types != self._type:
            raise TypeError(f"预期得到参数类型 {self._type}，实际为 {types}")

        if self._threads_enabled:
            threads = []
            for slot in self._slots:
                thread = threading.Thread(target=self._run_slot, args=(slot, *args), kwargs=kwargs)
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
        else:
            for slot in self._slots:
                slot(*args, **kwargs)
        return True

    def setEnabled(self, enabled: bool):
        self._enabled = enabled

    def setThreads(self, enable_threads: bool | None = None, max_threads: int | None = None):
        if enable_threads is not None:
            self._threads_enabled = enable_threads
        if max_threads is not None and isinstance(max_threads, int) and max_threads > 0:
            self._thread_semaphore.set_max_value(max_threads)


class MemoryInfo:
    used = None
    available = None
    total = None

    def __init__(self, used=None, available=None, total=None):
        self.used = used
        self.available = available
        self.total = total

    @staticmethod
    def mb_to_gb(mb):
        try:
            return round(float(mb) / 1024, 1)
        except (ValueError, TypeError):
            return None

    def MB(self):
        class _:
            used = None
            available = None
            total = None

        obj = _()
        obj.used = self.used
        obj.available = self.available
        obj.total = self.total
        return obj

    def GB(self):
        class _:
            used = None
            available = None
            total = None

        obj = _
        obj.used = self.mb_to_gb(self.used)
        obj.available = self.mb_to_gb(self.available)
        obj.total = self.mb_to_gb(self.total)
        return obj


class DeviceInfoData:
    updated = Signal()
    error = Signal(str)

    def __init__(self):
        self.last_update_time = time.time()
        self.singles = []

        self.cpu_usage = None
        self.cpu_temperature = None
        self.cpu_power = None

        self.gpu_usage = None
        self.gpu_temperature = None
        self.gpu_hotspot_temperature = None
        self.gpu_power = None

        self.gpu_memory_usage = None
        self.gpu_memory_used = None
        self.gpu_memory_available = None
        self.gpu_memory_total = None

        self.memory_usage = None
        self.memory_used = None
        self.memory_available = None
        self.memory_total = None

    def __str__(self):
        return f"CPU使用率    {self.cpu_usage}%\n" \
               f"CPU温度      {self.cpu_temperature}°C\n" \
               f"CPU功耗      {self.cpu_power} W\n" \
               f"GPU使用率    {self.gpu_usage}%\n" \
               f"GPU温度      {self.gpu_temperature}°C\n" \
               f"GPU热点温度  {self.gpu_hotspot_temperature}°C\n" \
               f"GPU功耗      {self.gpu_power} W\n" \
               f"GPU内存使用率 {self.gpu_memory_usage}%\n" \
               f"GPU内存已用量 {self.gpu_memory_used} MB\n" \
               f"GPU内存可用量 {self.gpu_memory_available} MB\n" \
               f"GPU内存总量   {self.gpu_memory_total} MB\n" \
               f"内存占用率    {self.memory_usage}%\n" \
               f"内存已用量    {self.memory_used} MB\n" \
               f"内存可用量    {self.memory_available} MB\n" \
               f"内存总量      {self.memory_total} MB"

    def extract_hardware_info(self, db):
        if "SCPUUTI" in db:
            self.cpu_usage = db["SCPUUTI"]["value"]
        if "TCPUPKG" in db:
            self.cpu_temperature = db["TCPUPKG"]["value"]
        if "PCPUPKG" in db:
            self.cpu_power = db["PCPUPKG"]["value"]

        if "SGPU1UTI" in db:
            self.gpu_usage = db["SGPU1UTI"]["value"]
        if "TGPU1" in db:
            self.gpu_temperature = db["TGPU1"]["value"]
        if "TGPU1HOT" in db:
            self.gpu_hotspot_temperature = db["TGPU1HOT"]["value"]
        if "PGPU1" in db:
            self.gpu_power = db["PGPU1"]["value"]
        if "SVMEMUSAGE" in db:
            self.gpu_memory_usage = db["SVMEMUSAGE"]["value"]
        if "SUSEDVMEM" in db:
            self.gpu_memory_used = db["SUSEDVMEM"]["value"]
        if "SFREEVMEM" in db:
            self.gpu_memory_available = db["SFREEVMEM"]["value"]

        if self.gpu_memory_used and self.gpu_memory_available:
            try:
                self.gpu_memory_total = float(self.gpu_memory_used) + float(self.gpu_memory_available)
            except (ValueError, TypeError):
                self.gpu_memory_total = None

        if "SMEMUTI" in db:
            self.memory_usage = db["SMEMUTI"]["value"]
        if "SUSEDMEM" in db:
            self.memory_used = db["SUSEDMEM"]["value"]
        if "SFREEMEM" in db:
            self.memory_available = db["SFREEMEM"]["value"]

        if self.memory_used and self.memory_available:
            try:
                self.memory_total = float(self.memory_used) + float(self.memory_available)
            except (ValueError, TypeError):
                self.memory_total = None

    async def Update(self):
        if os.name != 'nt':
            return

        db = {}
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\FinalWire\\AIDA64\\SensorValues") as key:
                for i in range(winreg.QueryInfoKey(key)[1]):
                    name, data, _type = winreg.EnumValue(key, i)
                    attr = name.split(".")
                    if attr[0] == "Label":
                        db[attr[1]] = {}
                        db[attr[1]]["label"] = data
                    else:
                        db[attr[1]]["value"] = data
        except FileNotFoundError:
            self.error.emit("未找到AIDA64注册表路径，请确认已安装并运行AIDA64")
            return
        except Exception as e:
            self.error.emit(f"读取AIDA64数据出错：{str(e)}")
            return

        current_time = time.time()
        if current_time > self.last_update_time:
            self.extract_hardware_info(db)
            self.last_update_time = current_time
            self.updated.emit()
        return


class DeviceInfo:
    updated = Signal()
    error = Signal(str)

    def __init__(self):
        self.device_info = DeviceInfoData()
        self.device_info.updated.connect(self.updated)
        self.device_info.error.connect(self.error)

        # 先提交一次更新
        _loop_thread.create_task(self.device_info.Update())

        # 更新间隔 (s)
        self.update_interval_time = 2

        self.update_thread_is_started = False
        self.start()

    def __str__(self):
        return self.device_info.__str__()

    def run(self):
        async def _update_loop():
            while True:
                await self.device_info.Update()
                await asyncio.sleep(self.update_interval_time)

        _loop_thread.create_task(_update_loop())

    def start(self):
        if self.update_thread_is_started:
            log("DeviceInfo", "更新线程已启动，无需重复启动")
            return None
        self.update_thread_is_started = True
        update_thread = threading.Thread(target=self.run, daemon=True)
        update_thread.start()
        return None

    def SetUpdateInterval(self, interval: int):
        if isinstance(interval, int) and interval > 0:
            self.update_interval_time = interval
            log("DeviceInfo", f"已设置更新间隔为 {interval} 秒")
        else:
            log("DeviceInfo", f"无效的更新间隔: {interval}，请提供一个正整数")

    def GetCPUUsage(self):
        return self.device_info.cpu_usage

    def GetCPUTemperature(self):
        return self.device_info.cpu_temperature

    def GetCPUPower(self):
        return self.device_info.cpu_power

    def GetGPUUsage(self):
        return self.device_info.gpu_usage

    def GetGPUTemperature(self):
        return self.device_info.gpu_temperature

    def GetGPUPower(self):
        return self.device_info.gpu_power

    def GetGPUMemoryUsage(self):
        return self.device_info.gpu_memory_usage

    def GetGPUMemory(self, unit="MB"):
        memory_info = MemoryInfo(used=self.device_info.gpu_memory_used,
                                 available=self.device_info.gpu_memory_available,
                                 total=self.device_info.gpu_memory_total)
        if unit == "GB" or unit == "gb":
            return memory_info.GB()
        return memory_info.MB()

    def GetGPUHotspotTemperature(self):
        return self.device_info.gpu_hotspot_temperature

    def GetMemoryUsage(self):
        return self.device_info.memory_usage

    def GetMemory(self, unit="MB"):
        memory_info = MemoryInfo(used=self.device_info.memory_used,
                                 available=self.device_info.memory_available,
                                 total=self.device_info.memory_total)
        if unit == "GB" or unit == "gb":
            return memory_info.GB()
        return memory_info.MB()


class BLE:
    class signals:
        found_device = Signal(str)
        connected = Signal()
        disconnected = Signal()
        connect_timeout = Signal()
        on_get_data = Signal(dict)  # 改为 dict 类型

    def __init__(self,
                 device_name="ESP32-S3-N16R8",
                 rx_uuid="6E400002-B5A3-F393-E0A9-E50E24DCCA9E",
                 tx_uuid="6E400003-B5A3-F393-E0A9-E50E24DCCA9E"):
        self.device_name = device_name
        self.rx_uuid = rx_uuid
        self.tx_uuid = tx_uuid

        self.device_client: BleakClient | None = None
        self.break_main_thread = False

        # 【修复2】添加接收缓冲区
        self.rx_buffer = b""

        self.signals.found_device.setThreads(enable_threads=True)
        self.signals.connected.setThreads(enable_threads=True)
        self.signals.disconnected.setThreads(enable_threads=True)
        self.signals.connect_timeout.setThreads(enable_threads=True)
        self.signals.on_get_data.setThreads(enable_threads=True)

        self.ScanDevice()

    def on_found_device(self, device_address):
        log("BLE", f"找到BLE设备 {self.device_name}，地址: {device_address}")
        self.signals.found_device.emit(device_address)

    def on_connected(self):
        log("BLE", f"成功连接到BLE设备 {self.device_name}")
        self.signals.connected.emit()

    def on_disconnected(self, client):
        log("BLE", f"BLE设备 {self.device_name} 已断开连接")
        self.device_client = None
        self.rx_buffer = b""  # 清空缓冲区
        self.signals.disconnected.emit()

    def process_complete_data(self, data_str):
        """处理完整的数据包"""
        try:
            data_dict = json.loads(data_str)
            log("BLE", f"从BLE设备 {self.device_name} 接收到数据: {data_dict}")
            self.signals.on_get_data.emit(data_dict)
        except json.JSONDecodeError:
            log("BLE", f"从BLE设备 {self.device_name} 接收到非JSON数据: {data_str}")
            self.signals.on_get_data.emit({})

    def on_get_data(self, sender, data):
        """处理分包拼接"""
        try:
            self.rx_buffer += data

            # 检查是否有结束符 \n
            while b'\n' in self.rx_buffer:
                complete_data_bytes, self.rx_buffer = self.rx_buffer.split(b'\n', 1)
                complete_data_str = complete_data_bytes.decode('utf-8').strip()
                if complete_data_str:
                    self.process_complete_data(complete_data_str)

        except Exception as e:
            log("BLE", f"处理从BLE设备 {self.device_name} 接收到的数据时出错: {str(e)}\n原始数据: {data}")
            return

    async def scan_device(self, interval, timeout):
        if self.device_client:
            log("BLE", f"已连接到BLE设备 {self.device_name}，无需重复连接")
            return True

        log("BLE", f"正在搜索BLE设备 {self.device_name}...")
        current_time = time.time()

        while True:
            if time.time() - current_time > timeout:
                log("BLE", f"搜索BLE设备 {self.device_name} 超时，请确保设备已开启并在范围内")
                self.signals.connect_timeout.emit()
                return False

            devices = await BleakScanner.discover()
            target_device_address = None

            for device in devices:
                if device.name == self.device_name:
                    target_device_address = device.address
                    break

            if target_device_address:
                self.on_found_device(target_device_address)

                self.device_client = BleakClient(address_or_ble_device=target_device_address,
                                                 disconnected_callback=self.on_disconnected)
                await self.device_client.connect()

                if self.device_client.is_connected:
                    self.on_connected()
                    await self.device_client.start_notify(self.tx_uuid, self.on_get_data)
                    return True
                else:
                    log("BLE", f"连接到BLE设备 {self.device_name} 失败，请重试")
                    self.device_client = None

            await asyncio.sleep(interval)

    def SendCommand(self, _command: str | list[dict] | dict | typing.Any):
        """
        发送指令到BLE设备
        """
        if not self.device_client or not self.device_client.is_connected:
            log("BLE", "设备未连接，无法发送指令")
            return

        async def _send():
            try:
                command_str = None
                # 统一转换为字符串并编码
                if isinstance(_command, dict):
                    command_str = json.dumps(_command)
                elif isinstance(_command, list):
                    if all(isinstance(item, dict) for item in _command):
                        command_dict = {}
                        for item in _command:
                            for key, value in item.items():
                                command_dict[key] = value
                        command_str = json.dumps(command_dict)
                else:
                    command_str = str(_command)

                if not command_str:
                    log("BLE", f"无法将指令 {_command} 转换为字符串，指令无效")
                    return

                # 添加结束符
                command_bytes = command_str.encode('utf-8') + b'\n'

                print(f"发送数据: {command_str}")
                await self.device_client.write_gatt_char(self.rx_uuid, command_bytes)

                log("BLE", f"指令发送成功: {_command}")
            except Exception as e:
                log("BLE", f"指令发送失败: {e}")

        _loop_thread.create_task(_send())

    def ScanDevice(self, interval=1, timeout=10):
        _loop_thread.create_task(self.scan_device(interval, timeout))

    def deinit(self):
        # 清除资源
        # 断开蓝牙连接
        self.device_client.disconnect()
        # 停止事件循环线程
        _loop_thread.loop.call_soon_threadsafe(_loop_thread.loop.stop)
        log("BLE", "已清理BLE资源")


class Commands:
    @staticmethod
    def SetFanSpeed(speed: int) -> dict:
        """
        设置风扇转速
        :param speed: 0-100 (%)
        :return:
        """
        return {"SetFanSpeed": speed}

    @staticmethod
    def SetPumpSpeed(speed: int) -> dict:
        """
        设置水泵转速
        :param speed: 0-100 (%)
        :return:
        """
        return {"SetPumpSpeed": speed}

    @staticmethod
    def GetFanSpeed(sample_time: int = 1) -> dict:
        """
        获取风扇速度
        :param sample_time: 采样时间 (s)
        :return:
        """
        return {"GetFanSpeed": sample_time}

    @staticmethod
    def GetPumpSpeed(sample_time: int = 1) -> dict:
        """
        获取水泵速度
        :param sample_time: 采样时间 (s)
        :return:
        """
        return {"GetPumpSpeed": sample_time}

    @staticmethod
    def SetBoardLEDColor(r: int, g: int, b: int) -> dict:
        """
        设置板载LED颜色
        :param r: 红色分量 (0-255)
        :param g: 绿色分量 (0-255)
        :param b: 蓝色分量 (0-255)
        :return:
        """
        return {"SetBoardLEDColor": {"r": r, "g": g, "b": b}}


if __name__ == "__main__":
    Debug(True)
    device_info = DeviceInfo()
    ble = BLE()
    now = 0
    while True:
        fan_speed = int(input("按回车键发送一次指令（输入exit退出）: \n"))

        ori = [0, 0, 0]
        ori[now] = 25

        # 构造正确的 JSON 消息
        ble.SendCommand([
            Commands.SetBoardLEDColor(0, 0, 0),
            Commands.SetFanSpeed(fan_speed),
            Commands.SetPumpSpeed(fan_speed),
            Commands.GetFanSpeed(),
            Commands.GetPumpSpeed()
        ])
        now += 1
        if now >= 3:
            now = 0