#!/usr/bin/env python3
'''
总线伺服舵机综合测试脚本
> Comprehensive Servo Test Script with Availability Tracking <
--------------------------------------------------
 * 作者: Generated for EmoRobots Project
 * 功能: 测试伺服舵机功能并存储可用性信息
 * 更新时间: 2025/07/25
--------------------------------------------------
'''

import os
import sys
import time
import json
import csv
import serial
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add the servo SDK path - adjust if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    import fashionstar_uart_sdk as uservo
except ImportError:
    print("Warning: fashionstar_uart_sdk not found. You may need to install or copy the SDK file.")
    print("Continuing with mock implementation for testing purposes...")
    uservo = None

class ServoTestConfig:
    """Configuration class for servo testing"""
    
    # Default serial port settings
    DEFAULT_PORT = '/dev/tty.usbserial-14210'  # Change for macOS: '/dev/tty.usbserial-*' or '/dev/cu.usbserial-*'
    DEFAULT_BAUDRATE = 1000000
    DEFAULT_TIMEOUT = 0.1  # Faster timeout for ping operations
    
    # Test parameters
    DEFAULT_SERVO_IDS = list(range(200))  # Test first 200 servo IDs (0-199)
    ANGLE_TEST_RANGE = [-90, -45, 0, 45, 90]  # Test angles in degrees
    MULTI_TURN_RANGE = [-360, -180, 0, 180, 360]  # Multi-turn test angles
    
    # Safety limits
    MAX_VOLTAGE = 12.0  # Maximum safe voltage
    MAX_CURRENT = 2.0   # Maximum safe current
    MAX_TEMPERATURE = 65  # Maximum safe temperature in Celsius
    
    # Output directory
    OUTPUT_DIR = "servo_test_results"

