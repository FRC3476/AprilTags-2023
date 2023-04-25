import os
import subprocess
import time
import traceback
from datetime import datetime

import cv2

import camera
import cameraconfig
import event_logger
import graphics
import network

timestamp = str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
with open("/var/www/AprilTags/logs/" + f"{timestamp}_log.txt", 'w') as write_file:
    initialize = True
    first_initialization = True
    first_cam_initialization = True
    first_record = True

    f = open("/var/www/AprilTags/ip.txt")
    ip = f.read()

    rtmp_url = "rtmp://" + str(ip[0:12]) + "/live/stream"

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
                event_logger.write_exception(write_file, traceback)
                continue

            try:
                # Create a new camera
                cam = camera.Camera(cam_config)
                event_logger.write_event(write_file, "Camera created!")
            except Exception:
                # Try again if camera failed to initialize
                # Next run needs to be in first_initialization mode because it may try to terminate an inproperly initialized camera
                event_logger.write_exception(write_file, traceback)
                first_initialization = True
                continue

            if cam_config.do_stream:
                command = ['ffmpeg',
                           '-y',
                           '-f', 'rawvideo',
                           '-vcodec', 'rawvideo',
                           '-pix_fmt', 'rgb24',
                           '-s', "{}x{}".format(cam_config.x_resolution, cam_config.y_resolution),
                           '-r', str(40),
                           '-i',
                           '-'] + "-c:v libx264 -preset fast -b:v 1M -bufsize 70000 -profile:v high -g 999999 -x264opts no-sliced-threads:nal-hrd=cbr -tune zerolatency -threads 1 -vsync 0 -flags2 fast -x264opts keyint=15".split(
                    ' ') + ['-pix_fmt', 'yuv420p',
                            '-s', "{}x{}".format(int(cam_config.x_resolution), int(cam_config.y_resolution)),
                            '-f', 'flv',
                            '-fflags', 'nobuffer',
                            '-listen', '1',
                            rtmp_url]

                # Runs this ffmpeg script in a subprocess
                p = subprocess.Popen(command, stdin=subprocess.PIPE)
                event_logger.write_event(write_file, "Stream Started")
                first_stream = False

            if not first_record:
                video_file.release()

            if cam_config.record_video:
                # Check for user directory in media
                dirs = os.listdir("/media")

                if (len(dirs) > 0):
                    # Check for drive plugged in
                    userdirs = os.listdir("/media/" + str(dirs[0]))
                else:
                    network.send_status("No user directory found for saving video to flash drive.")
                    event_logger.write_event(write_file, "No user directory found for saving video to flash drive.")
                    network.force_disable_recording()
                    continue

                if (len(userdirs) > 0):
                    drivename = "/media/" + str(dirs[0]) + "/" + str(userdirs[0]) + "/"
                else:
                    network.send_status("No flash drive plugged in to store video.")
                    event_logger.write_event(write_file, "No flash drive plugged in to store video.")
                    network.force_disable_recording()
                    continue

                hourminutesecond = str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))

                try:
                    video_file = cv2.VideoWriter(drivename + hourminutesecond + ".mkv",
                                                 cv2.VideoWriter_fourcc(*"mp4v"), cam_config.framerate,
                                                 (cam_config.x_resolution, cam_config.y_resolution))
                except Exception:
                    network.send_status("Could not write to flash drive file")
                    event_logger.write_exception(write_file, traceback)
                    network.force_disable_recording()

                network.send_status("Recording Video As: " + drivename + hourminutesecond + ".mkv")
                event_logger.write_event(write_file, "Recording Video As: " + drivename + hourminutesecond + ".mkv")
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
            network.send_status("Error when processing frames. " + str(traceback.format_exc()))
            # Go back to the top of the loop if failed
            # Tries to reinitialize the camera if it could not find a frame
            event_logger.write_exception(write_file, traceback)
            initialize = True
            continue

        for detection in detections:

            if detection.hamming == 0 and detection.tag_id >= 1 and detection.tag_id <= 8 and detection.decision_margin > cam_config.decision_margin:
                # Annotate and send the stream if set to true
                if cam.config.do_stream or cam.config.record_video:
                    graphics.annotate(color_frame, detection)

                network.log_pos(detection.tag_id, detection.pose_t[0], detection.pose_t[1], detection.pose_t[2],
                                detection.pose_R, timestamp)

        if cam_config.record_video:
            # Writes frame to video file
            record_frame = cv2.cvtColor(color_frame, cv2.COLOR_RGB2BGR)
            try:
                video_file.write(record_frame)
            except Exception as e:
                network.send_status("Could not write frame to file.")
                event_logger.write_exception(write_file, traceback)
                network.force_disable_recording()

        if cam_config.do_stream:
            # Writes frame to ffmpeg stream
            try:
                p.stdin.write(color_frame.tobytes())
            except (Exception):
                network.send_status("WARNING: Could not send frame to stream. " + str(traceback.format_exc()))
                event_logger.write_exception(write_file, traceback)

        # End of profiling
        network.log_looptime(time.time() - start_time)
        network.flush()
