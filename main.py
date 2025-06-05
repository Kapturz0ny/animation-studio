from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QScrollArea,
    QFileDialog,
    QMessageBox,
    QOpenGLWidget,
    QGroupBox,
)
from PyQt5.QtGui import (
    QOpenGLShaderProgram,
    QOpenGLShader,
    QMatrix4x4,
    QVector3D,
    QMouseEvent,
    QWheelEvent,
    QKeyEvent,
)
from PyQt5.QtCore import Qt, QPoint, QTimer
from OpenGL.GL import (
    glEnable,
    glClearColor,
    glClear,
    glBindVertexArray,
    glDrawArrays,
    glGenVertexArrays,
    glGenBuffers,
    glDeleteVertexArrays,
    glDeleteBuffers,
    glBindBuffer,
    glBufferData,
    glVertexAttribPointer,
    glEnableVertexAttribArray,
    glViewport,
    GL_DEPTH_TEST,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_ARRAY_BUFFER,
    GL_STATIC_DRAW,
    GL_FLOAT,
    GL_FALSE,
    GL_TRIANGLES,
)
import numpy as np


from loader.obj_loader import load_obj
from utils.camera import Camera, Direction
import sys
import ctypes

phong_vert = "shaders/phong.vert"
phong_frag = "shaders/phong.frag"
vert = "shaders/vertex_shader.glsl"
frag = "shaders/fragment_shader.glsl"


