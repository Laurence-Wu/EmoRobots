#!/usr/bin/env python3
'''
Example usage script for servo testing
示例：如何使用伺服舵机测试脚本
--------------------------------------------------
'''

import os
import sys

# Add the servo test script to path
sys.path.append(os.path.dirname(__file__))

from servo_test_comprehensive import ServoTester, ServoTestConfig

def example_basic_test():
    """基本测试示例"""
    print("=== 基本伺服舵机测试 ===")
    
    # 创建测试器 - 根据你的系统调整端口
    # macOS: '/dev/cu.usbserial-*' 或 '/dev/tty.usbserial-*'
    # Linux: '/dev/ttyUSB0' 或 '/dev/ttyACM0'
    # Windows: 'COM1', 'COM2', etc.
    
    tester = ServoTester(
        port='/dev/tty.usbserial-14210',  # 根据实际情况修改
        baudrate=115200
    )
    
    # 运行基本测试（不包括运动测试）
    results = tester.run_comprehensive_test(test_movement=False)
    
    # 保存结果
    tester.save_results("basic_test")
    
    # 显示摘要
    print(f"\n发现的舵机: {results['available_servos']}")
    print(f"错误数量: {len(results['errors'])}")
    
    return results

def example_full_test():
    """完整测试示例（包括运动测试）"""
    print("=== 完整伺服舵机测试（包括运动测试） ===")
    
    tester = ServoTester(port='/dev/cu.usbserial-0001')
    
    # 自定义测试的舵机ID
    tester.config.DEFAULT_SERVO_IDS = [0, 1, 2]  # 只测试前3个舵机
    
    # 运行完整测试
    results = tester.run_comprehensive_test(test_movement=True)
    
    # 保存结果
    tester.save_results("full_test")
    
    return results

def example_custom_config():
    """自定义配置示例"""
    print("=== 自定义配置测试 ===")
    
    # 创建自定义配置
    class CustomConfig(ServoTestConfig):
        DEFAULT_SERVO_IDS = [0, 1]  # 只测试两个舵机
        ANGLE_TEST_RANGE = [-45, 0, 45]  # 减少测试角度
        MAX_TEMPERATURE = 50  # 更严格的温度限制
    
    tester = ServoTester(port='/dev/cu.usbserial-0001')
    tester.config = CustomConfig()
    
    # 运行测试
    results = tester.run_comprehensive_test(test_movement=True)
    
    # 保存结果
    tester.save_results("custom_test")
    
    return results

def example_availability_check():
    """仅检查可用性示例"""
    print("=== 舵机可用性快速检查 ===")
    
    tester = ServoTester(port='/dev/cu.usbserial-0001')
    
    if tester.connect():
        try:
            # 快速发现可用的舵机
            available_servos = tester.discover_servos()
            
            print(f"可用的舵机ID: {available_servos}")
            
            # 为每个可用的舵机读取基本状态
            for servo_id in available_servos:
                status = tester.read_servo_status(servo_id)
                print(f"舵机 {servo_id}:")
                print(f"  - 在线: {status['online']}")
                print(f"  - 角度: {status.get('angle', 'N/A')}°")
                print(f"  - 电压: {status.get('voltage', 'N/A')}V")
                print(f"  - 温度: {status.get('temperature', 'N/A')}°C")
                
        finally:
            tester.disconnect()
    else:
        print("无法连接到舵机控制器")

def check_port_availability():
    """检查可用串口"""
    import serial.tools.list_ports
    
    print("=== 可用串口检查 ===")
    ports = serial.tools.list_ports.comports()
    
    if ports:
        print("发现的串口:")
        for port, desc, hwid in sorted(ports):
            print(f"  {port}: {desc}")
    else:
        print("未发现可用串口")
    
    print("\n常见端口名称:")
    print("  macOS: /dev/cu.usbserial-* 或 /dev/tty.usbserial-*")
    print("  Linux: /dev/ttyUSB0 或 /dev/ttyACM0")
    print("  Windows: COM1, COM2, COM3, ...")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Servo Test Examples')
    parser.add_argument('--check-ports', action='store_true', help='Check available serial ports')
    parser.add_argument('--basic', action='store_true', help='Run basic test')
    parser.add_argument('--full', action='store_true', help='Run full test with movement')
    parser.add_argument('--custom', action='store_true', help='Run custom configuration test')
    parser.add_argument('--availability', action='store_true', help='Quick availability check')
    parser.add_argument('--port', type=str, help='Serial port to use')
    
    args = parser.parse_args()
    
    if args.check_ports:
        check_port_availability()
    elif args.basic:
        example_basic_test()
    elif args.full:
        example_full_test()
    elif args.custom:
        example_custom_config()
    elif args.availability:
        example_availability_check()
    else:
        print("Servo Test Examples")
        print("==================")
        print()
        print("Available examples:")
        print("  --check-ports     : 检查可用串口")
        print("  --basic          : 基本测试（无运动）")
        print("  --full           : 完整测试（包括运动）")
        print("  --custom         : 自定义配置测试")
        print("  --availability   : 快速可用性检查")
        print()
        print("使用示例:")
        print("  python servo_test_examples.py --check-ports")
        print("  python servo_test_examples.py --basic --port /dev/cu.usbserial-0001")
        print("  python servo_test_examples.py --full --port /dev/ttyUSB0")
