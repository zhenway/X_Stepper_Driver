"""
文件名：test.py
功能：测试脚本 (增加接收测试)
"""
import time
from x_stepper import StepperMotor

# ================= 配置 =================
PORT_NAME = 'COM8' # 请修改为你的串口号

def main():
    print("=== ZDT X系列电机测试程序 ===")
    motor = StepperMotor(port=PORT_NAME, baud=115200, addr=0x01)
    
    try:
        
        # 测试原有功能
        print("\n[测试] 使能电机...")
        motor.enable()
        time.sleep(1)
        
        
 #       print("\n[测试] 速度模式运行...")
 #       motor.set_velocity(5000)
#    
 #       time.sleep(200)
        print("\n[测试] 位置模式运行...")
        motor.set_position(1000,300000)
        """
        # --- 新增：测试接收消息 ---
        print("\n[测试] 读取位置 (发送读取指令 0x36)...")
        # 直接调用底层读取接口，发送读取位置命令 (0x36)
        response = motor.read_response(0x36) 
        
        if response:
            print("成功接收到数据包")
        else:
            print("未接收到数据或超时")
"""


    except Exception as e:
        print(f"[错误] 发生异常: {e}")
    finally:
        motor.disable()

if __name__ == '__main__':
    main()