import sys
import math
import numpy as np
import open3d as o3d

def rotate_view(vis):
    ctr = vis.get_view_control()
    ctr.rotate(2.0, 0.0)
    return False


if __name__ == '__main__':
    args = sys.argv
    input_filename = args[1]
    pcd = o3d.io.read_point_cloud(input_filename)
    o3d.visualization.draw_geometries_with_animation_callback([pcd], rotate_view)

