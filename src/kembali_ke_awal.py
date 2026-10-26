#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_ros import Buffer, TransformListener, TransformException


class KembaliKeAwal(Node):
    def __init__(self):
        super().__init__('kembali_ke_awal')

        # Titik awal robot
        self.target_x = 83.053
        self.target_y = 20.105
        self.target_yaw = math.radians(22.605)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Parameter kontrol
        self.max_linear = 1.0
        self.min_linear = 0.15
        self.max_angular = 0.5
        self.position_tolerance = 0.10
        self.angle_tolerance = math.radians(2.0)

        self.stage = 'menuju_titik_awal'
        self.finished = False

        self.timer = self.create_timer(0.05, self.control_loop)

        self.get_logger().info(
            f'Target kembali: x={self.target_x}, y={self.target_y}'
        )

    def normalize_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def publish_cmd(self, linear=0.0, angular=0.0):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.cmd_pub.publish(msg)

    def control_loop(self):
        if self.finished:
            return

        try:
            transform = self.tf_buffer.lookup_transform(
                'odom',
                'base_footprint',
                rclpy.time.Time()
            )
        except TransformException:
            self.publish_cmd()
            return

        position = transform.transform.translation
        rotation = transform.transform.rotation

        x = position.x
        y = position.y

        sin_yaw = 2.0 * (
            rotation.w * rotation.z + rotation.x * rotation.y
        )
        cos_yaw = 1.0 - 2.0 * (
            rotation.y ** 2 + rotation.z ** 2
        )
        yaw = math.atan2(sin_yaw, cos_yaw)

        dx = self.target_x - x
        dy = self.target_y - y
        distance = math.hypot(dx, dy)

        cmd = Twist()

        if self.stage == 'menuju_titik_awal':
            if distance <= self.position_tolerance:
                self.stage = 'menyesuaikan_orientasi'
                self.publish_cmd()
                self.get_logger().info(
                    'Titik awal tercapai. Menyesuaikan orientasi.'
                )
                return

            target_heading = math.atan2(dy, dx)
            heading_error = self.normalize_angle(target_heading - yaw)

            # Koreksi arah sambil bergerak, tanpa berputar di tempat.
            cmd.angular.z = max(
                -self.max_angular,
                min(self.max_angular, 1.5 * heading_error)
            )

            # Kurangi kecepatan jika robot belum menghadap target.
            alignment = max(0.0, math.cos(heading_error))
            cmd.linear.x = max(
                self.min_linear,
                min(self.max_linear, distance * 0.5)
            ) * alignment

            self.cmd_pub.publish(cmd)

        elif self.stage == 'menyesuaikan_orientasi':
            angle_error = self.normalize_angle(self.target_yaw - yaw)

            if abs(angle_error) <= self.angle_tolerance:
                self.publish_cmd()
                self.finished = True
                self.timer.cancel()
                self.get_logger().info(
                    'Robot sudah kembali ke titik dan orientasi awal.'
                )
                return

            cmd.angular.z = max(
                -self.max_angular,
                min(self.max_angular, 1.5 * angle_error)
            )
            self.cmd_pub.publish(cmd)

    def stop_robot(self):
        self.publish_cmd()


def main(args=None):
    rclpy.init(args=args)
    node = KembaliKeAwal()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