class MyGLWidget(QOpenGLWidget):
    def __init__(self):
        super(MyGLWidget, self).__init__()
        self.color = [0.1, 0.1, 0.1]
        self.shader_program = None
        self.vao = None
        self.vbo = None
        self.additional_vaos = []
        self.additional_vbos = []
        self.additional_vertex_counts = []
        self.additional_visible_flags = []

        self.camera = Camera(
            position=QVector3D(3, 3, 5), yaw=-135.0, pitch=-30.0, zoom_fov=45.0
        )
        self.camera_interaction_mode = False
        self.last_mouse_pos = QPoint()
        self.keys_pressed = set()

        # timer for smooth camera movement
        self.camera_move_timer = QTimer(self)
        self.camera_move_timer.timeout.connect(self.update_camera_position_from_keys)
        self.timer_interval = 16

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
        self.initShaders()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        glClearColor(self.color[0], self.color[1], self.color[2], 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

        if not self.shader_program:
            return

        self.shader_program.bind()

        model = QMatrix4x4()
        view = self.camera.get_view_matrix()

        aspect_ratio = self.width() / max(1, self.height())
        projection = self.camera.get_projection_matrix(aspect_ratio)

        self.shader_program.setUniformValue("M", model)
        self.shader_program.setUniformValue("view", view)
        self.shader_program.setUniformValue("projection", projection)

        self.shader_program.setUniformValue("light_position", 5.0, 5.0, 5.0)
        self.shader_program.setUniformValue(
            "viewPos",
            self.camera.position.x(),
            self.camera.position.y(),
            self.camera.position.z(),
        )
        self.shader_program.setUniformValue("objectColor", 1.0, 0.3, 0.3)
        self.shader_program.setUniformValue("light_ambient", 1.0, 1.0, 1.0)
        self.shader_program.setUniformValue("light_diffuse", 1.0, 1.0, 1.0)
        self.shader_program.setUniformValue("light_shininess", 1.0, 1.0, 1.0)

        self.shader_program.setUniformValue("material_ambient", 0.2, 0.2, 0.2)
        self.shader_program.setUniformValue("material_diffuse", 1.0, 1.0, 1.0)
        self.shader_program.setUniformValue("material_shininess", 32.0)
        self.shader_program.setUniformValue("color", 1.0, 0.3, 0.3)
        self.shader_program.setUniformValue("camera_position", self.camera.position)

        # self.shader_program.setUniformValue("viewPos", 0.0, 3.0, 5.0)
        # self.shader_program.setUniformValue("objectColor", 1.0, 0.3, 0.3)
        # self.shader_program.setUniformValue("lightColor", self.light_color)

        # glBindVertexArray(0)

        for vao, count, visible in zip(
            self.additional_vaos,
            self.additional_vertex_counts,
            self.additional_visible_flags,
        ):
            if not visible:
                continue
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLES, 0, count)
        glBindVertexArray(0)

        self.shader_program.release()

    def set_camera_interaction_active(self, active):
        self.camera_interaction_mode = active
        if active:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            if not self.camera_move_timer.isActive():
                self.camera_move_timer.start(self.timer_interval)
            print("Tryb kamery WŁĄCZONY")
        else:
            self.clearFocus()
            self.unsetCursor()
            if self.camera_move_timer.isActive():
                self.camera_move_timer.stop()
            self.keys_pressed.clear()
            print("Tryb kamery WYŁĄCZONY")

    def mousePressEvent(self, event: QMouseEvent):
        if (
            self.camera_interaction_mode
            and event.buttons() == Qt.MouseButton.LeftButton
        ):
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if (
            self.camera_interaction_mode
            and event.buttons() == Qt.MouseButton.LeftButton
        ):

            offset_x = event.pos().x() - self.last_mouse_pos.x()
            offset_y = self.last_mouse_pos.y() - event.pos().y()

            self.last_mouse_pos = event.pos()

            if offset_x != 0 or offset_y != 0:
                self.camera.process_mouse_movement(offset_x, offset_y)
                self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.camera_interaction_mode and event.button() == Qt.MouseButton.LeftButton:
            self.unsetCursor()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if self.camera_interaction_mode:
            scroll_delta = event.angleDelta().y() / 120
            self.camera.process_mouse_scroll(scroll_delta)
            self.update()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if self.camera_interaction_mode:
            self.keys_pressed.add(event.key())
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if self.camera_interaction_mode and not event.isAutoRepeat():
            if event.key() in self.keys_pressed:
                self.keys_pressed.remove(event.key())
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def update_camera_position_from_keys(self):
        if not self.camera_interaction_mode or not self.hasFocus():
            return

        moved = False
        velocity_multiplier = 1.0

        if Qt.Key.Key_W in self.keys_pressed:
            self.camera.process_keyboard_movement(
                Direction.FORWARD, velocity_multiplier
            )
            moved = True
        if Qt.Key.Key_S in self.keys_pressed:
            self.camera.process_keyboard_movement(
                Direction.BACKWARD, velocity_multiplier
            )
            moved = True
        if Qt.Key.Key_A in self.keys_pressed:
            self.camera.process_keyboard_movement(Direction.LEFT, velocity_multiplier)
            moved = True
        if Qt.Key.Key_D in self.keys_pressed:
            self.camera.process_keyboard_movement(Direction.RIGHT, velocity_multiplier)
            moved = True
        if Qt.Key.Key_Space in self.keys_pressed:
            self.camera.process_keyboard_movement(Direction.UP, velocity_multiplier)
            moved = True
        if Qt.Key.Key_Control in self.keys_pressed:
            self.camera.process_keyboard_movement(Direction.DOWN, velocity_multiplier)
            moved = True

        if moved:
            self.update()

    def initShaders(self):
        self.shader_program = QOpenGLShaderProgram()
        if not self.shader_program.addShaderFromSourceFile(
            QOpenGLShader.Vertex, phong_vert  # type: ignore
        ):
            print("Błąd wczytywania vertex shadera")
        if not self.shader_program.addShaderFromSourceFile(
            QOpenGLShader.Fragment, phong_frag  # type: ignore
        ):
            print("Błąd wczytywania fragment shadera")
        self.shader_program.bindAttributeLocation("position", 0)
        self.shader_program.bindAttributeLocation("normal", 1)

        if not self.shader_program.link():
            print("Błąd linkowania shaderów")
            print(self.shader_program.log())


    def loadModel(self, vertices_np):
        self.makeCurrent()  # activate OpenGL context

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices_np.nbytes, vertices_np, GL_STATIC_DRAW)

        glVertexAttribPointer(
            0, 3, GL_FLOAT, GL_FALSE, 6 * vertices_np.itemsize, ctypes.c_void_p(0)
        )
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            1,
            3,
            GL_FLOAT,
            GL_FALSE,
            6 * vertices_np.itemsize,
            ctypes.c_void_p(3 * vertices_np.itemsize),
        )
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # save to list to draw in paintGL
        self.additional_vaos.append(vao)
        self.additional_vbos.append(vbo)
        self.additional_vertex_counts.append(len(vertices_np) // 6)

        self.doneCurrent()  # free context
        self.additional_visible_flags.append(True)

        self.update()

    def updateModelVertices(self, model_index, vertices_np):
        self.makeCurrent()

        vbo_id = self.additional_vbos[model_index]  # surowe ID
        glBindBuffer(GL_ARRAY_BUFFER, vbo_id)
        glBufferData(GL_ARRAY_BUFFER, vertices_np.nbytes, vertices_np, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.doneCurrent()
        self.update()


    def delete_model(self, index):
        self.makeCurrent()
        glDeleteVertexArrays(1, [self.additional_vaos[index]])
        glDeleteBuffers(1, [self.additional_vbos[index]])
        self.doneCurrent()

        del self.additional_vaos[index]
        del self.additional_vbos[index]
        del self.additional_vertex_counts[index]
        del self.additional_visible_flags[index]

        self.update()


    def change_background_color(self, r, g, b):
        self.color = [r, g, b]
        self.update()


class FigureItem(QWidget):
    def __init__(self, name, gl_widget, index, parent_layout, main_window, centroid, vertices_np):
        super().__init__()
        self.name = name
        self.gl_widget = gl_widget
        self.parent_layout = parent_layout
        self.main_window = main_window
        self.index = index

        self.centroid = centroid
        self.size_x = 1.0
        self.size_y = 1.0
        self.size_z = 1.0
        self.diffuse =  [0.0, 0.0, 0.0, 0.0]    # rozproszone odbicie swiatla
        self.specular =  [0.0, 0.0, 0.0, 0.0]   # odbicie zwierciadlane

        self.original_vertices = vertices_np
        self.current_vertices = vertices_np.copy()

        self.params_in_frames = {}

        layout = QHBoxLayout()
        self.name_button = QPushButton(name)
        self.name_button.clicked.connect(self.on_name_button_clicked)


        self.toggle_button = QPushButton("✖")
        self.toggle_button.setFixedSize(24, 24)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self.toggle_visibility)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(
            "background-color: lightgray; color: black; padding: 0px; margin: 0px;"
        )
        self.delete_button.setFixedSize(60, 24)
        self.delete_button.clicked.connect(self.delete_self)

        layout.addWidget(self.name_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.delete_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
    
    def toggle_visibility(self):
        current_state = self.toggle_button.isChecked()
        self.gl_widget.additional_visible_flags[self.index] = current_state
        self.update_icon()
        self.gl_widget.update()

    def on_name_button_clicked(self):
        self.display_figure_params()
        self.display_frame_figure()

    def fill_params_for_frame_1(self):
        self.params_in_frames[1] = {
            'centroid': self.centroid,
            'size_x': self.size_x,
            'size_y': self.size_y,
            'size_z': self.size_z,
            'rot_x': 0.0,
            'rot_y': 0.0,
            'rot_z': 0.0,
        }

    def update_icon(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setText("✖")  # figure visible
        else:
            self.toggle_button.setText("")  # figure invisible

    def delete_self(self):
        try:
            index = self.parent_layout.indexOf(self)
            if index != -1:
                self.gl_widget.delete_model(index)
        except Exception as e:
            print(f"Delete error: {e}")
        clear_layout(self.main_window.parameters_frame_area)
        clear_layout(self.main_window.parameters_object_area)
        self.main_window.param_frame_number.setText("Object in frame not chosen")
        self.main_window.param_object_name.setText("Object not selected")
        self.main_window.parameters_object_area.addWidget(self.main_window.param_object_name)
        self.main_window.parameters_frame_area.addWidget(self.main_window.param_frame_number)      
        self.setParent(None)
        self.parent_layout.removeWidget(self)
        self.deleteLater()
        
    def display_figure_params(self):
        section_layout = self.main_window.parameters_object_area
        clear_layout(section_layout)

        self.main_window.param_object_name.setText(f"Parameters for {self.name}")


        if 1 not in self.params_in_frames or not self.params_in_frames[1]:
            self.fill_params_for_frame_1()

        base_frame = self.params_in_frames.get(1, {})
        centroid = base_frame.get("centroid", (0.0, 0.0, 0.0))
        size_x = base_frame.get("size_x", 0.0)
        size_y = base_frame.get("size_y", 0.0)
        size_z = base_frame.get("size_z", 0.0)
        rot_x = base_frame.get("rot_x", 0.0)
        rot_y = base_frame.get("rot_y", 0.0)
        rot_z = base_frame.get("rot_z", 0.0)

        # Location
        self.location_title = QLabel("Location")
        self.location_box = QHBoxLayout()
        self.loc_x_text = QLineEdit(str(centroid[0]))
        self.loc_y_text = QLineEdit(str(centroid[1]))
        self.loc_z_text = QLineEdit(str(centroid[2]))
        self.location_box.addWidget(QLabel("x:"))
        self.location_box.addWidget(self.loc_x_text)
        self.location_box.addWidget(QLabel("y:"))
        self.location_box.addWidget(self.loc_y_text)
        self.location_box.addWidget(QLabel("z:"))
        self.location_box.addWidget(self.loc_z_text)

        # Size
        self.size_title = QLabel("Scale")
        self.size_box = QHBoxLayout()
        self.siz_x_text = QLineEdit(str(size_x))
        self.siz_y_text = QLineEdit(str(size_y))
        self.siz_z_text = QLineEdit(str(size_z))
        self.size_box.addWidget(QLabel("x:"))
        self.size_box.addWidget(self.siz_x_text)
        self.size_box.addWidget(QLabel("y:"))
        self.size_box.addWidget(self.siz_y_text)
        self.size_box.addWidget(QLabel("z:"))
        self.size_box.addWidget(self.siz_z_text)

        # Rotation
        self.rotation_title = QLabel("Rotation")
        self.rotation_box = QHBoxLayout()
        self.rot_x_text = QLineEdit(str(rot_x))
        self.rot_y_text = QLineEdit(str(rot_y))
        self.rot_z_text = QLineEdit(str(rot_z))
        self.rotation_box.addWidget(QLabel("x:"))
        self.rotation_box.addWidget(self.rot_x_text)
        self.rotation_box.addWidget(QLabel("y:"))
        self.rotation_box.addWidget(self.rot_y_text)
        self.rotation_box.addWidget(QLabel("z:"))
        self.rotation_box.addWidget(self.rot_z_text)

        # Diffuse (z atrybutu!)
        self.diffuse_title = QLabel("Diffuse (RGBA)")
        self.diffuse_box = QHBoxLayout()
        self.diff_r_text = QLineEdit(str(self.diffuse[0]))
        self.diff_g_text = QLineEdit(str(self.diffuse[1]))
        self.diff_b_text = QLineEdit(str(self.diffuse[2]))
        self.diff_a_text = QLineEdit(str(self.diffuse[3]))
        self.diffuse_box.addWidget(QLabel("R:"))
        self.diffuse_box.addWidget(self.diff_r_text)
        self.diffuse_box.addWidget(QLabel("G:"))
        self.diffuse_box.addWidget(self.diff_g_text)
        self.diffuse_box.addWidget(QLabel("B:"))
        self.diffuse_box.addWidget(self.diff_b_text)
        self.diffuse_box.addWidget(QLabel("A:"))
        self.diffuse_box.addWidget(self.diff_a_text)

        # Specular (z atrybutu!)
        self.specular_title = QLabel("Specular (RGBA)")
        self.specular_box = QHBoxLayout()
        self.spec_r_text = QLineEdit(str(self.specular[0]))
        self.spec_g_text = QLineEdit(str(self.specular[1]))
        self.spec_b_text = QLineEdit(str(self.specular[2]))
        self.spec_a_text = QLineEdit(str(self.specular[3]))
        self.specular_box.addWidget(QLabel("R:"))
        self.specular_box.addWidget(self.spec_r_text)
        self.specular_box.addWidget(QLabel("G:"))
        self.specular_box.addWidget(self.spec_g_text)
        self.specular_box.addWidget(QLabel("B:"))
        self.specular_box.addWidget(self.spec_b_text)
        self.specular_box.addWidget(QLabel("A:"))
        self.specular_box.addWidget(self.spec_a_text)

        # Apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_figure_params)

        # Add to layout
        section_layout.addWidget(self.location_title)
        section_layout.addLayout(self.location_box)
        section_layout.addWidget(self.size_title)
        section_layout.addLayout(self.size_box)
        section_layout.addWidget(self.rotation_title)
        section_layout.addLayout(self.rotation_box)
        section_layout.addWidget(self.diffuse_title)
        section_layout.addLayout(self.diffuse_box)
        section_layout.addWidget(self.specular_title)
        section_layout.addLayout(self.specular_box)
        section_layout.addWidget(self.apply_btn)


    def apply_scale(self, scale_x, scale_y, scale_z):

        # original_vertices: [x, y, z, nx, ny, nz] flat array
        scaled_vertices = self.original_vertices.copy()
        # Skaluje tylko pozycje (co 6 wartości, 3 pierwsze to xyz)
        for i in range(0, len(scaled_vertices), 6):
            scaled_vertices[i] *= scale_x      # x
            scaled_vertices[i+1] *= scale_y    # y
            scaled_vertices[i+2] *= scale_z    # z

        # Przekaż do OpenGL (metoda w gl_widget, która aktualizuje VAO/VBO)
        self.current_vertices = scaled_vertices
        self.gl_widget.updateModelVertices(self.index, scaled_vertices)


    def apply_figure_params(self):
        chosen_frame_number = 1  # Stały numer dla wartości bazowych (domyślnych)

        # Upewnij się, że ten frame istnieje
        if chosen_frame_number not in self.params_in_frames:
            self.params_in_frames[chosen_frame_number] = {}

        try:
            self.params_in_frames[chosen_frame_number]["centroid"] = (
                float(self.loc_x_text.text()),
                float(self.loc_y_text.text()),
                float(self.loc_z_text.text()),
            )
            size_x = float(self.siz_x_text.text())
            size_y = float(self.siz_y_text.text())
            size_z = float(self.siz_z_text.text())
            self.params_in_frames[chosen_frame_number]["size_x"] = size_x
            self.params_in_frames[chosen_frame_number]["size_y"] = size_y
            self.params_in_frames[chosen_frame_number]["size_z"] = size_z
            self.params_in_frames[chosen_frame_number]["rot_x"] = float(self.rot_x_text.text())
            self.params_in_frames[chosen_frame_number]["rot_y"] = float(self.rot_y_text.text())
            self.params_in_frames[chosen_frame_number]["rot_z"] = float(self.rot_z_text.text())
            # Diffuse i specular zapisujemy bezpośrednio w atrybutach self
            self.diffuse = (
                float(self.diff_r_text.text()),
                float(self.diff_g_text.text()),
                float(self.diff_b_text.text()),
                float(self.diff_a_text.text()),
            )
            self.specular = (
                float(self.spec_r_text.text()),
                float(self.spec_g_text.text()),
                float(self.spec_b_text.text()),
                float(self.spec_a_text.text()),
            )
            print(f"Zapisano wartości podstawowe do frame #{chosen_frame_number}")
            self.apply_scale(size_x, size_y, size_z)

        except ValueError:
            print("Błąd: wprowadzone wartości muszą być liczbami")
            



    def display_frame_figure(self):
        chosen_frame_number = self.main_window.get_chosen_frame()
        # work only if the frame is chosen and the frame is filled
        if chosen_frame_number != -1 and chosen_frame_number in self.main_window.frame_numbers:
            section_layout = self.main_window.parameters_frame_area
            clear_layout(section_layout)
            section_title = self.main_window.param_frame_number
            section_title.setText(self.name + ' in Frame #' + str(chosen_frame_number))
            section_layout.addWidget(section_title)
            # prepare boxes
            self.location_title = QLabel("Location")
            self.location_box = QHBoxLayout()
            self.size_title = QLabel("Size")
            self.size_box = QHBoxLayout()
            self.rotation_title = QLabel("Rotation")
            self.rotation_box = QHBoxLayout()
            self.apply_btn = QPushButton("Apply")
            self.apply_btn.clicked.connect(self.apply_changes)
            #prepare location
            self.loc_x_label = QLabel("x:")
            self.loc_x_text = QLineEdit(self)
            self.loc_x_text.setText(str(self.params_in_frames[chosen_frame_number]["centroid"][0]))
            self.loc_y_label = QLabel("y:")
            self.loc_y_text = QLineEdit(self)
            self.loc_y_text.setText(str(self.params_in_frames[chosen_frame_number]["centroid"][1]))
            self.loc_z_label = QLabel("z:")
            self.loc_z_text = QLineEdit(self)
            self.loc_z_text.setText(str(self.params_in_frames[chosen_frame_number]["centroid"][2]))
            self.location_box.addWidget(self.loc_x_label)
            self.location_box.addWidget(self.loc_x_text)
            self.location_box.addWidget(self.loc_y_label)
            self.location_box.addWidget(self.loc_y_text)
            self.location_box.addWidget(self.loc_z_label)
            self.location_box.addWidget(self.loc_z_text)
            #prepare size
            self.siz_x_label = QLabel("x:")
            self.siz_x_text = QLineEdit(self)
            self.siz_x_text.setText(str(self.params_in_frames[chosen_frame_number]["size_x"]))
            self.siz_y_label = QLabel("y:")
            self.siz_y_text = QLineEdit(self)
            self.siz_y_text.setText(str(self.params_in_frames[chosen_frame_number]["size_y"]))
            self.siz_z_label = QLabel("z:")
            self.siz_z_text = QLineEdit(self)
            self.siz_z_text.setText(str(self.params_in_frames[chosen_frame_number]["size_z"]))
            self.size_box.addWidget(self.siz_x_label)
            self.size_box.addWidget(self.siz_x_text)
            self.size_box.addWidget(self.siz_y_label)
            self.size_box.addWidget(self.siz_y_text)
            self.size_box.addWidget(self.siz_z_label)
            self.size_box.addWidget(self.siz_z_text)
            #prepare rotation
            self.rot_x_label = QLabel("x:")
            self.rot_x_text = QLineEdit(self)
            self.rot_x_text.setText(str(self.params_in_frames[chosen_frame_number]["rot_x"]))
            self.rot_y_label = QLabel("y:")
            self.rot_y_text = QLineEdit(self)
            self.rot_y_text.setText(str(self.params_in_frames[chosen_frame_number]["rot_y"]))
            self.rot_z_label = QLabel("z:")
            self.rot_z_text = QLineEdit(self)
            self.rot_z_text.setText(str(self.params_in_frames[chosen_frame_number]["rot_z"]))
            self.rotation_box.addWidget(self.rot_x_label)
            self.rotation_box.addWidget(self.rot_x_text)
            self.rotation_box.addWidget(self.rot_y_label)
            self.rotation_box.addWidget(self.rot_y_text)
            self.rotation_box.addWidget(self.rot_z_label)
            self.rotation_box.addWidget(self.rot_z_text)

            #connect validate changes
            self.loc_x_text.textChanged.connect(self.validate_inputs)
            self.loc_y_text.textChanged.connect(self.validate_inputs)
            self.loc_z_text.textChanged.connect(self.validate_inputs)
            self.siz_x_text.textChanged.connect(self.validate_inputs)
            self.siz_y_text.textChanged.connect(self.validate_inputs)
            self.siz_z_text.textChanged.connect(self.validate_inputs)
            self.rot_x_text.textChanged.connect(self.validate_inputs)
            self.rot_y_text.textChanged.connect(self.validate_inputs)
            self.rot_z_text.textChanged.connect(self.validate_inputs)

            #add to main layout
            section_layout.addWidget(self.location_title)
            section_layout.addLayout(self.location_box)
            section_layout.addWidget(self.size_title)
            section_layout.addLayout(self.size_box)
            section_layout.addWidget(self.rotation_title)
            section_layout.addLayout(self.rotation_box)
            section_layout.addWidget(self.apply_btn)


    def apply_changes(self):
        chosen_frame_number = self.main_window.get_chosen_frame()
        if chosen_frame_number != -1:
           self.params_in_frames[chosen_frame_number]["centroid"] = (float(self.loc_x_text.text()), float(self.loc_y_text.text()), float(self.loc_z_text.text()))
           self.params_in_frames[chosen_frame_number]["size_x"] = float(self.siz_x_text.text())
           self.params_in_frames[chosen_frame_number]["size_y"] = float(self.siz_y_text.text())
           self.params_in_frames[chosen_frame_number]["size_z"] = float(self.siz_z_text.text())
           self.params_in_frames[chosen_frame_number]["rot_x"] = float(self.rot_x_text.text())
           self.params_in_frames[chosen_frame_number]["rot_y"] = float(self.rot_y_text.text())
           self.params_in_frames[chosen_frame_number]["rot_z"] = float(self.rot_z_text.text())


    def validate_inputs(self):
        valid = all(is_valid_float(edit.text()) for edit in [
        self.loc_x_text, self.loc_y_text,self.loc_z_text, 
        self.siz_x_text, self.siz_y_text, self.siz_z_text,
        self.rot_x_text, self.rot_y_text, self.rot_z_text])
        self.apply_btn.setEnabled(valid)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Program do animacji")

        # two main sections
        self.objects_gl_editor_widget = QWidget()
        self.animation_widget = QWidget()

        # layouts
        self.everything_layout = QVBoxLayout()
        self.objects_gl_editor_layout = QHBoxLayout()
        self.objects_layout = QVBoxLayout()
        self.editor_layout = QVBoxLayout()
        self.animation_layout = QVBoxLayout()

        self.gl_widget = MyGLWidget()

        # prepare object section
        # ambient row
        self.helper_ambient = QWidget()
        self.helper_ambient.setStyleSheet("border: 2px solid black;")
        self.ambient_area = QHBoxLayout()
        self.ambient_label = QLabel("Ambient: ", self)
        self.ambient_label.setStyleSheet("border: none;")
        self.ambient_textbox = QLineEdit(self)
        self.ambient_area.addWidget(self.ambient_label)
        self.ambient_area.addWidget(self.ambient_textbox)
        self.helper_ambient.setLayout(self.ambient_area)
        # figures title
        self.helper_figure_title = QWidget()
        self.helper_figure_title.setStyleSheet("border: 2px solid black;")
        self.figure_title_row = QHBoxLayout()
        self.figure_label = QLabel("Figures ", self)
        self.figure_label.setStyleSheet("border: none;")

        self.figure_add = QPushButton("+")
        self.figure_add.clicked.connect(self.load_model)

        self.figure_title_row.addWidget(self.figure_label)
        self.figure_title_row.addWidget(self.figure_add)
        self.helper_figure_title.setLayout(self.figure_title_row)
        # figures scrollable box
        self.helper_figure_box = QWidget()
        self.helper_figure_box.setStyleSheet("border: 2px solid black;")
        self.figure_box = QVBoxLayout()
        self.figure_scroll = QScrollArea(self)
        self.figure_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.figure_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.figure_scroll.setLayout(self.figure_box)
        self.helper_figure_box.setLayout(self.figure_box)
        self.figure_scroll.setWidgetResizable(True)
        self.figure_scroll.setWidget(self.helper_figure_box)

        # lights title
        self.helper_lights_title = QWidget()
        self.helper_lights_title.setStyleSheet("border: 2px solid black;")
        self.lights_title_row = QHBoxLayout()
        self.lights_label = QLabel("Lights ", self)
        self.lights_label.setStyleSheet("border: none;")
        self.lights_add = QPushButton("+")
        self.lights_title_row.addWidget(self.lights_label)
        self.lights_title_row.addWidget(self.lights_add)
        self.helper_lights_title.setLayout(self.lights_title_row)
        # lights scrollable box
        self.helper_lights_box = QWidget()
        self.helper_lights_box.setStyleSheet("border: 2px solid black;")
        self.lights_box = QVBoxLayout()
        self.lights_scroll = QScrollArea(self)
        self.lights_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.lights_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.lights_scroll.setLayout(self.lights_box)
        self.helper_lights_box.setLayout(self.lights_box)
        self.lights_scroll.setWidgetResizable(True)
        self.lights_scroll.setWidget(self.helper_lights_box)
        # add to objects layout
        self.objects_layout.addWidget(self.helper_ambient, stretch=1)
        self.objects_layout.addWidget(self.helper_figure_title, stretch=2)
        self.objects_layout.addWidget(self.figure_scroll, stretch=10)
        self.objects_layout.addWidget(self.helper_lights_title, stretch=2)
        self.objects_layout.addWidget(self.lights_scroll, stretch=10)

        # prepare editor section
        # camera section
        self.camera_controls_group = QGroupBox("Camera")
        self.camera_controls_group.setStyleSheet(
            """
            QGroupBox {
                border: 2px solid black;
                margin-top: 12px;        
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
        """
        )

        self.camera_controls_layout = QHBoxLayout()

        self.move_camera_button = QPushButton("Move")
        self.move_camera_button.setCheckable(True)
        self.move_camera_button.toggled.connect(
            self.gl_widget.set_camera_interaction_active
        )

        self.reset_camera_button = QPushButton("Reset")
        self.reset_camera_button.clicked.connect(self.reset_camera_view)

        self.camera_controls_layout.addWidget(self.move_camera_button)
        self.camera_controls_layout.addWidget(self.reset_camera_button)
        self.camera_controls_group.setLayout(self.camera_controls_layout)

        # parameters of an object
        self.helper_parameters_object = QWidget()
        self.helper_parameters_object.setStyleSheet("border: 2px solid black;")
        self.parameters_object_area = QVBoxLayout()
        self.param_object_name = QLabel("Object not chosen", self)
        self.parameters_object_area.addWidget(self.param_object_name)
        self.helper_parameters_object.setLayout(self.parameters_object_area)
        # parameters of a frame
        self.helper_parameters_frame = QWidget()
        self.helper_parameters_frame.setStyleSheet("border: 2px solid black;")
        self.parameters_frame_area = QVBoxLayout()
        self.param_frame_number = QLabel("Object in frame not chosen", self)
        self.parameters_frame_area.addWidget(self.param_frame_number)
        self.helper_parameters_frame.setLayout(self.parameters_frame_area)
        # add to editor layout
        self.editor_layout.addWidget(self.camera_controls_group, stretch=1)
        self.editor_layout.addWidget(self.helper_parameters_object, stretch=12)
        self.editor_layout.addWidget(self.helper_parameters_frame, stretch=12)
        # prepare animation section
        self.helper_animation_header = QWidget()
        self.helper_animation_header.setStyleSheet("border: 2px solid black;")
        self.helper_animation_frames = QWidget()
        self.helper_animation_frames.setStyleSheet("border: 2px solid black;")
        self.animation_header_layout = QHBoxLayout()
        self.animation_frames_layout = QHBoxLayout()

        # header
        self.animation_label = QLabel("Animation")
        self.add_frame_btn = QPushButton("+")
        self.add_frame_btn.clicked.connect(self.add_frame)
        self.delete_frame_btn = QPushButton("X")
        self.delete_frame_btn.clicked.connect(self.delete_frame)
        self.frame_number = QLabel("Frame #")
        self.download = QPushButton("Download film")
        self.animation_header_layout.addWidget(self.animation_label)
        self.animation_header_layout.addWidget(self.add_frame_btn)
        self.animation_header_layout.addWidget(self.delete_frame_btn)
        self.animation_header_layout.addWidget(self.frame_number)
        self.animation_header_layout.addWidget(self.download)
        self.helper_animation_header.setLayout(self.animation_header_layout)

        self.animation_frames_scroll_area = QScrollArea()
        self.animation_frames_scroll_area.setWidgetResizable(True)
        self.animation_frames_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.animation_frames_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.animation_frames_container = QWidget()
        self.animation_frames_layout_internal = QHBoxLayout(
            self.animation_frames_container
        )
        self.animation_frames_layout_internal.setContentsMargins(0, 0, 0, 0)
        self.animation_frames_layout_internal.setSpacing(2)

        for i in range(100):
            btn = QPushButton(f"{i+1}")
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked=False, n=i+1: self.frame_chosen(n))
            self.animation_frames_layout_internal.addWidget(btn)
        self.frame_numbers = []

        self.animation_frames_scroll_area.setWidget(self.animation_frames_container)

        _layout_for_helper_animation_frames = QVBoxLayout(self.helper_animation_frames)
        _layout_for_helper_animation_frames.addWidget(self.animation_frames_scroll_area)

        # add to animation layout
        self.animation_layout.addWidget(self.helper_animation_header)
        self.animation_layout.addWidget(self.helper_animation_frames)

        # put layouts inside one another
        self.objects_gl_editor_layout.addLayout(self.objects_layout, stretch=2)
        self.objects_gl_editor_layout.addWidget(self.gl_widget, stretch=5)
        self.objects_gl_editor_layout.addLayout(self.editor_layout, stretch=2)
        self.objects_gl_editor_widget.setLayout(self.objects_gl_editor_layout)
        self.animation_widget.setLayout(self.animation_layout)
        self.everything_layout.addWidget(self.objects_gl_editor_widget, stretch=26)
        self.everything_layout.addWidget(self.animation_widget, stretch=7)

        self.setLayout(self.everything_layout)
        self.resize(1200, 800)

    def delete_frame(self):
        chosen_frame_number = self.get_chosen_frame()
        if chosen_frame_number != -1:
            if(chosen_frame_number in self.frame_numbers): # we do nothing if this frame is empty
                for i in range(self.figure_box.count()):
                    figure = self.figure_box.itemAt(i)
                    figure_widget = figure.widget()
                    if isinstance(figure_widget, FigureItem):
                        figure_widget.params_in_frames.pop(chosen_frame_number)
                # TODO usuwanie klatki ze słowników obiektów świateł
                self.frame_numbers.remove(chosen_frame_number)
                button = self.animation_frames_layout_internal.itemAt(chosen_frame_number-1).widget()
                button.setStyleSheet("background-color: none;")

    def add_frame(self):
        chosen_frame_number = self.get_chosen_frame()
        if chosen_frame_number != -1:
            if(not chosen_frame_number in self.frame_numbers): # we do nothing if there is already frame inside
                self.frame_numbers.append(chosen_frame_number)
                self.frame_numbers.sort()
                this_frame_index = self.frame_numbers.index(chosen_frame_number)
                if this_frame_index == 0: # no frames before
                    for i in range(self.figure_box.count()):
                        figure = self.figure_box.itemAt(i)
                        figure_widget = figure.widget()
                        if isinstance(figure_widget, FigureItem):
                            set_frame_to_figure(figure_widget, chosen_frame_number)
                else:
                    for i in range(self.figure_box.count()):
                        figure = self.figure_box.itemAt(i)
                        figure_widget = figure.widget()
                        if isinstance(figure_widget, FigureItem):
                            params = figure_widget.params_in_frames[self.frame_numbers[this_frame_index-1]]
                            set_frame_to_figure(figure_widget, chosen_frame_number, params)
                # TODO dodawanie klatki do słowników obiektów świateł
                # pokoloruj klatkę jeśli jest pełna
                button = self.animation_frames_layout_internal.itemAt(chosen_frame_number-1).widget()
                button.setStyleSheet("background-color: black;")

    def frame_chosen(self, number):
        self.frame_number.setText(f'Frame #{number}')

    def reset_camera_view(self):
        self.gl_widget.camera.reset_state()
        self.gl_widget.update()

    def load_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose OBJ file", "", "OBJ Files (*.obj)"
        )
        if not file_path:
            return  # user canceled action

        try:
            vertices_list, faces = load_obj(file_path)
            if not vertices_list or not faces:
                raise ValueError("Nie znaleziono poprawnych danych w pliku.")

            # Calculate normals and prepare data in the format: [x, y, z, nx, ny, nz]
            vertex_data = []
            for face in faces:
                v0 = np.array(vertices_list[face[0]])
                v1 = np.array(vertices_list[face[1]])
                v2 = np.array(vertices_list[face[2]])

                # normal for triangle
                normal = np.cross(v1 - v0, v2 - v0)
                normal = (
                    normal / np.linalg.norm(normal)
                    if np.linalg.norm(normal) > 0
                    else np.array([0.0, 0.0, 1.0])
                )

                for idx in face[:3]:  # triangles are assumed
                    pos = vertices_list[idx]
                    vertex_data.extend([*pos, *normal])

            vertices_np = np.array(vertex_data, dtype=np.float32)

            self.gl_widget.loadModel(vertices_np)

            # Add figure name to scrollbox:
            file_name = file_path.split("/")[-1]
            index = len(self.gl_widget.additional_vaos) - 1  # Ostatni dodany

            centroid, size_x, size_y, size_z = get_model_parameters(vertices_list)
            figure_item = FigureItem(file_name, self.gl_widget, index, self.figure_box, self, centroid, vertices_np)
            for frame in self.frame_numbers:
                set_frame_to_figure(figure_item, frame)
            self.figure_box.addWidget(figure_item)

        except Exception as e:
            QMessageBox.critical(
                self, "Błąd", f"Nie udało się wczytać modelu:\n{str(e)}"
            )
            
    def get_chosen_frame(self):
        chosen_frame_text = self.frame_number.text()
        find_hash = chosen_frame_text.find('#')
        chosen_frame_number_str = chosen_frame_text[find_hash+1:]
        if(chosen_frame_number_str != ""):
            chosen_frame_number = int(chosen_frame_number_str)
            return chosen_frame_number
        return -1

    def on_button_click(self):
        self.gl_widget.change_background_color(0.2, 0.0, 0.5)

def get_model_parameters(vertices):
    min_x = min(vertex[0] for vertex in vertices)
    max_x = max(vertex[0] for vertex in vertices)
    min_y = min(vertex[1] for vertex in vertices)
    max_y = max(vertex[1] for vertex in vertices)
    min_z = min(vertex[2] for vertex in vertices)
    max_z = max(vertex[2] for vertex in vertices)
    center = (
        (min_x + max_x) / 2,
        (min_y + max_y) / 2,
        (min_z + max_z) / 2,
    )
    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z
    return center, size_x, size_y, size_z

def set_frame_to_figure(figure_widget, chosen_frame_number, params={}):
    if(len(params) == 0):
        figure_widget.params_in_frames[chosen_frame_number] = {
            'centroid': figure_widget.centroid,
            'size_x': figure_widget.size_x,
            'size_y': figure_widget.size_y,
            'size_z': figure_widget.size_z,
            'rot_x': 0,
            'rot_y': 0,
            'rot_z': 0}
    else:
        figure_widget.params_in_frames[chosen_frame_number] = {
            'centroid': params['centroid'],
            'size_x': params['size_x'],
            'size_y': params['size_y'],
            'size_z': params['size_z'],
            'rot_x': params['rot_x'],
            'rot_y': params['rot_y'],
            'rot_z': params['rot_z']}

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
        else:
            # Jeśli to np. layout zagnieżdżony
            sub_layout = item.layout()
            if sub_layout is not None:
                clear_layout(sub_layout)

def is_valid_float(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
