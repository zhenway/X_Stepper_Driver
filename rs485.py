"""
文件名：rs485.py
功能：底层串口通信驱动 (已增加接收功能)
"""
import sys
import time

try:
    from machine import UART, Pin
    MICROPYTHON = True
except ImportError:
    MICROPYTHON = False

class RS485:
    def __init__(self, port=None, baud=115200, uart_id=1, tx=4, rx=5, de_pin=2):
        self.baud = baud
        if MICROPYTHON:
            self.uart = UART(uart_id, baudrate=baud, tx=Pin(tx), rx=Pin(rx))
            self.de = Pin(de_pin, Pin.OUT)
            self.de.value(0) # 默认接收模式
        else:
            try:
                import serial
                self.uart = serial.Serial(port, baudrate=baud, timeout=1)
                time.sleep(2) 
            except ImportError:
                print("错误：PC端运行需要安装 pyserial (pip install pyserial)")
                sys.exit()

    def write(self, data):
        if MICROPYTHON:
            self.de.value(1) 
            self.uart.write(data)
            self.uart.flush()
            self.de.value(0) 
        else:
            self.uart.write(data)

    def read(self, length=10, timeout=0.1):
        """
        读取串口数据 (用于查看电机返回的消息)
        """
        if MICROPYTHON:
            time.sleep(timeout)
            if self.uart.any():
                return self.uart.read(length)
            return None
        else:
            return self.uart.read(length)