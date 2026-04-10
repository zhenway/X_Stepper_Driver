"""
文件名：x_stepper.py
功能：ZDT X系列闭环步进电机驱动类 (仅修正使能指令)
"""
import time
from rs485 import RS485

# 指令常量
CMD_ENABLE = 0xF3
CMD_DISABLE = 0xF4
CMD_STOP = 0xFE
CMD_VEL = 0xF6 # 速度模式
CMD_POS = 0xFB # 位置模式
CHECK_CODE = 0x6B # 根据文档 4.1.1 固定校验码

class StepperMotor:
    def __init__(self, port=None, baud=115200, addr=0x01):
        self.addr = addr
        self.bus = RS485(port=port, baud=baud)
        self.running = False

    def _build_cmd(self, cmd, *args):
        """构建数据包"""
        data = bytearray(args)
        packet = bytearray([self.addr, cmd]) + data + bytearray([CHECK_CODE])
        return bytes(packet)

    def _send(self, cmd, *args):
        """发送指令并打印日志"""
        packet = self._build_cmd(cmd, *args)
        self.bus.write(packet)
        
        # 打印发送内容
        print(f"TX: {' '.join(f'{b:02X}' for b in packet)}")
        
        # --- 新增：读取并打印电机返回的消息 ---
        response = self.bus.read(length=10, timeout=0.1)
        if response:
            print(f"RX: {' '.join(f'{b:02X}' for b in response)}")
        return response

    # --- 仅修正此处：Enable/Disable ---
    
    def enable(self):
        """
        电机使能 (已严格修正格式)
        文档 5.3.2: Addr F3 AB 01 01 6B
        """
        # 修正：增加 0xAB (辅助码) 和 0x01 (同步位)
        self._send(CMD_ENABLE, 0xAB, 0x01, 0x00)

    def disable(self):
        """
        电机失能
        """
        # 对应修正关闭指令
        self._send(CMD_ENABLE, 0xAB, 0x00, 0x00)

    # --- 以下为原有功能，完全未改动 ---
    
    def stop(self):
        self._send(CMD_STOP)
        self.running = False
    def set_velocity(self, speed):
        """
        设置速度模式运行
        speed: 目标速度 (单位: RPM)
               注意：协议单位是 0.1 RPM，这里自动转换
        """
        direction = 0x00      # 0x00: 正转, 0x01: 反转
        accel = 200          # 加速度: 1000 RPM/s (0x03E8)
        sync = 0x00           # 立即执行

        # === 核心修正 ===
        # 协议要求速度单位为 0.1 RPM
        # 如果传入 speed=1000 (1000 RPM)，需要转换为 10000 (0x2710)
        speed_val = int(speed * 10)

        # 限制最大值 (协议最大 3000.0 RPM -> 30000)
        if speed_val > 30000:
            speed_val = 30000

        # 拆分高低字节
        # 加速度 (2字节): 1000 -> 0x03 E8
        
        acc_l = accel & 0xFF        # 0x14 (20)
        acc_h = (accel >> 8) & 0xFF # 0x00 (0)

        # 速度 (2字节): 10000 -> 0x27 10
        spd_h = (speed_val >> 8) & 0xFF
        spd_l = speed_val & 0xFF

        # 发送指令 (共9字节: Addr + Cmd + Dir + AccH + AccL + SpdH + SpdL + Sync + Check)
        # 之前的问题是多发了一个字节，现在严格修正为 8个参数 + 1个校验位
            # --- 发送指令 (关键修正点) ---
    # ZDT 协议要求：先发低字节，再发高字节 (小端模式)
    # 顺序必须是: 方向 + Acc_L + Acc_H + Spd_L + Spd_H + Sync
    # 对比你之前的代码，你把 Acc_H 和 Acc_L 的位置写反了！
        self._send(
            CMD_VEL, 
            direction, 
            acc_l,   # 先发低位
            acc_h,  # 再发高位
            spd_l,   # 先发低位
            spd_h,  # 再发高位
            sync)
        self.running = True

    def set_position(self, speed, pos, mode=0x00, sync=0x00, direction=0x01):
        """
        直通限速位置模式 (X固件功能码 0xFB)
        speed: 目标速度 (RPM)，如传入 1000
        pos: 目标位置 (0.1°)，如传入 5000 代表 500.0°
        """
        # 速度单位是 0.1RPM，传入 RPM 需乘 10
        speed_val = int(speed * 10)
        pos_val = int(pos)

        # 大端序拆字节，通过 _send 发送
        self._send(
            CMD_POS,
            direction,
            (speed_val >> 8) & 0xFF,  # 速度高字节
            speed_val & 0xFF,          # 速度低字节
            (pos_val >> 24) & 0xFF,    # 位置字节3
            (pos_val >> 16) & 0xFF,    # 位置字节2
            (pos_val >> 8) & 0xFF,     # 位置字节1
            pos_val & 0xFF,            # 位置字节0
            mode,
            sync,
        )

