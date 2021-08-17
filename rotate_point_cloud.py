import sys
import math
import numpy as np
import open3d as o3d

if __name__ == '__main__':
    args = sys.argv
    input_filename = args[1]
    output_filename = args[2]
    rotate_x = math.radians(float(args[3]))
    rotate_y = math.radians(float(args[4]))
    rotate_z = math.radians(float(args[5]))

    pcd = o3d.io.read_point_cloud(input_filename)
    R = pcd.get_rotation_matrix_from_xyz((rotate_x, rotate_y, rotate_z))
    pcd.rotate(R, center=(0, 0, 0))
    o3d.io.write_point_cloud(output_filename, pcd)

