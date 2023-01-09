import cv2

light_blue = (255, 120, 60)
white = (255, 255, 255)
width_px = 4


def annotate(frame, detection, n_pose):
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

    cv2.putText(frame, "x: " + str(n_pose[0]), (int(corners[1][0] + 50), int(corners[1][1])),
                cv2.FONT_HERSHEY_SIMPLEX, 1, white)
    cv2.putText(frame, "y: " + str(n_pose[1]), (int(corners[1][0] + 50), int(corners[1][1] + 30)),
                cv2.FONT_HERSHEY_SIMPLEX, 1, white)
    cv2.putText(frame, "z: " + str(n_pose[2]), (int(corners[1][0] + 50), int(corners[1][1] + 60)),
                cv2.FONT_HERSHEY_SIMPLEX, 1, white)
