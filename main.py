import time

import cv2

import camera
import cameraconfig
import graphics
import network

initialize = True
first_initialization = True

# Main Control Loop
while True:
    start_time = time.time()

    if not network.is_connected():
        # If network check connection returns true, then we are not connected
        network.initialize()
        continue

    if initialize:
        try:
            if first_initialization:
                cam_config = cameraconfig.Config()
                first_initialization = False
            else:
                cam.terminate()
                cam_config.update_config()
        except Exception:
            continue

        try:
            # Create a new camera
            cam = camera.Camera(cam_config)
        except Exception:
            # Try again if camera failed to initialize
            # Next run needs to be in first_initialization mode because it may try to terminate an inproperly initialized camera
            first_initialization = True
            continue

        initialize = False

    # Check if camera settings changed
    if network.update_state.check_update():
        initialize = True
        continue

    # Get detections
    try:
        detections, gray_frame, timestamp = cam.process_frame()
    except Exception:
        # Go back to the top of the loop if failed
        continue

    for detection in detections:

        # Annotate and send the stream if set to true
        if cam.config.do_stream:
            graphics.annotate(gray_frame, detection)

        network.log_pos(detection.tag_id, detection.pose_t[0], detection.pose_t[1], detection.pose_t[2], timestamp)

    if cam.config.do_stream:
        # Send the gray_frame over camera stream
        cv2.imshow("Test", gray_frame)
        cv2.waitKey(1)

    # End of profiling
    network.log_looptime(time.time() - start_time)
    network.flush()
