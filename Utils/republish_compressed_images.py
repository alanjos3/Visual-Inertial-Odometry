#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import cv2
import numpy as np
from cv_bridge import CvBridge

class StereoRepublisher(Node):
    def __init__(self):
        super().__init__('stereo_republisher_node')	
        self.bridge = CvBridge()

        # Best Effort QoS handles high-bandwidth data more reliably over networks
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # --- LEFT CAMERA ---
        # Subscribes to left_raw_gray path provided
        self.sub_left = self.create_subscription(
            CompressedImage,
            '/zed/zed_node/left_raw_gray/image_raw_gray/compressed',
            self.left_callback,
            qos_profile)
        self.pub_left = self.create_publisher(Image, 'cam0/image_raw', 10)

        # --- RIGHT CAMERA ---
        # Subscribes to right_raw_gray path provided
        self.sub_right = self.create_subscription(
            CompressedImage,
            '/zed/zed_node/right_raw_gray/image_raw_gray/compressed',
            self.right_callback,
            qos_profile)
        self.pub_right = self.create_publisher(Image, 'cam1/image_raw', 10)

        self.get_logger().info('Stereo Decompressor Active:')
        self.get_logger().info('  /left_raw_gray  -> /cam0/image_raw')
        self.get_logger().info('  /right_raw_gray -> /cam1/image_raw')

    def process_and_publish(self, msg, publisher, frame_id):
        try:
            # Convert bytes to numpy array
            np_arr = np.frombuffer(msg.data, np.uint8)
            # Decode image (IMREAD_UNCHANGED preserves the grayscale/mono8 format)
            cv_image = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)

            if cv_image is not None:
                # Convert OpenCV Mat to ROS 2 Image
                raw_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='mono8')
                
                # Copy original hardware timestamp for VIO synchronization
                raw_msg.header = msg.header
                raw_msg.header.frame_id = frame_id
                
                publisher.publish(raw_msg)
        except Exception as e:
            self.get_logger().error(f'Error on {frame_id}: {str(e)}')

    def left_callback(self, msg):
        self.process_and_publish(msg, self.pub_left, 'cam0')

    def right_callback(self, msg):
        self.process_and_publish(msg, self.pub_right, 'cam1')

def main(args=None):
    rclpy.init(args=args)
    node = StereoRepublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Stereo Republisher...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
