import sys
import open3d as o3d

if __name__ == "__main__":
    args = sys.argv
    pcd = o3d.io.read_point_cloud(args[1])

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Point Cloud Visualizer",
                    width=1280, height=960)
    vis.add_geometry(pcd)
    render_opt = vis.get_render_option()
    render_opt.point_size = 1.0

    while True:
        if vis.poll_events():
            vis.update_renderer()
        else:
            break

    vis.destroy_window()
