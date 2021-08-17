import sys
import os
import json
import open3d as o3d

class VisualizerApp:
    def __init__(self, recorddir):
        self.load_app_config('app_config.json')
        self.recorddir = recorddir
        self.intrinsic = self.load_intrinic(recorddir + self.intrinsic_filename)
        self.extrinsic = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]]
        self.frame_count = self.frame_count_init

    def load_app_config(self, filename):
        input_file = open(filename, 'r')
        j = json.load(input_file)
        self.sub_dir_color = j['sub_dir_color']
        self.sub_dir_depth = j['sub_dir_depth']
        self.filename_zerofill = j['filename_zerofill']
        self.intrinsic_filename = j['intrinsic_filename']
        self.frame_count_init = j['frme_count_init']

    def load_intrinic(self, filename):
        input_file = open(filename, 'r')
        j = json.load(input_file)
        width = j['width']
        height = j['height']
        intrinsic_matrix = j['intrinsic_matrix']
        intrinsic = o3d.camera.PinholeCameraIntrinsic(
            width, height, intrinsic_matrix[0], intrinsic_matrix[4], intrinsic_matrix[6], intrinsic_matrix[7])
        return intrinsic

    def load_rgbd_images(self, frame_count):
        filename = str(frame_count).zfill(self.filename_zerofill)
        color = o3d.io.read_image(self.recorddir + self.sub_dir_color + filename + ".jpg")
        depth = o3d.io.read_image(self.recorddir + self.sub_dir_depth + filename + ".png")
        return color, depth

    def key_callback(self, vis):
        self.frame_count = self.frame_count + 1
        return True

    def process(self):
        color, depth = self.load_rgbd_images(self.frame_count)
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color, depth, depth_scale=1000.0, convert_rgb_to_intensity=False)
        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
            rgbd, self.intrinsic, self.extrinsic)

        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.register_key_callback(32, self.key_callback)
        vis.create_window(window_name="Point Cloud Visualizer",
                        width=800, height=800)
        vis.add_geometry(pcd)
        render_opt = vis.get_render_option()
        render_opt.point_size = 1.0

        if vis.poll_events():
            vis.update_renderer()

        while True:
            color, depth = self.load_rgbd_images(self.frame_count)
            rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
                color, depth, depth_scale=1000.0, convert_rgb_to_intensity=False)
            pcd_new = o3d.geometry.PointCloud.create_from_rgbd_image(
                rgbd, self.intrinsic, self.extrinsic)
            pcd.points = pcd_new.points
            pcd.colors = pcd_new.colors
            vis.update_geometry(pcd)
            if vis.poll_events():
                vis.update_renderer()
            else:
                break

        vis.destroy_window()

if __name__ == "__main__":
    args = sys.argv
    target_dir = args[1]
    app = VisualizerApp(target_dir.replace(os.sep,'/'))
    app.process()

