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
from PyQt5.QtWidgets import QOpenGLWidget
from utils.camera import Camera, Direction
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import (
    QOpenGLShaderProgram,
    QOpenGLShader,
    QMatrix4x4,
    QVector3D,
    QMouseEvent,
    QWheelEvent,
    QKeyEvent,
)
import ctypes

phong_vert = "shaders/phong.vert"
phong_frag = "shaders/phong.frag"

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
        self.visible_lights = []

        self.camera = Camera(
            position=QVector3D(3, 3, 5), yaw=-135.0, pitch=-30.0, zoom_fov=45.0
        )
        self.lights = []

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
        self.shader_program.setUniformValue("material_ambient", 1.0, 0.2, 0.2)
        self.shader_program.setUniformValue("material_diffuse", 1.0, 0.2, 0.2)
        self.shader_program.setUniformValue("material_specular", 1.0, 1.0, 1.0)
        self.shader_program.setUniformValue("material_shininess", 32.0)        

        self.shader_program.setUniformValue("numLights", len(self.lights))
        for i, light in enumerate(self.lights):
            if self.visible_lights[i] is not False:
                self.shader_program.setUniformValue(f"lights[{i}].position", light["position"])
                self.shader_program.setUniformValue(f"lights[{i}].ambient", light["ambient"])
                self.shader_program.setUniformValue(f"lights[{i}].diffuse", light["diffuse"])
                self.shader_program.setUniformValue(f"lights[{i}].specular", light["specular"])

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

    def add_light(self, light):
        print("dodano światło")
        self.lights.append(light)
        self.visible_lights.append(True)  # domyślnie światło jest widoczne
        self.update()

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
    
    def delete_light(self, index):
        if 0 <= index < len(self.lights):
            del self.lights[index]
            self.update()
        else:
            print("Nieprawidłowy indeks światła do usunięcia")


    def change_background_color(self, r, g, b):
        self.color = [r, g, b]
        self.update()
