import pyrealsense2 as rs


class Gyro:
    first = True

    is_stopped = False

    # Constants of Integration
    gyro_angle_x = 0
    gyro_angle_y = 0
    gyro_angle_z = 0

    t_last = 0

    def __init__(self):
        # start the frames pipe
        p = rs.pipeline()
        conf = rs.config()
        conf.enable_stream(rs.stream.gyro)
        prof = p.start(conf)
        self.p = p

    # Gets the rotation for the x, y, and z dimensions in radians
    def get_rotation(self):
        return round(self.gyro_angle_x, 2), round(self.gyro_angle_y, 2), round(self.gyro_angle_z, 2)

    def stop(self):
        self.is_stopped = True

    def run_gyro(self):
        try:
            while not self.is_stopped:
                f = self.p.wait_for_frames()

                # gather IMU data
                gyro = f[0].as_motion_frame().get_motion_data()

                t = f.get_timestamp()

                # calculation for the first frame
                if self.first:
                    self.first = False
                    self.t_last = f.get_timestamp()

                    continue

                # calculation for the second frame onwards

                dt = (t - self.t_last) / 1000
                self.t_last = f.get_timestamp()
                # integrate gyro velocities

                self.gyro_angle_x = self.gyro_angle_x + round(gyro.x, 2) * dt
                self.gyro_angle_y = self.gyro_angle_y + round(gyro.y, 2) * dt
                self.gyro_angle_z = self.gyro_angle_z + round(gyro.z, 2) * dt


        finally:
            self.p.stop()
