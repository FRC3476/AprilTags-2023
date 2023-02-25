import socket
import time

import imagezmq
import imutils

import camera
import cameraconfig
import graphics
import network

initialize = True
first_initialization = True
first_cam_initialization = True

hostName = socket.gethostname()

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

            if cam.config.do_stream:
                sender = imagezmq.ImageSender(
                    connect_to="tcp://" + str(cam_config.stream_ip) + ":" + str(cam_config.stream_port))
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
        detections, timestamp, color_frame = cam.process_frame()
    except Exception:
        # Go back to the top of the loop if failed
        # Tries to reinitialize the camera if it could not find a frame
        initialize = True
        continue

    for detection in detections:

        if detection.hamming == 0 and detection.tag_id >= 1 and detection.tag_id <= 8 and detection.decision_margin > 1:
            # Annotate and send the stream if set to true
            if cam.config.do_stream:
                graphics.annotate(color_frame, detection)

            network.log_pos(detection.tag_id, detection.pose_t[0], detection.pose_t[1], detection.pose_t[2],
                            detection.pose_R, timestamp)

    if cam.config.do_stream:
        # Send the gray_frame over camera stream
        try:
            send_frame = imutils.resize(color_frame, width=640, height=400)
            sender.send_image(hostName, send_frame)
        except:
            network.send_status("Error: Could not send frame to camera server.")
            initialize = True
            continue

    # End of profiling
    network.log_looptime(time.time() - start_time)
    network.flush()
