#!/usr/bin/env python3

import time
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class GerakRobot(Node):

    def __init__(self):
        super().__init__('gerak_robot')

        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Kecepatan gerak lurus
        self.linear_speed = 3.0

    # =====================================
    # PUBLISH VELOCITY
    # =====================================

    def publish_velocity(self, linear, angular):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.publisher.publish(msg)

    # =====================================
    # BERHENTI
    # =====================================

    def berhenti(self):
        for _ in range(10):
            self.publish_velocity(0.0, 0.0)
            time.sleep(0.1)

    # =====================================
    # MAJU
    # =====================================

    def maju(self, jarak):
        if jarak <= 0:
            self.get_logger().warning(
                'Jarak harus lebih dari 0.'
            )
            return

        durasi = jarak / self.linear_speed

        self.get_logger().info(
            f'Maju {jarak} meter'
        )

        start_time = time.monotonic()

        try:
            while time.monotonic() - start_time < durasi:
                self.publish_velocity(
                    self.linear_speed,
                    0.0
                )
                time.sleep(0.05)
        finally:
            self.berhenti()

    # =====================================
    # MUNDUR
    # =====================================

    def mundur(self, jarak):
        if jarak <= 0:
            self.get_logger().warning(
                'Jarak harus lebih dari 0.'
            )
            return

        durasi = jarak / self.linear_speed

        self.get_logger().info(
            f'Mundur {jarak} meter'
        )

        start_time = time.monotonic()

        try:
            while time.monotonic() - start_time < durasi:
                self.publish_velocity(
                    -self.linear_speed,
                    0.0
                )
                time.sleep(0.05)
        finally:
            self.berhenti()

    # =====================================
    # FUNGSI BELOK UTAMA
    # Kecepatan dimasukkan langsung di sini
    # =====================================

    def belok(self, sudut, arah='kiri'):

        # Parameter belok
        linear_speed = 1.0
        angular_speed = 1.729

        if sudut <= 0:
            self.get_logger().warning(
                'Sudut harus lebih dari 0 derajat.'
            )
            return

        if arah == 'kiri':
            angular = angular_speed
        elif arah == 'kanan':
            angular = -angular_speed
        else:
            self.get_logger().error(
                "Arah harus 'kiri' atau 'kanan'."
            )
            return

        # Konversi derajat menjadi radian
        sudut_rad = math.radians(sudut)

        # Hitung durasi belok
        durasi = (sudut_rad / angular_speed) * 2.3865



        self.get_logger().info(
            f'Belok {arah} {sudut} derajat sambil maju | '
            f'Kecepatan maju: {linear_speed} m/s | '
            f'Kecepatan sudut: {angular_speed} rad/s | '
            f'Durasi: {durasi:.2f} detik'
        )

        start_time = time.monotonic()

        try:
            while time.monotonic() - start_time < durasi:
                self.publish_velocity(
                    linear_speed,
                    angular
                )
                time.sleep(0.05)
        finally:
            self.berhenti()

    # =====================================
    # GERAK LENGKUNG
    # Sudut positif = kiri
    # Sudut negatif = kanan
    # =====================================

    def gerak_lengkung(self, sudut):

        if sudut == 0:
            self.get_logger().warning(
                'Sudut lengkung tidak boleh 0 derajat.'
            )
            return

        # Parameter gerak lengkung
        linear_speed = 2.0
        angular_speed = 0.5

        # Menentukan arah lengkungan
        arah = 'kiri' if sudut > 0 else 'kanan'

        angular = (
            angular_speed if sudut > 0
            else -angular_speed
        )

        # Menghitung durasi berdasarkan sudut
        durasi = (
            math.radians(abs(sudut)) / angular_speed
        ) * 9.3

        self.get_logger().info(
            f'Gerak lengkung ke {arah} sebesar '
            f'{abs(sudut)} derajat | '
            f'Kecepatan maju: {linear_speed} m/s | '
            f'Kecepatan sudut: {abs(angular):.2f} rad/s | '
            f'Durasi: {durasi:.2f} detik'
        )

        start_time = time.monotonic()

        try:
            while time.monotonic() - start_time < durasi:
                self.publish_velocity(
                    linear_speed,
                    angular
                )
                time.sleep(0.05)
        finally:
            self.berhenti()

    # =====================================
    # BELOK KIRI
    # =====================================

    def belok_kiri(self, sudut):
        self.belok(sudut, arah='kiri')

    # =====================================
    # BELOK KANAN
    # =====================================

    def belok_kanan(self, sudut):
        self.belok(sudut, arah='kanan')


# =====================================
# PROGRAM UTAMA
# =====================================

def main(args=None):
    rclpy.init(args=args)

    robot = GerakRobot()

    try:
        robot.maju(8.5)
        robot.belok_kiri(90)

        robot.maju(1.5)
        robot.belok_kanan(90)

        robot.maju(4.5)
        robot.belok_kanan(90)

        robot.maju(11.8)
        robot.belok_kiri(90)

        robot.maju(23.7)
        robot.belok_kiri(90)

        robot.maju(31.6)
        robot.gerak_lengkung(45)

        robot.maju(8.5)
        robot.belok_kanan(90)

        robot.maju(3.7)
        robot.belok_kanan(90)

        robot.maju(14.0)
        robot.belok_kiri(90)

        robot.maju(3.0)
        robot.belok_kanan(90)

        robot.maju(2.5)
        robot.belok_kiri(90)

        robot.maju(15.0)
        robot.belok_kiri(90)

        robot.maju(10.0)

        robot.berhenti()

    except KeyboardInterrupt:
        robot.get_logger().info(
            'Program dihentikan.'
        )

    finally:
        robot.berhenti()
        robot.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
