import usb.core
import usb.util
import time
import struct
import math

# Define Vendor and Product IDs
VENDOR_ID = 0x0563
PRODUCT_ID = 0x0053

# Home position encoder values (0 degrees)
HOME_AXIS1 = 15971      # Base Joint
HOME_AXIS2 = 24861     # Shoulder Joint
HOME_AXIS3 = 26802     # Elbow Joint
HOME_AXIS4 = 16387     # Wrist Roll Joint
HOME_AXIS5 = 13068     # Wrist Flip Joint

# Encoder resolutions
COUNTS_AXIS1 = 65536    # First axis (Base Joint)
COUNTS_AXIS2 = 65536    # Second axis (Shoulder Joint)
COUNTS_AXIS3 = 32768    # Third axis (Elbow Joint)
COUNTS_AXIS4 = 16384    # Fourth axis (Wrist Roll Joint)
COUNTS_AXIS5 = 16384    # Fifth axis (Wrist Flip Joint)

def counts_to_degrees(counts, home_counts, resolution):
    # Convert the difference from home position to degrees
    diff = counts - home_counts
    return (diff * 360.0) / resolution

def parse_packet(data):
    if len(data) != 33:
        raise ValueError("Invalid packet length")
    
    data = list(data)
    values = []
    for i in range(2, 29, 4):
        value = struct.unpack('<i', bytes(data[i:i+4]))[0]
        values.append(value)
    
    return values

# Main program
device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
if device is None:
    print("MicroScribe device not found.")
else:
    print("MicroScribe device found!")
    
    if device.is_kernel_driver_active(0):
        device.detach_kernel_driver(0)
    
    device.set_configuration()
    print("Device configuration set.")
    print("Displaying angles relative to home position:")
    
    try:
        while True:
            data = device.read(0x81, 33)
            values = parse_packet(data)
            
            # Calculate angles relative to home position using correct resolutions
            axis1_angle = counts_to_degrees(values[0], HOME_AXIS1, COUNTS_AXIS1)
            axis2_angle = counts_to_degrees(values[1], HOME_AXIS2, COUNTS_AXIS2)
            axis3_angle = counts_to_degrees(values[2], HOME_AXIS3, COUNTS_AXIS3)
            axis4_angle = counts_to_degrees(values[3], HOME_AXIS4, COUNTS_AXIS4)
            axis5_angle = counts_to_degrees(values[4], HOME_AXIS5, COUNTS_AXIS5)
            
            print("\033[2J\033[H")  # Clear screen and move to top
            print(f"Joint angles relative to home:")
            print(f"  Base Joint:        {axis1_angle:7.2f}° ({values[0]})")
            print(f"  Shoulder Joint:    {axis2_angle:7.2f}° ({values[1]})")
            print(f"  Elbow Joint:       {axis3_angle:7.2f}° ({values[2]})")
            print(f"  Wrist Roll Joint:  {axis4_angle:7.2f}° ({values[3]})")
            print(f"  Wrist Flip Joint:  {axis5_angle:7.2f}° ({values[4]})")
            print("-" * 40)
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping data capture.")
