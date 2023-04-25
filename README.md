# AprilTags-2023
## AprilTags code used on the 2023 Code Orange robot Baja.

### Features
* Apriltags Detection and Pose Estimation
* Tag Filtering for Few False Positives
* Wide Array of Camera Support
* Live-Updatable Configurations
* FFMPEG Video Streaming
* Recording Video to Flash Drive
* Live Video Tag Annotation
* Comprehensive Error Handling and Logging

### Environment Details
* Tested to run on Ubuntu on a Beelink Mini PC
* Tested to run using a Realsense R445 Depth Camera and several generic webcams
* Flash drive should be used if video recording is desired. It will write to the first drive alphabetically sorted in the /media/{USERNAME}/ directory
* Program is expected to be run in the /var/www/AprilTags/AprilTags-2023 directory
* /var/www/AprilTags/logs file should exist in order for logs to be stored
* /var/www/AprilTags/ip.txt file should exist with the static IPV4 device ip stored inside if streaming is desired
* This program acts as a NetworkTables client that connects to a NetworkTables server running on an NI RoboRIO, so the proper roboRIO ip should be set in constants.py
* Program will send tag translation and orientation relative to the camera as key: tag_id, value: [x, y, z, x, y, z, w, latency] where indicies 3, 4, 5, and 6 represent a quaternion
* In normal use, program is to launch automatically on boot through a linux crontab and will automatically relaunch if an unhandled crash occurs using a bash script
* It is recommended that the device running the program boots on receiving power, has a static ip set, and has wifi disabled
* All external libraries must be installed independently
