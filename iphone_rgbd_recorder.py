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
        self.filename_zerofill = j['filename_zerofill']
        self.intrinsic_filename = j['intrinsic_filename']
        self.frame_count_init = j['frme_count_init']
        self.config_filename = j['config_filename']
        self.dir_name_format = j['dir_name_format']
        self.depth_colorize_fixed_range = j['depth_colorize_fixed_range']
        self.depth_colorize_min = j['depth_colorize_min']
        self.depth_colorize_max = j['depth_colorize_max']

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
        self.recorddir = self.recorddir_root + now.strftime(self.dir_name_format) + "/"
        os.makedirs(self.recorddir)
        os.makedirs(self.recorddir + self.sub_dir_color)
        os.makedirs(self.recorddir + self.sub_dir_depth)

    def save_config_as_json(self, filename):
        with open(filename, 'w') as outfile:
            obj = json.dump(
                {
                    "name": "iPhone LiDAR 3D Reconstruction",
                    "path_dataset": self.recorddir,
                    "path_intrinsic": self.recorddir + self.intrinsic_filename,
                    "max_depth": 3.0,
                    "voxel_size": 0.05,
                    "max_depth_diff": 0.07,
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

    def initialize_recording(self, frame):
        self.make_record_dir()
        self.save_config_as_json(self.recorddir + self.config_filename)
        self.save_intrinsic_as_json(self.recorddir + self.intrinsic_filename, frame)

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
        depth_mm = depth_org * 1000.0
        depth_mm_u16 = np.clip(depth_mm.astype(np.uint16), 0, 65535)
        depth = self.resize_depth_image(color, depth_mm_u16)
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
        depth_clipped = np.clip(depth.astype(np.uint16), min, max)
        depth_normalized = self.normalize_min_max(depth_clipped, min, max)
        depth_colored = cv2.applyColorMap(cv2.convertScaleAbs(depth_normalized, alpha=255.0), cv2.COLORMAP_JET)
        return depth_colored

    def show_image(self, color, depth):
        depth_colored = self.colorize_depth(depth)
        image_display = cv2.hconcat([color, depth_colored])
        cv2.imshow('iPhone RGB-D', image_display)

    def save_rgbd_images(self, color, depth, rec_count):
        filename = str(rec_count).zfill(self.filename_zerofill)
        cv2.imwrite(self.recorddir + self.sub_dir_color + filename + ".jpg", color)
        cv2.imwrite(self.recorddir + self.sub_dir_depth + filename + ".png", depth)

    def start_processing_stream(self):
        rec_count = self.frame_count_init

        while self.activate:
            self.event.wait()
            color, depth = self.get_rgbd_image()
            self.show_image(color, depth)

            key = cv2.waitKey(1) & 0xff
            if key == ord('r'):
                if self.recording:
                    self.recording = False
                else:
                    self.recording = True
            elif key == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break

            if self.recording:
                if rec_count == self.frame_count_init:
                    self.initialize_recording(color)
                self.save_rgbd_images(color, depth, rec_count)
                rec_count = rec_count + 1

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
        
