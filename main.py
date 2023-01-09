import time

import cv2
import numpy as np
import pyrealsense2 as rs
from pupil_apriltags import Detector

import constants
import graphics
import network

if constants.USE_DEPTH_CAM:
    # Depth Camera Setup
    pipeline = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
    profile = pipeline.start(cfg)

    # Set realsense exposure
    s = profile.get_device().query_sensors()[1]
    s.set_option(rs.option.exposure, constants.CAMERA_EXPOSURE)

    # Gets camera intrinsics
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
else:
    # Camera Setup
    camera = cv2.VideoCapture(constants.CAMERA_PORT)
    camera.set(cv2.CAP_PROP_EXPOSURE, constants.CAMERA_EXPOSURE)

tag_detector = Detector(families="tag36h11", nthreads=4)

# Main Control Loop
while True:

    # Start of profiling
    start_time = time.time()

    if (constants.USE_DEPTH_CAM):
        rs_frames = pipeline.wait_for_frames()

        rs_color_frame = rs_frames.get_color_frame()

        if not rs_color_frame:
            continue

        color_frame = np.asanyarray(rs_color_frame.get_data())

        # Convert to grayscale or processing
        gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)

        # Search for tags
        detections = tag_detector.detect(img=gray_frame, estimate_tag_pose=True,
                                         camera_params=(intr.fx, intr.fy, intr.width / 2.0, intr.height / 2.0),
                                         tag_size=.02)
    else:
        ret, frame = camera.read()
        # Convert to grayscale or processing
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Search for tags
        detections = tag_detector.detect(img=gray_frame, estimate_tag_pose=True,
                                         camera_params=(constants.CAM_FX, constants.CAM_FY, constants.CAM_WIDTH / 2.0,
                                                        constants.CAM_HEIGHT / 2.0), tag_size=.02)

    for detection in detections:

        if constants.ENABLE_GRAPHICS:
            graphics.annotate(color_frame, detection)

        network.log_pos(detection.tag_id, detection.pose_t[0], detection.pose_t[1], detection.pose_t[2])

    if constants.ENABLE_GRAPHICS:
        cv2.imshow("View", color_frame)
        c = cv2.waitKey(1)

    # breaks out of loop if esc key is pressed
    if c == 27:
        break

    # End of profiling
    network.log_looptime(time.time() - start_time)
    network.flush()

camera.release()
cv2.destryAllWindows()
