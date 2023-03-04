# Default Values
import network


class Config:

    def __init__(self):
        self.update_config()

    def update_config(self):
        self.cam_type = network.get_cam_type()
        self.exposure = network.get_exposure()
        self.port = network.get_port()
        self.x_resolution = network.get_x_res()
        self.y_resolution = network.get_y_res()
        self.framerate = network.get_framerate()
        self.fx = network.get_fx()
        self.fy = network.get_fy()
        self.cx = network.get_cx()
        self.cy = network.get_cy()
        self.threads = network.get_threads()
        self.do_stream = network.get_do_stream()
        self.stream_port = network.get_stream_port()
        self.stream_ip = network.get_stream_ip()
        self.decision_margin = network.get_decision_margin()
        self.encode_quality = network.get_encode_quality()
