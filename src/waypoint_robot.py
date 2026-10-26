#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class WaypointRobot(Node):

    def __init__(self):
        super().__init__('waypoint_robot')

        # Publisher perintah gerak
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Subscriber posisi robot
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Posisi awal
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.odom_received = False

        # Daftar waypoint (x, y) dalam meter
        self.waypoints = [
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
            (0.0, 0.0),
        ]

        self.waypoint_index = 0

        # Parameter gerakan
        self.linear_speed = 0.3
        self.angular_speed = 0.5
        self.distance_tolerance = 0.15
        self.angle_tolerance = 0.2

        # Timer untuk memperbarui gerakan
        self.timer = self.create_timer(
            0.05,
            self.control_loop
        )

        self.get_logger().info('Waypoint Robot dimulai.')

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        siny_cosp = 2.0 * (
            q.w * q.z + q.x * q.y
        )

        cosy_cosp = 1.0 - 2.0 * (
            q.y * q.y + q.z * q.z
        )

        self.yaw = math.atan2(
            siny_cosp,
            cosy_cosp
        )

        self.odom_received = True

    def publish_velocity(self, linear, angular):
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular

        self.publisher.publish(msg)

    def stop_robot(self):
        self.publish_velocity(0.0, 0.0)

    def control_loop(self):
        # Tunggu sampai menerima data odometri
        if not self.odom_received:
            self.stop_robot()
            return

        # Semua waypoint telah dicapai
        if self.waypoint_index >= len(self.waypoints):
            self.stop_robot()
            return

        target_x, target_y = self.waypoints[
            self.waypoint_index
        ]

        # Hitung jarak menuju waypoint
        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.sqrt(dx**2 + dy**2)

        # Periksa apakah waypoint sudah tercapai
        if distance < self.distance_tolerance:
            self.stop_robot()

            self.get_logger().info(
                f'Waypoint {self.waypoint_index + 1} tercapai.'
            )

            self.waypoint_index += 1

            if self.waypoint_index >= len(self.waypoints):
                self.get_logger().info(
                    'Semua waypoint selesai.'
                )

            return

        # Hitung sudut menuju waypoint
        target_yaw = math.atan2(dy, dx)

        angle_error = target_yaw - self.yaw

        # Normalisasi sudut ke rentang -pi sampai pi
        angle_error = math.atan2(
            math.sin(angle_error),
            math.cos(angle_error)
        )

        # Putar terlebih dahulu jika arah belum sesuai
        if abs(angle_error) > self.angle_tolerance:
            angular = max(
                -self.angular_speed,
                min(self.angular_speed, 1.5 * angle_error)
            )

            self.publish_velocity(0.0, angular)

        else:
            # Bergerak maju sambil mengoreksi arah
            linear = min(
                self.linear_speed,
                0.5 * distance
            )

            angular = max(
                -self.angular_speed,
                min(self.angular_speed, 1.5 * angle_error)
            )

            self.publish_velocity(linear, angular)


def main(args=None):
    rclpy.init(args=args)

    robot = WaypointRobot()

    try:
        rclpy.spin(robot)

    except KeyboardInterrupt:
        pass

    finally:
        robot.stop_robot()
        robot.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
