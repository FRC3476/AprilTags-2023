# Offsets for each tag around the field to make their orgins at the same place and normalize them
# Format is (X_OFFSET, X_NORMALIZATION, Y_OFFSET, Y_NORMALIZATION, Z_OFFSET, Z_NORMALIZATION)
import math

# X, Y, and Z coordinates of the tag
offset_map = {
    -1: (0, 0, 0),
    0: (0, 0, 0),
    1: (0, 0, 0),
    2: (0, 0, 0),
    3: (0, 0, 0),
    4: (0, 0, 0)
}

offset_map.setdefault(-1)


# Find coordinates of tag (normalized to 0-1) (Orgin is left, bottom, far)
def normalize_tag(detection, pitch, yaw, roll):
    sin = math.sin(-yaw)
    cos = math.cos(-yaw)

    x_pos = (detection.pose_t[0] * cos) - (detection.pose_t[2] * sin)
    y_pos = detection.pose_t[1]
    z_pos = (detection.pose_t[2] * cos) + (detection.pose_t[0] * sin)

    try:
        offsets = offset_map[detection.tag_id]
    except KeyError:
        offsets = offset_map[-1]

    return round(float(x_pos + offsets[0]), 3), round(float(y_pos + offsets[1]), 3), round(float(z_pos + offsets[2]), 3)
