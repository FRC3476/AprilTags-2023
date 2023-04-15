import time
import traceback

import cv2
import numpy as np
import pyrealsense2 as rs
from pupil_apriltags import Detector

import constants
import network


class Camera:

    # Depth cam for use with realsense depth cam (True or False)
    # exposure is an integer
    def __init__(self, camera_config):
        self.config = camera_config

        if self.config.cam_type == 0:
            # Depth Cam setup
            self.pipeline = rs.pipeline()
            cfg = rs.config()

            try:
                cfg.enable_stream(rs.stream.color, int(self.config.x_resolution), int(self.config.y_resolution),
                                  rs.format.rgb8, int(self.config.framerate))
                profile = self.pipeline.start(cfg)
            except Exception:
                network.send_status("Error: Could not enable depth camera stream. " + str(traceback.format_exc()))
                raise Exception("Error: Could not enable depth camera stream.")

            # Set realsense exposure
            try:
                s = profile.get_device().query_sensors()[1]
                s.set_option(rs.option.exposure, self.config.exposure)
            except Exception:
                network.send_status(
                    "Error: Invalid exposure: " + str(self.config.exposure) + " " + str(traceback.format_exc()))
                raise Exception("Error: Invalid exposure: " + str(self.config.exposure))

            # Gets camera intrinsics
            try:
                intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
                self.intr = intr

            except Exception:
                network.send_status("Error: Could not find depth camera intrinsics. " + str(traceback.format_exc()))
                raise Exception("Error: Could not find depth camera intrinsics.")

            self.fx = intr.fx
            self.fy = intr.fy
            self.cx = intr.width / 2.0
            self.cy = intr.height / 2.0

        elif self.config.cam_type == 1:
            # Camera Setup
            try:
                self.camera = cv2.VideoCapture(self.config.port)
            except Exception:
                network.send_status("Error: Invalid port: " + str(self.config.port) + " " + str(traceback.format_exc()))
                raise Exception("Error: Invalid port: " + str(self.config.port))

            try:
                self.camera.set(cv2.CAP_PROP_EXPOSURE, self.config.exposure)
            except Exception:
                network.send_status(
                    "Error: Invalid exposure: " + str(self.config.exposure) + " " + str(traceback.format_exc()))
                raise Exception("Error: Invalid exposure: " + str(self.config.exposure))

            try:
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.x_resolution)
            except Exception:
                network.send_status(
                    "Error: Invalid X Resolution: " + str(self.config.x_resolution) + " " + str(traceback.format_exc()))
                raise Exception("Error: Invalid X Resolution: " + str(self.config.x_resolution))

            try:
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.y_resolution)
            except Exception:
                network.send_status(
                    "Error: Invalid Y Resolution: " + str(self.config.y_resolution) + " " + str(traceback.format_exc()))
                raise Exception("Error: Invalid Y Resolution: " + str(self.config.y_resolution))

            try:
                self.camera.set(cv2.CAP_PROP_FPS, self.config.framerate)
            except Exception:
                network.send_status(
                    "Error: Invalid framerate: " + str(self.config.framerate) + " " + str(traceback.format_exc()))
                raise Exception("Error: Invalid framerate: " + str(self.config.framerate))

            # Camera intrinsics
            self.fx = self.config.fx
            self.fy = self.config.fy
            self.cx = self.config.cx
            self.cy = self.config.cy
        else:
            # Not 0 or 1
            network.send_status(
                "Error: Invalid camera type: " + str(self.config.cam_type) + " " + str(traceback.format_exc()))
            raise Exception("Error: Invalid camera type: " + str(self.config.cam_type))

        try:
            self.tag_detector = Detector(families=constants.TAG_FAMILY, nthreads=self.config.threads)
        except Exception:
            network.send_status(
                "Error: Invalid number of threads: " + str(self.config.threads) + " " + str(traceback.format_exc()))
            raise Exception("Error: Invalid number of threads: " + str(self.config.threads))

    # Returns detections along with timestamp
    def process_frame(self):

        if self.config.cam_type == 0:

            # Wait for frames
            rs_frames = self.pipeline.wait_for_frames()

            timestamp = rs_frames.get_timestamp()

            # Get color frame
            rs_color_frame = rs_frames.get_color_frame()

            # Check if the frame is ready
            if not rs_color_frame:
                raise Exception("Could not get color frame from depth camera.")

            # Convert to image that is usable by open-cv
            color_frame = np.asanyarray(rs_color_frame.get_data())

            # Convert to grayscale or processing
            gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)

        else:
            # Receive Frames
            ret, frame = self.camera.read()

            timestamp = time.time()

            # Check if the frame is ready
            if not ret:
                raise Exception("Could not get frame from non-depth camera.")

            # Convert to grayscale or processing
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        detections = self.tag_detector.detect(img=gray_frame, estimate_tag_pose=True,
                                              camera_params=(self.fx, self.fy, self.cx, self.cy),
                                              tag_size=constants.TAG_SIZE_M)
        return detections, timestamp, color_frame

    def terminate(self):
        try:
            if self.config.cam_type == 0:
                self.pipeline.stop()
            elif self.config.cam_type == 1:
                self.camera.terminate()
            else:
                network.send_satus(
                    "Error: Tried to terminate invalid camera type:  " + str(self.config.cam_type) + " " + str(
                        traceback.format_exc()))
        except Exception:
            network.send_status("Error: Failed to terminate camera." + str(traceback.format_exc()))
            raise Exception("Error: Failed to terminate camera.")
