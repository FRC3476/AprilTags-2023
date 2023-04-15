import cv2
import pyrealsense2 as rs

light_blue = (60, 120, 255)
white = (255, 255, 255)
yellow = (0, 255, 255)
width_px = 4


def annotate(frame, detection):
    corners = detection.corners
    corner1 = (int(corners[0][0]), int(corners[0][1]))
    corner2 = (int(corners[1][0]), int(corners[1][1]))
    corner3 = (int(corners[2][0]), int(corners[2][1]))
    corner4 = (int(corners[3][0]), int(corners[3][1]))

    # Outline the tag
    cv2.line(frame, corner1, corner2, light_blue, width_px)
    cv2.line(frame, corner2, corner3, light_blue, width_px)
    cv2.line(frame, corner3, corner4, light_blue, width_px)
    cv2.line(frame, corner4, corner1, light_blue, width_px)

    cv2.putText(frame, "ID: " + str(detection.tag_id), (int(corners[1][0] + 10), int(corners[1][1])),
                cv2.FONT_HERSHEY_SIMPLEX, 1, white)


def draw_lines(frame, intrinsics, lines):
    # Iterates through groups of 6 coordinates representing the two 3D coordinates of the top and the bottom of the pole
    for i in range(0, len(lines), 6):
        # p1 and p2 represent the two end points of the pole projected into 2d
        p1 = rs.rs2_project_point_to_pixel(intrinsics, [lines[i], lines[i + 1], lines[i + 2]])
        p2 = rs.rs2_project_point_to_pixel(intrinsics, [lines[i + 3], lines[i + 4], lines[i + 5]])

        # Draws line onto the frame from the two 2D endpoints found
        cv2.line(frame, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), yellow, width_px)
