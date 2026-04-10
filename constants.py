"""
文件名：constants.py
"""
# Control Commands
ENABLE = 0xF3
STOP = 0xFE

# Motion Commands (X Firmware)
VEL_CTRL = 0xF6      # Speed Mode
POS_CTRL = 0xFB      # Position Mode (Direct Speed Limit)
TORQUE_CTRL = 0xF5   # Torque Mode

# Read Commands
READ_CURRENT = 0x26  # Read Bus Current
READ_POSITION = 0x36 # Read Real-time Position
READ_STATUS = 0xF1

# System
REBOOT = 0x97

# Protocol
CHECK = 0x6B         # Fixed Checksum for X Firmware