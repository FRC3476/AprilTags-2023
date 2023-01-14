from _pynetworktables import NetworkTables

import constants
import update_state

# Will need to set with ip of roboRIO when on the robot
NetworkTables.initialize(server=constants.ROBOT_IP)
vision_table = NetworkTables.getDefault().getTable("Vision")
vision_misc_table = NetworkTables.getDefault().getTable("Vision Misc")
config_table = NetworkTables.getDefault().getTable("Vision Config")

update_state = update_state.UpdateState()


def initialize():
    NetworkTables.initialize(server=constants.ROBOT_IP)


# Returns true if connected
def is_connected():
    return vision_misc_table.getBoolean("Connection Flag", False)


def value_changed(key, value, isNew, t):
    # Table generation itself can trigger this, so it is excluded here
    send_status("Updating Config")
    update_state.schedule_update()


# Add listener
config_table.addEntryListener(value_changed)


def send_status(exception):
    vision_misc_table.getEntry("Latest Status").setString(str(exception))


def log_pos(tag_id, x, y, z, timestamp):
    vision_table.getEntry(str(tag_id) + ":x").setValue(float(x))
    vision_table.getEntry(str(tag_id) + ":y").setValue(float(y))
    vision_table.getEntry(str(tag_id) + ":z").setValue(float(z))
    vision_table.getEntry(str(tag_id) + ":" + str(timestamp))


def log_looptime(time):
    vision_misc_table.getEntry("Vision Looptime").setValue(time)


def get_exposure():
    return int(config_table.getEntry("Exposure").getDouble(150))


def get_cam_type():
    cam_type = config_table.getEntry("Camera Type").getDouble(0)

    # If invalid camera type
    if cam_type != 0 and cam_type != 1:
        send_status("Error: Invalid camera type: " + str(cam_type))
        return 0
    else:
        return cam_type


def get_port():
    return config_table.getEntry("Port").getDouble(0)


def get_x_res():
    return int(config_table.getEntry("X Resolution").getDouble(1280))


def get_y_res():
    return int(config_table.getEntry("Y Resolution").getDouble(800))


def get_framerate():
    return int(config_table.getEntry("Framerate").getDouble(30))


# Intrinsics only used here if not the realsense depth camera
def get_fx():
    return config_table.getEntry("fx").getDouble(480)


def get_fy():
    return config_table.getEntry("fy").getDouble(480)


def get_cx():
    return config_table.getEntry("cx").getDouble(640)


def get_cy():
    return config_table.getEntry("cy").getDouble(400)


def get_threads():
    return int(config_table.getEntry("Threads").getDouble(4))


def get_do_stream():
    return config_table.getEntry("Do Stream").getBoolean(False)


def flush():
    NetworkTables.getDefault().flush()
