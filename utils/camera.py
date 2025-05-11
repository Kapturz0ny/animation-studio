from PyQt5.QtGui import QVector3D, QMatrix4x4
import numpy as np
from enum import Enum


class Direction(Enum):
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"
    DOWN = "DOWN"


class Camera:
    def __init__(
        self,
        position=QVector3D(3, 3, 5),
        world_up=QVector3D(0, 1, 0),
        yaw=-135.0,
        pitch=-30.0,
        movement_speed=0.1,
        mouse_sensitivity=0.1,
        zoom_fov=45.0,
    ):
        self.position = position
        self.front = QVector3D(0, 0, -1)
        self.world_up = world_up
        self.yaw = yaw
        self.pitch = pitch
        self.movement_speed = movement_speed
        self.mouse_sensitivity = mouse_sensitivity
        self.zoom_fov = zoom_fov  # base fov

        # Store initial values for reset
        self.initial_position = QVector3D(position)
        self.initial_world_up = QVector3D(world_up)
        self.initial_yaw = yaw
        self.initial_pitch = pitch
        self.initial_movement_speed = movement_speed
        self.initial_mouse_sensitivity = mouse_sensitivity
        self.initial_zoom_fov = zoom_fov

        self.right = QVector3D()
        self.up = QVector3D()

        self._update_camera_vectors()

    def _update_camera_vectors(self):
        fx = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        fy = np.sin(np.radians(self.pitch))
        fz = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        self.front = QVector3D(fx, fy, fz).normalized()

        self.right = QVector3D.crossProduct(self.front, self.world_up).normalized()
        self.up = QVector3D.crossProduct(self.right, self.front).normalized()

    def get_view_matrix(self):
        matrix = QMatrix4x4()
        matrix.lookAt(self.position, self.position + self.front, self.up)
        return matrix

    def get_projection_matrix(self, aspect_ratio, near_plane=0.1, far_plane=100.0):
        projection = QMatrix4x4()
        projection.perspective(self.zoom_fov, aspect_ratio, near_plane, far_plane)
        return projection

    def process_mouse_movement(self, x_offset, y_offset, constrain_pitch=True):
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity

        self.yaw += x_offset
        self.pitch += y_offset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self._update_camera_vectors()

    def process_mouse_scroll(self, y_offset):
        self.zoom_fov -= y_offset
        if self.zoom_fov < 1.0:
            self.zoom_fov = 1.0
        if self.zoom_fov > 75.0:
            self.zoom_fov = 75.0

    def process_keyboard_movement(self, direction, velocity_multiplier=1.0):
        actual_velocity = self.movement_speed * velocity_multiplier

        if direction == Direction.FORWARD:
            self.position += self.front * actual_velocity
        if direction == Direction.BACKWARD:
            self.position -= self.front * actual_velocity
        if direction == Direction.LEFT:
            self.position -= self.right * actual_velocity
        if direction == Direction.RIGHT:
            self.position += self.right * actual_velocity
        if direction == Direction.UP:
            self.position += self.world_up * actual_velocity
        if direction == Direction.DOWN:
            self.position -= self.world_up * actual_velocity

    def reset_state(self):
        self.position = QVector3D(self.initial_position)
        self.world_up = QVector3D(self.initial_world_up)
        self.yaw = self.initial_yaw
        self.pitch = self.initial_pitch
        self.movement_speed = self.initial_movement_speed
        self.mouse_sensitivity = self.initial_mouse_sensitivity
        self.zoom_fov = self.initial_zoom_fov
        self._update_camera_vectors()
