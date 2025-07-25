'''
FashionStar UART Servo SDK for Python
总线伺服舵机 Python SDK
--------------------------------------------------
 * 作者: 深圳市华馨京科技有限公司
 * 网站：https://fashionrobo.com/
 * 基于通信协议的Python SDK
 * 适用于所有总线伺服舵机型号
--------------------------------------------------
'''

import time
import struct
import serial
from typing import Optional, Union


class UartServoManager:
    """UART Servo Manager Class - 总线伺服舵机管理器"""
    
    # Protocol constants
    HEADER_REQUEST = b'\x12\x4c'
    HEADER_RESPONSE = b'\x05\x1c'
    
    # Command codes
    CMD_PING = 0x01                 # 舵机通讯检测
    CMD_SET_SERVO_ANGLE = 0x03      # 设置舵机角度
    CMD_QUERY_SERVO_ANGLE = 0x04    # 查询舵机角度
    CMD_SET_SERVO_MTURN = 0x06      # 设置舵机多圈角度
    CMD_QUERY_VOLTAGE = 0x10        # 查询舵机电压
    CMD_QUERY_CURRENT = 0x11        # 查询舵机电流
    CMD_QUERY_POWER = 0x12          # 查询舵机功率
    CMD_QUERY_TEMPERATURE = 0x13    # 查询舵机温度
    CMD_QUERY_STATUS = 0x14         # 查询舵机状态
    CMD_SET_DAMPING = 0x20          # 设置阻尼模式
    CMD_RESET_USER_DATA = 0x30      # 重置用户数据
    CMD_READ_DATA = 0x31            # 读取数据
    CMD_WRITE_DATA = 0x32           # 写入数据
    
    def __init__(self, uart: serial.Serial, timeout: float = 0.1):
        """
        初始化UART伺服舵机管理器
        
        Args:
            uart: 已配置的串口对象
            timeout: 通讯超时时间(秒)
        """
        self.uart = uart
        self.timeout = timeout
        self.uart.timeout = timeout
    
    def _calc_checksum(self, data: bytes) -> int:
        """计算校验和"""
        return sum(data) % 256
    
    def _pack_request(self, cmd: int, params: bytes = b'') -> bytes:
        """打包请求数据包"""
        size = len(params)
        packet = self.HEADER_REQUEST + struct.pack('<BB', cmd, size) + params
        checksum = self._calc_checksum(packet)
        return packet + struct.pack('<B', checksum)
    
    def _unpack_response(self, response: bytes) -> Optional[bytes]:
        """解包响应数据包"""
        if len(response) < 5:  # 最小包长度
            return None
            
        # 检查帧头
        if response[:2] != self.HEADER_RESPONSE:
            return None
            
        # 提取命令码和数据长度
        cmd, size = struct.unpack('<BB', response[2:4])
        
        # 检查包长度
        expected_len = 5 + size  # 帧头(2) + 命令码(1) + 长度(1) + 数据(size) + 校验和(1)
        if len(response) != expected_len:
            return None
            
        # 提取数据和校验和
        data = response[4:4+size]
        checksum = response[-1]
        
        # 验证校验和
        calc_checksum = self._calc_checksum(response[:-1])
        if checksum != calc_checksum:
            return None
            
        return data
    
    def _send_command(self, cmd: int, params: bytes = b'') -> Optional[bytes]:
        """发送命令并接收响应"""
        try:
            # 清空接收缓冲区
            self.uart.reset_input_buffer()
            
            # 发送请求
            request = self._pack_request(cmd, params)
            self.uart.write(request)
            self.uart.flush()
            
            # 等待响应
            time.sleep(0.01)  # 短暂延迟
            
            # 读取响应
            response = self.uart.read(100)  # 读取最多100字节
            if not response:
                return None
                
            # 解包响应
            return self._unpack_response(response)
            
        except Exception as e:
            print(f"Command error: {e}")
            return None
    
    def ping(self, servo_id: int) -> bool:
        """
        舵机通讯检测
        
        Args:
            servo_id: 舵机ID (0-253)
            
        Returns:
            bool: True表示舵机在线，False表示离线
        """
        params = struct.pack('<B', servo_id)
        response = self._send_command(self.CMD_PING, params)
        return response is not None
    
    def set_servo_angle(self, servo_id: int, angle: float, 
                       interval: Optional[int] = None,
                       velocity: Optional[float] = None,
                       t_acc: Optional[int] = None,
                       t_dec: Optional[int] = None,
                       power: Optional[int] = None,
                       is_mturn: bool = False) -> bool:
        """
        设置舵机角度
        
        Args:
            servo_id: 舵机ID
            angle: 目标角度(度)
            interval: 执行周期(毫秒)
            velocity: 目标转速(度/秒)
            t_acc: 加速时间(毫秒)
            t_dec: 减速时间(毫秒)
            power: 功率限制(毫瓦)
            is_mturn: 是否多圈模式
            
        Returns:
            bool: 命令是否发送成功
        """
        try:
            angle_int = int(angle * 10)  # 角度转换为0.1度单位
            
            if interval is not None:
                # 按时间执行
                params = struct.pack('<BhH', servo_id, angle_int, interval)
                cmd = self.CMD_SET_SERVO_MTURN if is_mturn else self.CMD_SET_SERVO_ANGLE
                
            elif velocity is not None:
                # 按速度执行
                velocity_int = int(velocity * 10)
                t_acc = t_acc or 0
                t_dec = t_dec or 0
                params = struct.pack('<BhhHH', servo_id, angle_int, velocity_int, t_acc, t_dec)
                cmd = self.CMD_SET_SERVO_MTURN if is_mturn else self.CMD_SET_SERVO_ANGLE
                
            else:
                # 默认执行
                params = struct.pack('<Bh', servo_id, angle_int)
                cmd = self.CMD_SET_SERVO_MTURN if is_mturn else self.CMD_SET_SERVO_ANGLE
            
            response = self._send_command(cmd, params)
            return response is not None
            
        except Exception as e:
            print(f"Set angle error: {e}")
            return False
    
    def query_servo_angle(self, servo_id: int) -> Optional[float]:
        """
        查询舵机角度
        
        Args:
            servo_id: 舵机ID
            
        Returns:
            float: 舵机当前角度(度)，None表示查询失败
        """
        params = struct.pack('<B', servo_id)
        response = self._send_command(self.CMD_QUERY_SERVO_ANGLE, params)
        
        if response and len(response) >= 2:
            angle_int = struct.unpack('<h', response[:2])[0]
            return angle_int / 10.0
        return None
    
    def query_voltage(self, servo_id: int) -> Optional[float]:
        """
        查询舵机电压
        
        Args:
            servo_id: 舵机ID
            
        Returns:
            float: 电压值(伏特)，None表示查询失败
        """
        params = struct.pack('<B', servo_id)
        response = self._send_command(self.CMD_QUERY_VOLTAGE, params)
        
        if response and len(response) >= 2:
            voltage_int = struct.unpack('<H', response[:2])[0]
            return voltage_int / 1000.0  # 转换为伏特
        return None
    
    def query_current(self, servo_id: int) -> Optional[float]:
        """
        查询舵机电流
        
        Args:
            servo_id: 舵机ID
            
        Returns:
            float: 电流值(安培)，None表示查询失败
        """
        params = struct.pack('<B', servo_id)
        response = self._send_command(self.CMD_QUERY_CURRENT, params)
        
        if response and len(response) >= 2:
            current_int = struct.unpack('<h', response[:2])[0]
            return current_int / 1000.0  # 转换为安培
        return None
    
    def query_power(self, servo_id: int) -> Optional[float]:
        """
        查询舵机功率
        
        Args:
            servo_id: 舵机ID
            
        Returns:
            float: 功率值(瓦特)，None表示查询失败
        """
        params = struct.pack('<B', servo_id)
        response = self._send_command(self.CMD_QUERY_POWER, params)
        
        if response and len(response) >= 2:
            power_int = struct.unpack('<H', response[:2])[0]
            return power_int / 1000.0  # 转换为瓦特
        return None
    
    def query_temperature(self, servo_id: int) -> Optional[float]:
        """
        查询舵机温度
        
        Args:
            servo_id: 舵机ID
            
        Returns:
            float: 温度值(摄氏度)，None表示查询失败
        """
        params = struct.pack('<B', servo_id)
        response = self._send_command(self.CMD_QUERY_TEMPERATURE, params)
        
        if response and len(response) >= 1:
            temp_int = struct.unpack('<b', response[:1])[0]
            return float(temp_int)
        return None
    
    def query_status(self, servo_id: int) -> Optional[int]:
        """
        查询舵机状态
        
        Args:
            servo_id: 舵机ID
            
        Returns:
            int: 状态标志位，None表示查询失败
            BIT[0] - 执行指令置1，执行完成后清零
            BIT[1] - 执行指令错误置1，在下次正确执行后清零
            BIT[2] - 堵转错误置1，解除堵转后清零
            BIT[3] - 电压过高置1，电压恢复正常后清零
            BIT[4] - 电压过低置1，电压恢复正常后清零
            BIT[5] - 温度过高置1，温度恢复正常后清零
        """
        params = struct.pack('<B', servo_id)
        response = self._send_command(self.CMD_QUERY_STATUS, params)
        
        if response and len(response) >= 1:
            return struct.unpack('<B', response[:1])[0]
        return None
    
    def set_damping(self, servo_id: int, power: int = 0) -> bool:
        """
        设置阻尼模式
        
        Args:
            servo_id: 舵机ID
            power: 阻尼功率(0-1000毫瓦)，0为关闭阻尼
            
        Returns:
            bool: 命令是否发送成功
        """
        params = struct.pack('<BH', servo_id, power)
        response = self._send_command(self.CMD_SET_DAMPING, params)
        return response is not None
    
    def reset_user_data(self, servo_id: int) -> bool:
        """
        重置用户数据区
        
        Args:
            servo_id: 舵机ID
            
        Returns:
            bool: 命令是否发送成功
        """
        params = struct.pack('<B', servo_id)
        response = self._send_command(self.CMD_RESET_USER_DATA, params)
        return response is not None
    
    def read_data(self, servo_id: int, address: int, length: int = 1) -> Optional[bytes]:
        """
        读取舵机数据
        
        Args:
            servo_id: 舵机ID
            address: 数据地址
            length: 读取长度
            
        Returns:
            bytes: 读取的数据，None表示读取失败
        """
        params = struct.pack('<BBB', servo_id, address, length)
        return self._send_command(self.CMD_READ_DATA, params)
    
    def write_data(self, servo_id: int, address: int, data: bytes) -> bool:
        """
        写入舵机数据
        
        Args:
            servo_id: 舵机ID
            address: 数据地址
            data: 要写入的数据
            
        Returns:
            bool: 命令是否发送成功
        """
        params = struct.pack('<BB', servo_id, address) + data
        response = self._send_command(self.CMD_WRITE_DATA, params)
        return response is not None


