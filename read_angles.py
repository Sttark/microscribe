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

# Link lengths and offsets in millimeters (calculated from provided coordinates)
BASE_HEIGHT = 210.82    # Height of first joint from base
L1 = 362.32            # First joint to second joint
L2 = 322.43            # Second joint to third joint
L3 = 135.97            # Third joint to probe tip

def counts_to_degrees(counts, home_counts, resolution):
    # Convert the difference from home position to degrees
    diff = counts - home_counts
    return (diff * 360.0) / resolution

def angles_to_xyz(theta1, theta2, theta3, theta4, theta5):
    """
    Convert joint angles to XYZ coordinates
    theta1: base rotation (degrees)
    theta2: shoulder angle (degrees)
    theta3: elbow angle (degrees)
    theta4: wrist roll (degrees)
    theta5: wrist flip (degrees)
    Returns: (x, y, z) coordinates in millimeters
    """
    # Convert angles to radians
    t1 = math.radians(theta1)
    t2 = math.radians(theta2)
    t3 = math.radians(theta3)
    t4 = math.radians(theta4)
    t5 = math.radians(theta5)
    
    # Start from base height
    z = BASE_HEIGHT
    
    # Calculate first joint position (already included in BASE_HEIGHT)
    x1 = 0
    y1 = 0
    
    # Calculate second joint position
    x2 = L1 * math.cos(t2)
    z2 = z + L1 * math.sin(t2)
    
    # Calculate third joint position
    x3 = x2 + L2 * math.cos(t2 + t3)
    z3 = z2 + L2 * math.sin(t2 + t3)
    
    # Calculate probe tip position including wrist angles
    x4 = x3 + L3 * math.cos(t2 + t3 + t4) * math.cos(t5)
    z4 = z3 + L3 * math.sin(t2 + t3 + t4) * math.cos(t5)
    
    # Rotate around base to get final X,Y coordinates
    x = x4 * math.cos(t1)
    y = x4 * math.sin(t1)
    z = z4
    
    return (x, y, z)

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
    print("Displaying angles and XYZ coordinates:")
    
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
            
            # Calculate XYZ coordinates
            x, y, z = angles_to_xyz(axis1_angle, axis2_angle, axis3_angle, 
                                  axis4_angle, axis5_angle)
            
            print("\033[2J\033[H")  # Clear screen and move to top
            print(f"Joint angles relative to home:")
            print(f"  Base Joint:        {axis1_angle:7.2f}° ({values[0]})")
            print(f"  Shoulder Joint:    {axis2_angle:7.2f}° ({values[1]})")
            print(f"  Elbow Joint:       {axis3_angle:7.2f}° ({values[2]})")
            print(f"  Wrist Roll Joint:  {axis4_angle:7.2f}° ({values[3]})")
            print(f"  Wrist Flip Joint:  {axis5_angle:7.2f}° ({values[4]})")
            print("-" * 40)
            print(f"Probe tip position:")
            print(f"  X: {x:7.2f} mm")
            print(f"  Y: {y:7.2f} mm") 
            print(f"  Z: {z:7.2f} mm")
            print("-" * 40)
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping data capture.")
