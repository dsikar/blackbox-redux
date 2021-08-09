#
#
# Config file for point information  reader



# True  - Running on Pi
# False - Running on PC
IS_RUNNING_ON_PI = False


DISPLAY_POINT_REQUEST_PACKETS_DETAIL   = 0
DISPLAY_POINT_REQUEST_PACKETS_OVERVIEW = 1

PC_COM_PORT = "COM10"

# Mode to go through each configured loop device and log
# info to USB
POINT_INFO_SCAN = 1
# Checker mode
CHECKER_MODE    = 2

MODE_IS = POINT_INFO_SCAN
