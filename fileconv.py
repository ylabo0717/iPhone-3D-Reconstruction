import sys
import os
import shutil
import pathlib
import json
import cv2
import datetime

class FileConverter:
    def __init__(self, input_dir):
        self.load_app_config('app_config.json')
        self.input_dir = input_dir
        input_dir_name = pathlib.Path(input_dir).name
        dt = datetime.datetime.strptime(pathlib.Path(input_dir).name, '%Y_%m_%d_%H_%M_%S')
        self.output_dir = input_dir.replace(input_dir_name, dt.strftime(self.dir_name_format))
        self.make_output_dir()

    def load_app_config(self, filename):
        input_file = open(filename, 'r')
        j = json.load(input_file)
        self.sub_dir_color = j['sub_dir_color']
        self.sub_dir_depth = j['sub_dir_depth']
        self.sub_dir_depth_resized = j['sub_dir_depth_resized']
        self.filename_zerofill = j['filename_zerofill']
        self.intrinsic_filename = j['intrinsic_filename']
        self.dir_name_format = j['dir_name_format']

    def make_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def make_output_dir(self):
        self.make_dir(self.output_dir)
        self.make_dir(self.output_dir + '/' + self.sub_dir_color)
        self.make_dir(self.output_dir + '/' + self.sub_dir_depth)
        self.make_dir(self.output_dir + '/' + self.sub_dir_depth_resized)

    def convert_intrinsics(self):
        frame = cv2.imread(self.input_dir + "frame_00000.jpg")
        input_file = open(self.input_dir + "frame_00000.json", 'r')
        j = json.load(input_file)
        intrinsic_matrix = j['intrinsics']
        with open(self.output_dir + self.intrinsic_filename, 'w') as outfile:
            obj = json.dump(
                {
                    'width':
                        frame.shape[1],
                    'height':
                        frame.shape[0],
                    'intrinsic_matrix': intrinsic_matrix
                },
                outfile,
                indent=4)

    def resize_depth_image(self, color, depth):
        color_width = color.shape[1]
        color_height = color.shape[0]
        depth_width = depth.shape[1]
        depth_height = depth.shape[0]
        if depth_width != color_width and color_height != depth_height:
            depth = cv2.resize(depth, dsize=(color_width, color_height), interpolation=cv2.INTER_LANCZOS4)
        return depth

    def convert_images(self, frame_count):
        input_filename = str(frame_count).zfill(5)
        input_filename_color = self.input_dir + "frame_" + input_filename + ".jpg"
        input_filename_depth = self.input_dir + "depth_" + input_filename + ".png"

        output_filename = str(frame_count).zfill(self.filename_zerofill)
        output_filename_color = self.output_dir + self.sub_dir_color + output_filename + ".jpg"
        output_filename_depth = self.output_dir + self.sub_dir_depth + output_filename + ".png"
        output_filename_depth_resized = self.output_dir + self.sub_dir_depth_resized + output_filename + ".png"

        if os.path.exists(input_filename_color) and os.path.exists(input_filename_depth):
            shutil.copy(input_filename_color, output_filename_color)
            shutil.copy(input_filename_depth, output_filename_depth)
            color = cv2.imread(output_filename_color)
            depth = cv2.imread(output_filename_depth, -1)
            depth_resized = self.resize_depth_image(color, depth)
            cv2.imwrite(output_filename_depth_resized, depth_resized)
            return True
        else:
            return False

    def process(self):
        self.convert_intrinsics()
        frame_count = 0 
        while True:
            if self.convert_images(frame_count) == False:
                break           
            frame_count = frame_count + 3

if __name__ == '__main__':
    args = sys.argv
    target_dir = args[1]
    app = FileConverter(target_dir.replace(os.sep,'/'))
    app.process()
