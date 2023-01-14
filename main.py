import time

import camera
import cameraconfig
import graphics
import network

initialize = True
cam_config = cameraconfig.Config()

# Main Control Loop
while True:
    start_time = time.time()

    if not network.is_connected():
        # If network check connection returns true, then we are not connected
        network.initialize()

    if initialize:
        try:
            if cam is None:
                # Camera has not been initialized before
                cam = camera.Camera(cam_config)
            else:
                # Terminate old camera if camera has been initialized before
                cam.terminate()
                cam = camera.Camera(cam_config)
        except Exception:
            # Try again if camera failed to initialize
            continue

        initialize = False

    # Check if camera settings changed
    if network.update_state.check_update():
        cam.config.update_config()
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
        print("test")

    # End of profiling
    network.log_looptime(time.time() - start_time)
    network.flush()
