from _pynetworktables import NetworkTables

import constants

# Will need to set with ip of roboRIO when on the robot
NetworkTables.initialize(server=constants.ROBOT_IP)
vision_table = NetworkTables.getDefault().getTable("Vision")
config_table = NetworkTables.getDefault().getTable("Vision Config")


def log_pos(tag_id, x, y, z):
    vision_table.getEntry(str(tag_id) + "x").setValue(float(x))
    vision_table.getEntry(str(tag_id) + "y").setValue(float(y))
    vision_table.getEntry(str(tag_id) + "z").setValue(float(z))


def log_looptime(time):
    vision_table.getEntry("Vision Looptime").setValue(time)


def log_camera_open(is_open):
    vision_table.getEntry("Is Camera Open").setValue(is_open)


def get_exposure():
    return config_table.getEntry("Exposure").getDouble()


def get_cam_type():
    return config_table.getEntry("Camera Type").getDouble()


def flush():
    NetworkTables.getDefault().flush()
