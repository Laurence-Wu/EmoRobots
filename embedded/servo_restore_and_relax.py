#!/usr/bin/env python3
'''
伺服舵机复位和放松脚本
> Servo Position Restore and Relax Script <
--------------------------------------------------
 * 作者: Generated for EmoRobots Project
 * 功能: 恢复伺服舵机位置并设置为放松状态
 * 更新时间: 2025/07/25
--------------------------------------------------
'''

import os
import sys
import time
import json
import serial
import logging
from datetime import datetime

# Add the servo SDK path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    import fashionstar_uart_sdk as uservo
except ImportError:
    print("Warning: fashionstar_uart_sdk not found. You may need to install or copy the SDK file.")
    print("Continuing with mock implementation for testing purposes...")
    uservo = None

class ServoRestoreConfig:
    """Configuration for servo restore operations"""
    
    # Serial port settings
    DEFAULT_PORT = '/dev/tty.usbserial-14210'
    DEFAULT_BAUDRATE = 1000000
    DEFAULT_TIMEOUT = 0.1
    
    # Restore positions (angle in degrees)
    RESTORE_POSITIONS = {
        0: 0.0,    # Servo 0 to 0 degrees
        1: 0.0,    # Servo 1 to 0 degrees
        # Add more servos as needed
    }
    
    # Movement parameters
    MOVE_INTERVAL = 2000  # Movement time in milliseconds
    SETTLE_TIME = 2.5     # Time to wait for movement completion
    
    # Damping power (0 = fully relaxed, 1000 = maximum holding power)
    DAMPING_POWER = 0     # 0 for completely relaxed

class ServoRestorer:
    """Servo position restoration and relaxation class"""
    
    def __init__(self, port: str = None, baudrate: int = None):
        self.config = ServoRestoreConfig()
        self.port = port or self.config.DEFAULT_PORT
        self.baudrate = baudrate or self.config.DEFAULT_BAUDRATE
        
        # Initialize logging
        self.setup_logging()
        
        # Initialize serial connection
        self.uart = None
        self.control = None
        self.connected = False
        
        # Track found servos
        self.available_servos = []
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Establish connection to servo controller"""
        try:
            self.logger.info(f"Connecting to {self.port} at {self.baudrate} baud...")
            
            self.uart = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=1,
                bytesize=8,
                timeout=self.config.DEFAULT_TIMEOUT
            )
            
            if uservo:
                self.control = uservo.UartServoManager(self.uart)
                self.logger.info("Servo control manager initialized")
            else:
                self.logger.warning("Using mock servo control (SDK not available)")
                self.control = MockServoManager()
            
            self.connected = True
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Close connection"""
        try:
            if self.uart and self.uart.is_open:
                self.uart.close()
                self.logger.info("Connection closed")
            self.connected = False
        except Exception as e:
            self.logger.error(f"Disconnect error: {str(e)}")
    
    def find_available_servos(self, servo_ids: list = None) -> list:
        """Find available servos"""
        if servo_ids is None:
            servo_ids = list(self.config.RESTORE_POSITIONS.keys())
        
        available = []
        self.logger.info("Scanning for available servos...")
        
        for servo_id in servo_ids:
            try:
                if self.control.ping(servo_id):
                    available.append(servo_id)
                    self.logger.info(f"Found servo ID {servo_id}")
                else:
                    self.logger.warning(f"Servo ID {servo_id} not responding")
            except Exception as e:
                self.logger.error(f"Error checking servo {servo_id}: {str(e)}")
        
        self.available_servos = available
        self.logger.info(f"Found {len(available)} available servos: {available}")
        return available
    
    def get_current_position(self, servo_id: int) -> float:
        """Get current servo position"""
        try:
            angle = self.control.query_servo_angle(servo_id)
            self.logger.info(f"Servo {servo_id} current position: {angle:.1f}°")
            return angle
        except Exception as e:
            self.logger.error(f"Error reading position for servo {servo_id}: {str(e)}")
            return None
    
    def move_to_position(self, servo_id: int, target_angle: float) -> bool:
        """Move servo to target position"""
        try:
            current_angle = self.get_current_position(servo_id)
            if current_angle is None:
                return False
            
            self.logger.info(f"Moving servo {servo_id} from {current_angle:.1f}° to {target_angle:.1f}°")
            
            # Send movement command
            success = self.control.set_servo_angle(
                servo_id, 
                target_angle, 
                interval=self.config.MOVE_INTERVAL
            )
            
            if success:
                self.logger.info(f"Movement command sent to servo {servo_id}")
                # Wait for movement completion
                time.sleep(self.config.SETTLE_TIME)
                
                # Verify final position
                final_angle = self.get_current_position(servo_id)
                if final_angle is not None:
                    error = abs(final_angle - target_angle)
                    if error < 5.0:  # 5 degree tolerance
                        self.logger.info(f"Servo {servo_id} reached target position (error: {error:.1f}°)")
                        return True
                    else:
                        self.logger.warning(f"Servo {servo_id} position error: {error:.1f}°")
                        return False
            else:
                self.logger.error(f"Failed to send movement command to servo {servo_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error moving servo {servo_id}: {str(e)}")
            return False
    
    def set_damping_mode(self, servo_id: int, power: int = 0) -> bool:
        """Set servo to damping (relaxed) mode"""
        try:
            success = self.control.set_damping(servo_id, power)
            if success:
                if power == 0:
                    self.logger.info(f"Servo {servo_id} set to fully relaxed mode")
                else:
                    self.logger.info(f"Servo {servo_id} set to damping mode (power: {power})")
                return True
            else:
                self.logger.error(f"Failed to set damping mode for servo {servo_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting damping mode for servo {servo_id}: {str(e)}")
            return False
    
    def restore_and_relax_servo(self, servo_id: int) -> bool:
        """Restore servo position and set to relaxed state"""
        if servo_id not in self.config.RESTORE_POSITIONS:
            self.logger.warning(f"No restore position defined for servo {servo_id}")
            return False
        
        target_position = self.config.RESTORE_POSITIONS[servo_id]
        
        # Step 1: Move to restore position
        self.logger.info(f"Step 1: Restoring servo {servo_id} to {target_position}°")
        if not self.move_to_position(servo_id, target_position):
            self.logger.error(f"Failed to restore position for servo {servo_id}")
            return False
        
        # Step 2: Set to relaxed mode
        self.logger.info(f"Step 2: Setting servo {servo_id} to relaxed mode")
        if not self.set_damping_mode(servo_id, self.config.DAMPING_POWER):
            self.logger.error(f"Failed to set relaxed mode for servo {servo_id}")
            return False
        
        self.logger.info(f"Servo {servo_id} successfully restored and relaxed")
        return True
    
    def restore_all_servos(self):
        """Restore all available servos"""
        if not self.connected:
            self.logger.error("Not connected to servo controller")
            return False
        
        # Find available servos
        available_servos = self.find_available_servos()
        
        if not available_servos:
            self.logger.warning("No servos found to restore")
            return False
        
        success_count = 0
        total_servos = len(available_servos)
        
        self.logger.info(f"Starting restoration process for {total_servos} servos...")
        
        for servo_id in available_servos:
            self.logger.info(f"\n--- Processing Servo {servo_id} ---")
            if self.restore_and_relax_servo(servo_id):
                success_count += 1
            else:
                self.logger.error(f"Failed to process servo {servo_id}")
            
            # Small delay between servos
            time.sleep(0.5)
        
        self.logger.info(f"\n--- Restoration Complete ---")
        self.logger.info(f"Successfully processed: {success_count}/{total_servos} servos")
        
        if success_count == total_servos:
            self.logger.info("All servos restored and relaxed successfully!")
            return True
        else:
            self.logger.warning(f"{total_servos - success_count} servos failed to restore")
            return False
    
    def emergency_relax_all(self):
        """Emergency function to relax all found servos without position restore"""
        if not self.connected:
            self.logger.error("Not connected to servo controller")
            return False
        
        # Find available servos with broader scan
        self.logger.info("Emergency relax mode - scanning for all servos...")
        available_servos = []
        
        # Scan more servo IDs for emergency mode
        for servo_id in range(10):  # Check first 10 servo IDs
            try:
                if self.control.ping(servo_id):
                    available_servos.append(servo_id)
                    self.logger.info(f"Found servo ID {servo_id}")
            except:
                pass
        
        if not available_servos:
            self.logger.warning("No servos found for emergency relax")
            return False
        
        self.logger.info(f"Emergency relaxing {len(available_servos)} servos...")
        
        for servo_id in available_servos:
            try:
                self.set_damping_mode(servo_id, 0)
                self.logger.info(f"Emergency relaxed servo {servo_id}")
            except Exception as e:
                self.logger.error(f"Failed to relax servo {servo_id}: {str(e)}")
        
        self.logger.info("Emergency relax complete")
        return True


