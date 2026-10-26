#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TrialBelok(Node):

    def __init__(self):
        super().__init__('trial_belok')

        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # =========================
        # PARAMETER UJI
        # =========================

        self.linear_speed = 0.0
        self.angular_speed = 1.5
        self.turn_duration = 2.39

        # Pilihan: 'kiri' atau 'kanan'
        self.direction = 'kiri'

    def publish_velocity(self, linear, angular):
        msg = Twist()

        msg.linear.x = float(linear)
        msg.angular.z = float(angular)

        self.publisher.publish(msg)

    def stop_robot(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0

        # Kirim beberapa kali agar robot menerima perintah berhenti
        for _ in range(10):
            self.publisher.publish(msg)
            time.sleep(0.1)

    def turn(self):
        # Tentukan arah belok
        if self.direction == 'kiri':
            angular = self.angular_speed
        elif self.direction == 'kanan':
            angular = -self.angular_speed
        else:
            self.get_logger().error(
                "Arah tidak valid. Gunakan 'kiri' atau 'kanan'."
            )
            return

        self.get_logger().info('Bersiap melakukan pengujian...')
        time.sleep(1.0)

        self.get_logger().info(
            f'Belok sambil maju | '
            f'Arah: {self.direction} | '
            f'Kecepatan maju: {self.linear_speed} m/s | '
            f'Kecepatan sudut: {self.angular_speed} rad/s | '
            f'Durasi: {self.turn_duration} detik'
        )

        start_time = time.monotonic()

        try:
            while (
                time.monotonic() - start_time
                < self.turn_duration
            ):
                self.publish_velocity(
                    self.linear_speed,
                    angular
                )
                time.sleep(0.05)

        finally:
            self.stop_robot()

        self.get_logger().info('Pengujian belok selesai.')

    def stop(self):
        self.stop_robot()


def main(args=None):
    rclpy.init(args=args)

    robot = TrialBelok()

    try:
        while True:
            robot.turn()

            # Jeda 1 detik sebelum pengujian berikutnya
            time.sleep(1.0)

    except KeyboardInterrupt:
        robot.get_logger().info(
            'Pengujian dihentikan oleh pengguna.'
        )

    finally:
        robot.stop()
        robot.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
