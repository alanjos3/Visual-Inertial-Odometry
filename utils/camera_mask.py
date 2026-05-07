#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class StereoBlackout(Node):

    def __init__(self):
        super().__init__('stereo_circular_mask_node')

        self.bridge = CvBridge()

        # Subscribers
        self.sub_cam0 = self.create_subscription(
            Image,
            '/cam0/image_raw',
            self.cam0_callback,
            10
        )

        self.sub_cam1 = self.create_subscription(
            Image,
            '/cam1/image_raw',
            self.cam1_callback,
            10
        )

        # Publishers
        self.pub_cam0 = self.create_publisher(Image, '/cam0/blackout', 10)
        self.pub_cam1 = self.create_publisher(Image, '/cam1/blackout', 10)

        # Adjustable radius scale (0 to 1)
        self.radius_scale = 0.5   #  change this (e.g., 0.5 → 0.8)

        self.get_logger().info("Stereo circular mask node started")

    def process_and_publish(self, msg, publisher):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            h, w, _ = cv_image.shape

            # Create circular mask
            center = (w // 2, h // 2)
            radius = int(min(w, h) * self.radius_scale)

            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.circle(mask, center, radius, 255, -1)

            # Apply mask
            masked = cv2.bitwise_and(cv_image, cv_image, mask=mask)

            # Convert back
            out_msg = self.bridge.cv2_to_imgmsg(masked, encoding='bgr8')
            out_msg.header = msg.header

            publisher.publish(out_msg)

        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def cam0_callback(self, msg):
        self.process_and_publish(msg, self.pub_cam0)

    def cam1_callback(self, msg):
        self.process_and_publish(msg, self.pub_cam1)


def main(args=None):
    rclpy.init(args=args)

    node = StereoBlackout()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
