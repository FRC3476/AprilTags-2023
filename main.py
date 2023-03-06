import os
import socket
import time
from datetime import datetime

import cv2
import imagezmq
from ping3 import ping

import camera
import cameraconfig
import graphics
import network

initialize = True
first_initialization = True
first_cam_initialization = True
first_record = True

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

        except Exception:
            # Try again if camera failed to initialize
            # Next run needs to be in first_initialization mode because it may try to terminate an inproperly initialized camera
            first_initialization = True
            continue

        if cam.config.do_stream:
            try:
                # Make sure that the ip exists
                p = ping(cam_config.stream_ip)
                if (not p):
                    raise (Exception)
                # Connect to the image receiver
                sender = imagezmq.ImageSender(
                    connect_to="tcp://" + str(cam_config.stream_ip) + ":" + str(cam_config.stream_port))

                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(cam_config.encode_quality)]
            except Exception:
                network.send_status(
                    "Can not connect to: " + "tcp://" + str(cam_config.stream_ip) + ":" + str(cam_config.stream_port))
                continue

        if not first_record:
            video_file.release()

        if cam.config.record_video:
            # Check for user directory in media
            dirs = os.listdir("/media")

            if (len(dirs) > 0):
                # Check for drive plugged in
                userdirs = os.listdir("/media/" + str(dirs[0]))
            else:
                network.send_status("No user directory found for saving video to flash drive.")
                continue

            if (len(userdirs) > 0):
                drivename = "/media/" + str(dirs[0]) + "/" + str(userdirs[0]) + "/"
            else:
                network.send_status("No flash drive plugged in to store video.")
                continue

            hourminutesecond = str(datetime.now().strftime("%H%M%S"))
            video_file = cv2.VideoWriter(drivename + hourminutesecond + ".mp4",
                                         cv2.VideoWriter_fourcc(*"mp4v"), cam_config.framerate,
                                         (cam_config.x_resolution, cam_config.y_resolution))
            network.send_status("Recording Video As: " + str(datetime.now().strftime("%H%M%S") + ".mp4"))
            first_record = False

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

        if detection.hamming == 0 and detection.tag_id >= 1 and detection.tag_id <= 8 and detection.decision_margin > cam_config.decision_margin:
            # Annotate and send the stream if set to true
            if cam.config.do_stream or cam.config.record_video:
                graphics.annotate(color_frame, detection)

            network.log_pos(detection.tag_id, detection.pose_t[0], detection.pose_t[1], detection.pose_t[2],
                            detection.pose_R, timestamp)

    if cam.config.do_stream or cam.config.record_video:
        # Format image and send it
        send_frame = cv2.resize(color_frame,
                                (int(cam_config.x_resolution * .25), int(cam_config.y_resolution * .25)),
                                cv2.INTER_LINEAR)
        send_frame = cv2.cvtColor(send_frame, cv2.COLOR_RGB2BGR)

    if cam.config.do_stream:
        # Send the gray_frame over camera stream
        try:
            # Format image and send it
            send_frame = cv2.resize(color_frame,
                                    (int(cam_config.x_resolution * .25), int(cam_config.y_resolution * .25)),
                                    cv2.INTER_LINEAR)
            send_frame = cv2.cvtColor(send_frame, cv2.COLOR_RGB2BGR)

            result, encimage = cv2.imencode('.jpg', send_frame, encode_param)
            sender.send_image(hostName, encimage)
        except:
            network.send_status("Error: Could not send frame to camera server.")
            continue

    if cam.config.record_video:
        record_frame = cv2.cvtColor(color_frame, cv2.COLOR_RGB2BGR)
        video_file.write(record_frame)

    # End of profiling
    network.log_looptime(time.time() - start_time)
    network.flush()
