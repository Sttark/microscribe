# MicroScribe Angle Reader

A Python script for reading and displaying joint angles from a MicroScribe iL+ digitizer in real-time. The script interfaces with the device via USB and provides continuous angle readings for all joints relative to their home positions.

## Hardware Compatibility

- **Digitizer**: MicroScribe iL+
- **Computer**: MacBook Pro
- **Connection**: USB

## Features

- Real-time reading of all joint angles
- Displays angles in degrees relative to home position
- Shows raw encoder values
- Monitors:
  - Axis 1: Base Joint
  - Axis 2: Shoulder Joint
  - Axis 3: Elbow Joint
  - Axis 4: Wrist Roll Joint
  - Axis 5: Wrist Flip Joint

## Requirements

- Python 3.x
- PyUSB library (`pip install pyusb`)

## Usage

1. Connect the MicroScribe iL+ to your MacBook Pro via USB
2. Run the script:
   ```bash
   python read_angles.py
   ```
3. The script will continuously display the angles for each joint
4. Press Ctrl+C to stop the program

## Technical Details

The script uses the following USB parameters to communicate with the device:
- Vendor ID: 0x0563
- Product ID: 0x0053

Joint angles are calculated using encoder values relative to predefined home positions with specific resolutions for each axis.

## Future Work

### Forward Kinematics Implementation
- Implement calculations to solve for X, Y, and Z coordinates using kinematic dimensions
- Convert joint angles to end-effector position in 3D space
- Validate position calculations against known reference points

### OnShape Integration
- Develop USB signal detection for the handheld remote button press
- Use button press signal as trigger for automatic point capture
- Implement automatic keystroke generation to input points into OnShape's MicroScribe 3D Points FeatureScript
- Create seamless workflow between physical measurements and CAD model
- Add configurable keystroke mappings for different OnShape operations
- Include error checking and validation for point data transfer
- Provide feedback mechanism to confirm successful point capture and transfer
