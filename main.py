import threading
import time

import cv2
import numpy as np
import pyrealsense2 as rs
from pupil_apriltags import Detector

import constants
import graphics
import gyro
import network
import pose

# Camera Setup
camera = cv2.VideoCapture(constants.CAMERA_PORT)
camera.set(cv2.CAP_PROP_EXPOSURE, constants.CAMERA_EXPOSURE)

tag_detector = Detector(families="tag36h11", nthreads=4)

# Gyro Setup
r_gyro = gyro.Gyro()
gyro_thread = threading.Thread(target=r_gyro.run_gyro)
gyro_thread.start()

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

# Main Control Loop
while True:

    network.log_camera_open(camera.isOpened())

    rs_frames = pipeline.wait_for_frames()

    # Start of profiling
    start_time = time.time()

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

    # initialize the normalized and averaged pose
    n_pose_sum = (0, 0, 0)
    detection_count = 0

    for detection in detections:
        n_pose = pose.normalize_tag(detection, r_gyro.gyro_angle_x, r_gyro.gyro_angle_y, r_gyro.gyro_angle_z)

        # Adds pose to sum
        n_pose_sum = (n_pose_sum[0] + n_pose[0], n_pose_sum[1] + n_pose[1], n_pose_sum[2] + n_pose[2])

        if constants.ENABLE_GRAPHICS:
            graphics.annotate(color_frame, detection, n_pose)

        network.log_pos(detection.tag_id, n_pose[0], n_pose[1], n_pose[2])

        detection_count = detection_count + 1

    # Create the average pose after summing each pose
    if detection_count != 0:
        avg_n_pose = (n_pose_sum[0] / detection_count, n_pose_sum[1] / detection_count, n_pose_sum[2] / detection_count)

        # Log average pose
        network.log_pos("avg", avg_n_pose[0], avg_n_pose[1], avg_n_pose[2])

    if constants.ENABLE_GRAPHICS:
        cv2.imshow("View", color_frame)
        c = cv2.waitKey(1)

        # breaks out of loop if esc key is pressed
        if c == 27:
            r_gyro.stop()
            break

    # End of profiling
    network.log_looptime(time.time() - start_time)
    network.flush()

camera.release()
cv2.destryAllWindows()