class ServoTester:
    """Comprehensive servo testing and availability tracking class"""
    
    def __init__(self, port: str = None, baudrate: int = None, timeout: float = None):
        self.config = ServoTestConfig()
        self.port = port or self.config.DEFAULT_PORT
        self.baudrate = baudrate or self.config.DEFAULT_BAUDRATE
        self.timeout = timeout or self.config.DEFAULT_TIMEOUT
        
        # Create output directory first
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        
        # Initialize logging after directory exists
        self.setup_logging()
        
        # Initialize serial connection and control
        self.uart = None
        self.control = None
        self.connected = False
        
        # Test results storage
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'port': self.port,
            'baudrate': self.baudrate,
            'available_servos': [],
            'servo_status': {},
            'test_summary': {},
            'errors': []
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = os.path.join(self.config.OUTPUT_DIR, f"servo_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Establish connection to servo controller"""
        try:
            self.logger.info(f"Attempting to connect to {self.port} at {self.baudrate} baud...")
            
            # Initialize serial connection
            self.uart = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=1,
                bytesize=8,
                timeout=self.timeout
            )
            
            if uservo:
                # Initialize servo control manager
                self.control = uservo.UartServoManager(self.uart)
                self.logger.info("Servo control manager initialized successfully")
            else:
                self.logger.warning("Using mock servo control (SDK not available)")
                self.control = MockServoManager()
            
            self.connected = True
            self.logger.info("Connection established successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {str(e)}")
            self.test_results['errors'].append(f"Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Close connection to servo controller"""
        try:
            if self.uart and self.uart.is_open:
                self.uart.close()
                self.logger.info("Serial connection closed")
            self.connected = False
        except Exception as e:
            self.logger.error(f"Error during disconnect: {str(e)}")
    
    def ping_servo(self, servo_id: int) -> bool:
        """Test if a servo is online and responding"""
        try:
            if not self.connected:
                return False
            
            is_online = self.control.ping(servo_id)
            if is_online:
                # Only log found servos to reduce noise
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.debug(f"Error pinging servo {servo_id}: {str(e)}")  # Changed to debug level
            self.test_results['errors'].append(f"Ping error for servo {servo_id}: {str(e)}")
            return False
    
    def read_servo_status(self, servo_id: int) -> Dict:
        """Read comprehensive status information from a servo"""
        status = {
            'servo_id': servo_id,
            'online': False,
            'angle': None,
            'voltage': None,
            'current': None,
            'power': None,
            'temperature': None,
            'status_flags': None,
            'errors': []
        }
        
        try:
            # Check if servo is online
            status['online'] = self.ping_servo(servo_id)
            
            if not status['online']:
                return status
            
            # Read angle
            try:
                status['angle'] = self.control.query_servo_angle(servo_id)
                self.logger.debug(f"Servo {servo_id} angle: {status['angle']}°")
            except Exception as e:
                status['errors'].append(f"Angle read error: {str(e)}")
            
            # Read voltage
            try:
                status['voltage'] = self.control.query_voltage(servo_id)
                self.logger.debug(f"Servo {servo_id} voltage: {status['voltage']}V")
            except Exception as e:
                status['errors'].append(f"Voltage read error: {str(e)}")
            
            # Read current
            try:
                status['current'] = self.control.query_current(servo_id)
                self.logger.debug(f"Servo {servo_id} current: {status['current']}A")
            except Exception as e:
                status['errors'].append(f"Current read error: {str(e)}")
            
            # Read power
            try:
                status['power'] = self.control.query_power(servo_id)
                self.logger.debug(f"Servo {servo_id} power: {status['power']}W")
            except Exception as e:
                status['errors'].append(f"Power read error: {str(e)}")
            
            # Read temperature
            try:
                status['temperature'] = self.control.query_temperature(servo_id)
                self.logger.debug(f"Servo {servo_id} temperature: {status['temperature']}°C")
            except Exception as e:
                status['errors'].append(f"Temperature read error: {str(e)}")
            
            # Check safety limits
            self.check_safety_limits(status)
            
        except Exception as e:
            self.logger.error(f"Error reading servo {servo_id} status: {str(e)}")
            status['errors'].append(f"Status read error: {str(e)}")
        
        return status
    
    def check_safety_limits(self, status: Dict):
        """Check if servo parameters are within safety limits"""
        servo_id = status['servo_id']
        
        if status['voltage'] and status['voltage'] > self.config.MAX_VOLTAGE:
            warning = f"Servo {servo_id}: Voltage {status['voltage']}V exceeds limit {self.config.MAX_VOLTAGE}V"
            self.logger.warning(warning)
            status['errors'].append(warning)
        
        if status['current'] and status['current'] > self.config.MAX_CURRENT:
            warning = f"Servo {servo_id}: Current {status['current']}A exceeds limit {self.config.MAX_CURRENT}A"
            self.logger.warning(warning)
            status['errors'].append(warning)
        
        if status['temperature'] and status['temperature'] > self.config.MAX_TEMPERATURE:
            warning = f"Servo {servo_id}: Temperature {status['temperature']}°C exceeds limit {self.config.MAX_TEMPERATURE}°C"
            self.logger.warning(warning)
            status['errors'].append(warning)
    
    def test_servo_movement(self, servo_id: int) -> Dict:
        """Test servo movement capabilities"""
        movement_results = {
            'servo_id': servo_id,
            'single_turn_test': [],
            'multi_turn_test': [],
            'movement_errors': []
        }
        
        try:
            self.logger.info(f"Testing movement for servo {servo_id}")
            
            # Test single turn movements
            for angle in self.config.ANGLE_TEST_RANGE:
                try:
                    self.logger.debug(f"Moving servo {servo_id} to {angle}°")
                    self.control.set_servo_angle(servo_id, angle, interval=1000)
                    time.sleep(1.5)  # Wait for movement completion
                    
                    # Verify position
                    actual_angle = self.control.query_servo_angle(servo_id)
                    error = abs(actual_angle - angle) if actual_angle is not None else float('inf')
                    
                    movement_results['single_turn_test'].append({
                        'target_angle': angle,
                        'actual_angle': actual_angle,
                        'error': error,
                        'success': error < 5.0  # 5 degree tolerance
                    })
                    
                    self.logger.debug(f"Target: {angle}°, Actual: {actual_angle}°, Error: {error}°")
                    
                except Exception as e:
                    error_msg = f"Single turn movement error at {angle}°: {str(e)}"
                    movement_results['movement_errors'].append(error_msg)
                    self.logger.error(error_msg)
            
            # Test multi-turn movements (if supported)
            for angle in self.config.MULTI_TURN_RANGE:
                try:
                    self.logger.debug(f"Multi-turn: Moving servo {servo_id} to {angle}°")
                    self.control.set_servo_angle(servo_id, angle, interval=2000, is_mturn=True)
                    time.sleep(2.5)  # Wait for movement completion
                    
                    # Verify position
                    actual_angle = self.control.query_servo_angle(servo_id)
                    error = abs(actual_angle - angle) if actual_angle is not None else float('inf')
                    
                    movement_results['multi_turn_test'].append({
                        'target_angle': angle,
                        'actual_angle': actual_angle,
                        'error': error,
                        'success': error < 10.0  # 10 degree tolerance for multi-turn
                    })
                    
                    self.logger.debug(f"Multi-turn Target: {angle}°, Actual: {actual_angle}°, Error: {error}°")
                    
                except Exception as e:
                    error_msg = f"Multi-turn movement error at {angle}°: {str(e)}"
                    movement_results['movement_errors'].append(error_msg)
                    self.logger.error(error_msg)
                    
        except Exception as e:
            error_msg = f"Movement test error for servo {servo_id}: {str(e)}"
            movement_results['movement_errors'].append(error_msg)
            self.logger.error(error_msg)
        
        return movement_results
    
    def discover_servos(self) -> List[int]:
        """Discover all available servos on the bus"""
        self.logger.info("Discovering available servos...")
        available_servos = []
        total_servos = len(self.config.DEFAULT_SERVO_IDS)
        
        for i, servo_id in enumerate(self.config.DEFAULT_SERVO_IDS):
            # Show progress for large ranges
            if i % 20 == 0:  # Progress every 20 servos
                progress = (i / total_servos) * 100
                self.logger.info(f"Progress: {progress:.1f}% ({i}/{total_servos}) - Testing servo ID {servo_id}")
            
            if self.ping_servo(servo_id):
                available_servos.append(servo_id)
                self.logger.info(f"Found servo at ID {servo_id}")
        
        self.test_results['available_servos'] = available_servos
        self.logger.info(f"Discovery complete. Found {len(available_servos)} servos: {available_servos}")
        
        return available_servos
    
    def run_comprehensive_test(self, test_movement: bool = True) -> Dict:
        """Run comprehensive test on all available servos"""
        self.logger.info("Starting comprehensive servo test...")
        
        if not self.connect():
            self.logger.error("Failed to establish connection. Aborting test.")
            return self.test_results
        
        try:
            # Discover available servos
            available_servos = self.discover_servos()
            
            if not available_servos:
                self.logger.warning("No servos found. Check connections and power supply.")
                # Generate empty test summary even when no servos found
                self.generate_test_summary()
                return self.test_results
            
            # Test each servo
            for servo_id in available_servos:
                self.logger.info(f"Testing servo {servo_id}...")
                
                # Read status
                status = self.read_servo_status(servo_id)
                self.test_results['servo_status'][servo_id] = status
                
                # Test movement if requested and servo is online
                if test_movement and status['online']:
                    movement_results = self.test_servo_movement(servo_id)
                    self.test_results['servo_status'][servo_id]['movement_test'] = movement_results
                
                self.logger.info(f"Servo {servo_id} test completed")
            
            # Generate test summary
            self.generate_test_summary()
            
        except Exception as e:
            error_msg = f"Test execution error: {str(e)}"
            self.logger.error(error_msg)
            self.test_results['errors'].append(error_msg)
        
        finally:
            self.disconnect()
        
        self.logger.info("Comprehensive test completed")
        return self.test_results
    
    def generate_test_summary(self):
        """Generate summary of test results"""
        summary = {
            'total_servos_tested': len(self.test_results['available_servos']),
            'online_servos': 0,
            'servos_with_errors': 0,
            'servos_with_safety_issues': 0,
            'movement_test_summary': {
                'servos_tested': 0,
                'successful_movements': 0,
                'failed_movements': 0
            }
        }
        
        for servo_id, status in self.test_results['servo_status'].items():
            if status['online']:
                summary['online_servos'] += 1
            
            if status['errors']:
                summary['servos_with_errors'] += 1
            
            # Check for safety issues
            if (status.get('voltage', 0) > self.config.MAX_VOLTAGE or
                status.get('current', 0) > self.config.MAX_CURRENT or
                status.get('temperature', 0) > self.config.MAX_TEMPERATURE):
                summary['servos_with_safety_issues'] += 1
            
            # Movement test summary
            if 'movement_test' in status:
                summary['movement_test_summary']['servos_tested'] += 1
                
                for test in status['movement_test']['single_turn_test']:
                    if test['success']:
                        summary['movement_test_summary']['successful_movements'] += 1
                    else:
                        summary['movement_test_summary']['failed_movements'] += 1
                
                for test in status['movement_test']['multi_turn_test']:
                    if test['success']:
                        summary['movement_test_summary']['successful_movements'] += 1
                    else:
                        summary['movement_test_summary']['failed_movements'] += 1
        
        self.test_results['test_summary'] = summary
        self.logger.info(f"Test Summary: {summary}")
    
    def save_results(self, filename_prefix: str = "servo_test"):
        """Save test results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON results
        json_filename = os.path.join(self.config.OUTPUT_DIR, f"{filename_prefix}_{timestamp}.json")
        with open(json_filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        self.logger.info(f"Results saved to {json_filename}")
        
        # Save CSV summary
        csv_filename = os.path.join(self.config.OUTPUT_DIR, f"{filename_prefix}_summary_{timestamp}.csv")
        self.save_csv_summary(csv_filename)
        
        # Save availability report
        availability_filename = os.path.join(self.config.OUTPUT_DIR, f"servo_availability_{timestamp}.txt")
        self.save_availability_report(availability_filename)
        
        return json_filename, csv_filename, availability_filename
    
    def save_csv_summary(self, filename: str):
        """Save servo status summary to CSV"""
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['servo_id', 'online', 'angle', 'voltage', 'current', 'power', 'temperature', 'error_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for servo_id, status in self.test_results['servo_status'].items():
                writer.writerow({
                    'servo_id': servo_id,
                    'online': status['online'],
                    'angle': status.get('angle', 'N/A'),
                    'voltage': status.get('voltage', 'N/A'),
                    'current': status.get('current', 'N/A'),
                    'power': status.get('power', 'N/A'),
                    'temperature': status.get('temperature', 'N/A'),
                    'error_count': len(status.get('errors', []))
                })
        
        self.logger.info(f"CSV summary saved to {filename}")
    
    def save_availability_report(self, filename: str):
        """Save servo availability report"""
        with open(filename, 'w') as f:
            f.write("SERVO AVAILABILITY REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Test Date: {self.test_results['timestamp']}\n")
            f.write(f"Port: {self.test_results['port']}\n")
            f.write(f"Baudrate: {self.test_results['baudrate']}\n\n")
            
            f.write("SUMMARY:\n")
            f.write("-" * 20 + "\n")
            summary = self.test_results['test_summary']
            f.write(f"Total Servos Tested: {summary['total_servos_tested']}\n")
            f.write(f"Online Servos: {summary['online_servos']}\n")
            f.write(f"Servos with Errors: {summary['servos_with_errors']}\n")
            f.write(f"Servos with Safety Issues: {summary['servos_with_safety_issues']}\n\n")
            
            f.write("AVAILABLE SERVOS:\n")
            f.write("-" * 20 + "\n")
            for servo_id in self.test_results['available_servos']:
                status = self.test_results['servo_status'][servo_id]
                f.write(f"Servo ID {servo_id}: ")
                if status['online']:
                    f.write("AVAILABLE")
                    if status.get('angle') is not None:
                        f.write(f" (Angle: {status['angle']:.1f}°)")
                    if status.get('voltage') is not None:
                        f.write(f" (Voltage: {status['voltage']:.1f}V)")
                    if status.get('temperature') is not None:
                        f.write(f" (Temp: {status['temperature']:.0f}°C)")
                else:
                    f.write("OFFLINE")
                f.write("\n")
            
            f.write("\nSPACE ALLOCATION:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Servo ID Range Available: {min(self.config.DEFAULT_SERVO_IDS)} - {max(self.config.DEFAULT_SERVO_IDS)}\n")
            f.write(f"Used Servo IDs: {sorted(self.test_results['available_servos'])}\n")
            f.write(f"Free Servo IDs: {sorted(set(self.config.DEFAULT_SERVO_IDS) - set(self.test_results['available_servos']))}\n")
        
        self.logger.info(f"Availability report saved to {filename}")


class MockServoManager:
    """Mock servo manager for testing when SDK is not available"""
    
    def __init__(self):
        self.mock_servos = {0: True, 1: False, 2: True}  # Mock some servos as online
        self.mock_angles = {0: 0.0, 2: 45.0}
    
    def ping(self, servo_id: int) -> bool:
        return self.mock_servos.get(servo_id, False)
    
    def query_servo_angle(self, servo_id: int) -> float:
        return self.mock_angles.get(servo_id, 0.0)
    
    def query_voltage(self, servo_id: int) -> float:
        return 8.4  # Mock voltage
    
    def query_current(self, servo_id: int) -> float:
        return 0.5  # Mock current
    
    def query_power(self, servo_id: int) -> float:
        return 4.2  # Mock power
    
    def query_temperature(self, servo_id: int) -> float:
        return 35.0  # Mock temperature
    
    def set_servo_angle(self, servo_id: int, angle: float, **kwargs):
        if servo_id in self.mock_angles:
            self.mock_angles[servo_id] = angle


def main():
    """Main function to run comprehensive servo tests"""
    
    # Create servo tester with default settings
    tester = ServoTester()
    
    print("=" * 60)
    print("   FASHIONSTAR SERVO COMPREHENSIVE TEST SCRIPT")
    print("=" * 60)
    print(f"Port: {tester.port}")
    print(f"Baudrate: {tester.baudrate}")
    print(f"Testing Servo IDs: 0-{len(tester.config.DEFAULT_SERVO_IDS)-1} ({len(tester.config.DEFAULT_SERVO_IDS)} total)")
    print("Movement Tests: DISABLED (Motionless scan)")
    print("=" * 60)
    
    # Run comprehensive test WITHOUT movement
    results = tester.run_comprehensive_test(test_movement=False)
    
    # Save results
    json_file, csv_file, availability_file = tester.save_results()
    
    print("\n" + "=" * 60)
    print("   TEST COMPLETED")
    print("=" * 60)
    print(f"Servos Found: {len(results['available_servos'])}")
    if results['available_servos']:
        print(f"Found Servo IDs: {results['available_servos']}")
        print("Servo Details:")
        for servo_id in results['available_servos']:
            status = results['servo_status'][servo_id]
            details = [f"ID: {servo_id}"]
            if status.get('angle') is not None:
                details.append(f"Angle: {status['angle']:.1f}°")
            if status.get('voltage') is not None:
                details.append(f"Voltage: {status['voltage']:.1f}V")
            if status.get('temperature') is not None:
                details.append(f"Temp: {status['temperature']:.0f}°C")
            print(f"  - {' | '.join(details)}")
    else:
        print("No servos found - Check connections and power supply")
    print(f"Total Errors: {len(results['errors'])}")
    print("Results saved to:")
    print(f"  - {json_file}")
    print(f"  - {csv_file}")
    print(f"  - {availability_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
