"""
文件名：test.py
功能：力控夹爪 + 回原位测试
"""
import time
from x_stepper import StepperMotor

PORT_NAME = 'COM16'
MOTOR_ADDR = 0x01
BAUDRATE = 115200

def _read_current_raw(motor, timeout=0.3):
    addr = motor.addr
    cmd = bytearray([addr, 0x27, 0x6B])
    motor.bus.write(cmd)
    start = time.time()
    while time.time() - start < timeout:
        data = motor.bus.read(length=10, timeout=0.05)
        if data and len(data) >= 5:
            if data[0] == addr and data[1] == 0x27:
                return (data[2] << 8) | data[3]
    return None

def _read_position_raw(motor, timeout=0.3):
    addr = motor.addr
    cmd = bytearray([addr, 0x36, 0x6B])
    motor.bus.write(cmd)
    start = time.time()
    while time.time() - start < timeout:
        data = motor.bus.read(length=10, timeout=0.05)
        if data and len(data) >= 8:
            if data[0] == addr and data[1] == 0x36:
                sign = 1 if data[2] == 0x00 else -1
                val = (data[3] << 24) | (data[4] << 16) | (data[5] << 8) | data[6]
                return sign * val * 0.1
    return None

def force_grip(motor, target_current_mA, slope=500, grip_timeout=5.0):
    print(f"\n[力控夹爪] 目标电流 {target_current_mA} mA, 斜率 {slope} mA/s")
    motor.set_torque(slope=slope, current=target_current_mA)
    time.sleep(0.1)

    stable_count = 0
    fail_count = 0
    start_time = time.time()

    try:
        while time.time() - start_time < grip_timeout:
            current_mA = _read_current_raw(motor)
            if current_mA is None:
                fail_count += 1
                if fail_count > 10:
                    print("[力控夹爪] 通信连续失败，停止夹紧！")
                    return False
                time.sleep(0.05)
                continue
            fail_count = 0
            print(f"[监控] 当前电流: {current_mA} mA")
            if current_mA >= target_current_mA * 0.9:
                stable_count += 1
                if stable_count >= 3:
                    print(f"[力控夹爪] 夹紧完成，电流稳定在 {current_mA} mA")
                    return True
            else:
                stable_count = 0
            time.sleep(0.1)
        print("[力控夹爪] 超时，未能夹紧！")
        return False
    finally:
        motor.stop()
        print("[力控夹爪] 电机运动已停止，保持使能锁轴")

def main():
    print("=== ZDT X系列电机 力控夹爪 + 回原位测试 ===")
    motor = StepperMotor(port=PORT_NAME, baud=BAUDRATE, addr=MOTOR_ADDR)

    try:
        print("\n[初始化] 使能电机...")
        motor.enable()
        time.sleep(1)

        home_pos = _read_position_raw(motor)
        if home_pos is None:
            print("[错误] 无法读取原位，退出！")
            return
        print(f"[参考] 当前原位: {home_pos:.1f}°")

        success = force_grip(motor, target_current_mA=500, slope=500, grip_timeout=5.0)

        if success:
            print("\n[结果] 夹紧成功，保持 3 秒...")
            time.sleep(3)
        print(f"\n[回位] 正在回到原位 {home_pos:.1f}° ...")
        motor.set_position(speed=500, pos=int(home_pos * 10), mode=0x01)
        time.sleep(3)
        print("[回位] 完成。")

    except KeyboardInterrupt:
        print("\n[用户中断]")
    except Exception as e:
        print(f"[异常] {e}")
    finally:
        print("\n[清理] 失能电机...")
        try:
            motor.disable()
        except Exception as e:
            print(f"[警告] 失能失败: {e}")

if __name__ == '__main__':
    main()