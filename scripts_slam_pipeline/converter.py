import rosbag 
import cv2
from cv_bridge import CvBridge
import argparse
import glob
import os 
import pathlib
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


def extract_video_and_IMU(bag_file, topics_list, demo_dir, raw_video_dir):
    bridge = CvBridge()
    bag = rosbag.Bag(bag_file, 'r')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    frame_rate = 30
    frame_size = None

    raw_video_writer = None
    demo_video_writer = None
    output_dir= pathlib.Path(demo_dir).joinpath('demo_'+bag_file[0:-4])
    output_video = pathlib.Path(output_dir).joinpath("raw_video.mp4")
    if(not os.path.exists(output_dir)):
        os.mkdir(output_dir)

    if('mapping' in bag_file):
        raw_video_file = pathlib.Path(raw_video_dir).joinpath('mapping.mp4')
        output_dir = pathlib.Path(demo_dir).joinpath('mapping')
        if (not os.path.exists(output_dir)):
            os.mkdir(output_dir)
        output_video = output_dir.joinpath('raw_video.mp4')
    else if ('gripper_calibration' in bag_file):
        gripper_calibration_dir = pathlib.Path(raw_video_dir).joinpath('gripper_calibration')
        if(not os.path.exists(gripper_calibration_dir)):
            os.mkdir(gripper_calibration_dir)
        raw_video_file = pathlib.Path(gripper_calibration_dir).joinpath('raw_video.mp4')
        output_dir = pathlib.Path(demo_dir).joinpath(bag_file[0:-4])
        if (not os.path.exists(output_dir)):
            os.mkdir(output_dir)
        output_video = output_dir.joinpath('raw_video.mp4')
    else:
        raw_video_file = pathlib.Path(raw_video_dir).joinpath(bag_file[0:-4])
        output_dir = pathlib.Path(demo_dir).joinpath(bag_file[0:-4])
        if (not os.path.exists(output_dir)):
            os.mkdir(output_dir)
        output_video = output_dir.joinpath('raw_video.mp4')

    
    for topic, msg, t in bag.read_messages(topics=topics_list):
        if("image/data" in topic):
            try:
                frame = bridge.imgmsg_to_cv2(msg, "bgr8")
            except Exception as e:
                print(f"Error converting message: {e}")
                continue
            if frame_size is None:
                #First frame, determine frame size.
                frame_size = (frame.shape[1], frame.shape[0])
                demo_video_writer = cv2.VideoWriter(output_video, fourcc, frame_rate, frame_size)
                raw_video_writer = cv2.VideoWriter(raw_video_file, fourcc, frame_rate, frame_size)
            demo_video_writer.write(frame)
            raw_video_writer.write(frame)

    bag.close()
    if raw_video_writer is not None:
        raw_video_writer.release()
        print(f"Video saved as {raw_video_file}")
    if demo_video_writer is not None:
        demo_video_writer.release()
        print(f"Video saved as {output_video}")




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bag_dir", type = str, required = True)
    parser.add_argument("-t", "--task_name", type = str, required=True)
    args = parser.parse_args()
    #Set up folder directories.
    data_dir = pathlib.Path(ROOT_DIR).joinpath('data_workspace')
    
    task_dir = data_dir.joinpath(args.task_name)
    demo_dir = task_dir.joinpath('demos')
    mapping_dir = demo_dir.joinpath('mapping')
    raw_video_dir = task_dir.joinpath('raw_videos')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(task_dir):
        os.mkdir(task_dir)
    if not os.path.exists(demo_dir):
        os.mkdir(demo_dir)
    if not os.path.exists(mapping_dir):
        os.mkdir(mapping_dir)
    if not os.path.exists(raw_video_dir):
        os.mmkdir(raw_video_dir)

    
    

    
    bag_files = glob.glob(args.bag_dir+"/*")
    for bag_file in bag_files:
        bag = rosbag.Bag(bag_file)
        #Extract topics of image data and IMU data.
        target_topics = ["/imu/data", "/image/data"]
        topics = bag.get_type_and_topic_info()[1].keys()
        topics_list = []
        for t in topics:
            print("Topic.." + str(t))
            for target in target_topics:
                if(target in t):
                    topics_list.append(t)
        
        extract_video_and_IMU(bag_file, topics_list, demo_dir, raw_video_dir)

            

    
    
        