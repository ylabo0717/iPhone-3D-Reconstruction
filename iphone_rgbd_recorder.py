import numpy as np
import cv2
from threading import Event
import os
import datetime
import json
from record3d import Record3DStream

ROOT_RECORD_DIR_NAME = os.getcwd().replace(os.sep,'/') + '/data/'

class RecorderApp:
    def __init__(self):
        self.load_app_config('app_config.json')
        self.event = Event()
        self.session = None
        self.activate = False
        self.recording = False
        self.recorddir_root = ROOT_RECORD_DIR_NAME
        if not os.path.exists(self.recorddir_root):
            os.makedirs(self.recorddir_root)

    def load_app_config(self, filename):
        input_file = open(filename, 'r')
        j = json.load(input_file)
        self.sub_dir_color = j['sub_dir_color']
        self.sub_dir_depth = j['sub_dir_depth']
        self.sub_dir_depth_resized = j['sub_dir_depth_resized']
        self.filename_zerofill = j['filename_zerofill']
        self.intrinsic_filename = j['intrinsic_filename']
        self.frame_count_init = j['frme_count_init']
        self.config_filename = j['config_filename']
        self.dir_name_format = j['dir_name_format']
        self.depth_colorize_fixed_range = j['depth_colorize_fixed_range']
        self.depth_colorize_min = j['depth_colorize_min']
        self.depth_colorize_max = j['depth_colorize_max']
        self.record_display_image = j['record_display_image']
        self.viewer_resize_factor = j['viewer_resize_factor']

    def on_new_frame(self):
        self.event.set()

    def on_stream_stopped(self):
        print('Stream stopped')
        self.activate = False
        raise RuntimeError('Stream stopped')

    def connect_to_device(self, dev_idx):
        print('Searching for devices')
        devs = Record3DStream.get_connected_devices()
        print('{} device(s) found'.format(len(devs)))
        for dev in devs:
            print('\tID: {}\n\tUDID: {}\n'.format(dev.product_id, dev.udid))

        if len(devs) <= dev_idx:
            raise RuntimeError('Cannot connect to device #{}, try different index.'
                               .format(dev_idx))

        self.activate = True
        dev = devs[dev_idx]
        self.session = Record3DStream()
        self.session.on_new_frame = self.on_new_frame
        self.session.on_stream_stopped = self.on_stream_stopped
        self.session.connect(dev)

    def make_record_dir(self):
        now = datetime.datetime.now()
        self.save_dir_name = now.strftime(self.dir_name_format) + "/"
        self.recorddir = self.recorddir_root + self.save_dir_name
        os.makedirs(self.recorddir)
        os.makedirs(self.recorddir + self.sub_dir_color)
        os.makedirs(self.recorddir + self.sub_dir_depth)
        os.makedirs(self.recorddir + self.sub_dir_depth_resized)

    def save_config_as_json(self, filename):
        with open(filename, 'w') as outfile:
            obj = json.dump(
                {
                    "name": "iPhone LiDAR 3D Reconstruction",
                    "path_dataset": "../../../../../data/" + self.save_dir_name,
                    "path_intrinsic": "../../../../../data/" + self.save_dir_name + self.intrinsic_filename,
                    "depth_max": 3.0,
                    "voxel_size": 0.05,
                    "depth_diff_max": 0.07,
                    "preference_loop_closure_odometry": 0.1,
                    "preference_loop_closure_registration": 5.0,
                    "tsdf_cubic_size": 3.0,
                    "icp_method": "color",
                    "global_registration": "ransac",
                    "python_multi_threading": True
                },
                outfile,
                indent=4)

    def save_intrinsic_as_json(self, filename, frame):
        intrinsics = self.session.get_intrinsic_mat()
        with open(filename, 'w') as outfile:
            obj = json.dump(
                {
                    'width':
                        frame.shape[1],
                    'height':
                        frame.shape[0],
                    'intrinsic_matrix': [
                        intrinsics.fx, 0, 0, 0, intrinsics.fy, 0, intrinsics.tx,
                        intrinsics.ty, 1
                    ]
                },
                outfile,
                indent=4)

    def create_video_writer(self, frame):
        filepath = self.recorddir + 'recording.avi'
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(filepath, fourcc, 30.0, (frame.shape[1], frame.shape[0]))

    def initialize_recording(self, frame, display_image):
        self.make_record_dir()
        self.save_config_as_json(self.recorddir + self.config_filename)
        self.save_intrinsic_as_json(self.recorddir + self.intrinsic_filename, frame)
        if self.record_display_image:
            self.create_video_writer(display_image)

    def finalize_recording(self):
        if not self.video_writer is None:
            self.video_writer.release()

    def resize_depth_image(self, color, depth):
        color_width = color.shape[1]
        color_height = color.shape[0]
        depth_width = depth.shape[1]
        depth_height = depth.shape[0]
        if depth_width != color_width and color_height != depth_height:
            depth = cv2.resize(depth, dsize=(color_width, color_height), interpolation=cv2.INTER_LANCZOS4)
        return depth

    def get_rgbd_image(self):
        color_org = self.session.get_rgb_frame()
        color = cv2.cvtColor(color_org, cv2.COLOR_RGB2BGR)
        depth_org = self.session.get_depth_frame()
        depth_mm = depth_org.astype(np.float64) * 1000.0
        depth = np.clip(depth_mm, 0, 65535).astype(np.uint16)
        return color, depth

    def normalize_min_max(self, x, min, max):
        diff_max_min = max - min
        result = x
        if diff_max_min != 0:
            result = (x - min) / (max - min)
        return result

    def colorize_depth(self, depth):
        min = 0
        max = 65535
        if self.depth_colorize_fixed_range:
            min = self.depth_colorize_min
            max = self.depth_colorize_max
        else:
            min = depth.min()
            max = depth.max()
        depth_clipped = np.clip(depth, min, max).astype(np.uint16)
        depth_normalized = self.normalize_min_max(depth_clipped, min, max)
        depth_colored = cv2.applyColorMap(cv2.convertScaleAbs(depth_normalized, alpha=255.0), cv2.COLORMAP_JET)
        return depth_colored

    def show_image(self, color, depth):
        color_resized = cv2.resize(color, dsize=None, fx=self.viewer_resize_factor, fy=self.viewer_resize_factor)
        depth_resized = self.resize_depth_image(color_resized, depth)
        depth_colored = self.colorize_depth(depth_resized)
        display_image = cv2.hconcat([color_resized, depth_colored])
        cv2.imshow('iPhone RGB-D', display_image)
        return display_image

    def save_rgbd_images(self, color, depth, rec_count):
        filename = str(rec_count).zfill(self.filename_zerofill)
        depth_resized = self.resize_depth_image(color, depth)
        cv2.imwrite(self.recorddir + self.sub_dir_color + filename + ".png", color)
        cv2.imwrite(self.recorddir + self.sub_dir_depth + filename + ".png", depth)
        cv2.imwrite(self.recorddir + self.sub_dir_depth_resized + filename + ".png", depth_resized)

    def start_processing_stream(self):
        try:
            rec_count = self.frame_count_init

            while self.activate:
                self.event.wait()
                color, depth = self.get_rgbd_image()
                display_image = self.show_image(color, depth)

                key = cv2.waitKey(1) & 0xff
                if key == ord('r'):
                    if self.recording:
                        self.recording = False
                        self.finalize_recording()
                    else:
                        self.recording = True
                elif key == ord('q') or key == 27:
                    cv2.destroyAllWindows()
                    break

                if self.recording:
                    if rec_count == self.frame_count_init:
                        self.initialize_recording(color, display_image)
                    self.save_rgbd_images(color, depth, rec_count)
                    rec_count = rec_count + 1
                    if not self.video_writer is None:
                        self.video_writer.write(display_image)
        finally:
            self.finalize_recording()
            self.event.clear()

if __name__ == '__main__':
    try:
        app = RecorderApp()
        app.connect_to_device(dev_idx=0)
        app.start_processing_stream()
    except RuntimeError as e:
        print(e)
    finally:
        print('Finished')
        