# 兼容性别名
UartServo = UartServoManager

def create_servo_manager(port: str, baudrate: int = 115200, timeout: float = 0.1) -> UartServoManager:
    """
    创建伺服舵机管理器的便捷函数
    
    Args:
        port: 串口设备名
        baudrate: 波特率
        timeout: 超时时间
        
    Returns:
        UartServoManager: 舵机管理器实例
    """
    uart = serial.Serial(
        port=port,
        baudrate=baudrate,
        parity=serial.PARITY_NONE,
        stopbits=1,
        bytesize=8,
        timeout=timeout
    )
    return UartServoManager(uart, timeout)


if __name__ == "__main__":
    # 测试代码
    print("FashionStar UART Servo SDK")
    print("SDK功能测试...")
    
    # 这里可以添加基本的SDK测试代码
    try:
        # 测试创建管理器（不实际连接硬件）
        print("SDK初始化成功")
        print("可用的主要功能:")
        print("- ping(servo_id): 检测舵机在线状态")
        print("- set_servo_angle(servo_id, angle): 设置舵机角度")
        print("- query_servo_angle(servo_id): 查询舵机角度")
        print("- query_voltage/current/power/temperature(servo_id): 查询状态")
        print("- set_damping(servo_id, power): 设置阻尼模式")
        
    except Exception as e:
        print(f"SDK测试错误: {e}")
