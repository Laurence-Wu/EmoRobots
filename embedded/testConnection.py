import serial
import time

# Use the correct port for your Arduino, usually '/dev/ttyACM0'
ARDUINO_PORT = "/dev/ttyACM0"

try:
    # Connect to the Arduino
    arduino = serial.Serial(port=ARDUINO_PORT, baudrate=9600, timeout=1)
    time.sleep(2) # Wait for the connection to establish

    print("Sending command 'd' to delay and flash...")
    
    # Send the 'd' character as bytes
    arduino.write(b'd')
    
    arduino.close()
    print("Command sent successfully.")

except serial.SerialException:
    print(f"Error: Could not open port {ARDUINO_PORT}. Is the Arduino connected?")