class MockServoManager:
    """Mock servo manager for testing"""
    
    def __init__(self):
        self.positions = {0: -90.5, 1: -108.9}
    
    def ping(self, servo_id: int) -> bool:
        return servo_id in self.positions
    
    def query_servo_angle(self, servo_id: int) -> float:
        return self.positions.get(servo_id, 0.0)
    
    def set_servo_angle(self, servo_id: int, angle: float, **kwargs) -> bool:
        if servo_id in self.positions:
            self.positions[servo_id] = angle
            return True
        return False
    
    def set_damping(self, servo_id: int, power: int) -> bool:
        return servo_id in self.positions


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Servo Restore and Relax Script')
    parser.add_argument('--port', type=str, help='Serial port')
    parser.add_argument('--emergency', action='store_true', help='Emergency relax mode (no position restore)')
    parser.add_argument('--servo-id', type=int, help='Restore specific servo ID only')
    
    args = parser.parse_args()
    
    # Create restorer
    restorer = ServoRestorer(port=args.port)
    
    print("=" * 60)
    print("   SERVO POSITION RESTORE AND RELAX SCRIPT")
    print("=" * 60)
    print(f"Port: {restorer.port}")
    print(f"Baudrate: {restorer.baudrate}")
    
    if args.emergency:
        print("Mode: EMERGENCY RELAX (no position restore)")
    else:
        print("Mode: RESTORE AND RELAX")
        print(f"Restore positions: {restorer.config.RESTORE_POSITIONS}")
    
    print("=" * 60)
    
    # Connect to servos
    if not restorer.connect():
        print("Failed to connect to servo controller")
        return
    
    try:
        if args.emergency:
            # Emergency relax mode
            restorer.emergency_relax_all()
        elif args.servo_id is not None:
            # Restore specific servo
            restorer.find_available_servos([args.servo_id])
            if args.servo_id in restorer.available_servos:
                restorer.restore_and_relax_servo(args.servo_id)
            else:
                print(f"Servo {args.servo_id} not found or not responding")
        else:
            # Restore all configured servos
            restorer.restore_all_servos()
            
    finally:
        restorer.disconnect()
    
    print("=" * 60)
    print("   OPERATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
