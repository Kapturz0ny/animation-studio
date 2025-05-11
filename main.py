from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QScrollArea
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader, QMatrix4x4, QVector3D, QMouseEvent, QWheelEvent 
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QSize, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
from utils.cube import generate_cube
from utils.camera import Camera
import sys

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

        self.camera = Camera(position=QVector3D(3, 3, 5))
        self.camera_interaction_mode = False
        self.last_mouse_pos = QPoint()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
        self.initShaders()
        self.initCube()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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

        self.shader_program.setUniformValue("lightPos", 5.0, 5.0, 5.0)
        self.shader_program.setUniformValue("viewPos", self.camera.position.x(), self.camera.position.y(), self.camera.position.z())
        self.shader_program.setUniformValue("objectColor", 1.0, 0.3, 0.3)
        self.shader_program.setUniformValue("lightColor", 1.0, 1.0, 1.0)

        self.shader_program.setUniformValue("material_ambient", 0.2, 0.2, 0.2)
        self.shader_program.setUniformValue("material_diffuse", 1.0, 1.0, 1.0)
        self.shader_program.setUniformValue("material_shininess", 32.0)
        self.shader_program.setUniformValue("color", 1.0, 0.3, 0.3)
        self.shader_program.setUniformValue("camera_position", 3.0, 3.0, 5.0)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glBindVertexArray(0)

        self.shader_program.release()

    def mousePressEvent(self, event: QMouseEvent):
        if self.camera_interaction_mode and event.buttons() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.update()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.camera_interaction_mode and event.buttons() == Qt.MouseButton.LeftButton:

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
            self.update()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if self.camera_interaction_mode:
            scroll_delta = event.angleDelta().y() / 120
            self.camera.process_mouse_scroll(scroll_delta)
            self.update()
        else:
            super().wheelEvent(event)

    def initShaders(self):
        self.shader_program = QOpenGLShaderProgram()
        if not self.shader_program.addShaderFromSourceFile(QOpenGLShader.Vertex, phong_vert):
            print("Błąd wczytywania vertex shadera")
        if not self.shader_program.addShaderFromSourceFile(QOpenGLShader.Fragment, phong_frag):
            print("Błąd wczytywania fragment shadera")
        self.shader_program.bindAttributeLocation("position", 0)
        self.shader_program.bindAttributeLocation("normal", 1)

        if not self.shader_program.link():
            print("Błąd linkowania shaderów")

    def initCube(self):
        vertices = generate_cube()  # Użyj funkcji generującej sześcian z cube.py

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Pozycje
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # Normalne
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def change_background_color(self, r, g, b):
        self.color = [r, g, b]
        self.update()
        

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Program do animacji")
        self.setGeometry(700, 300, 500, 500)

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
        self.figure_title_row.addWidget(self.figure_label)
        self.figure_title_row.addWidget(self.figure_add)
        self.helper_figure_title.setLayout(self.figure_title_row)
        #figures scrollable box
        self.helper_figure_box = QWidget()
        self.helper_figure_box.setStyleSheet("border: 2px solid black;")
        self.figure_box = QVBoxLayout()
        self.figure_scroll = QScrollArea(self)
        self.figure_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.figure_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.figure_scroll.setLayout(self.figure_box)
        self.helper_figure_box.setLayout(self.figure_box)
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
        #lights scrollable box
        self.helper_lights_box = QWidget()
        self.helper_lights_box.setStyleSheet("border: 2px solid black;")
        self.lights_box = QVBoxLayout()
        self.lights_scroll = QScrollArea(self)
        self.lights_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.lights_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lights_scroll.setLayout(self.lights_box)
        self.helper_lights_box.setLayout(self.lights_box)
        # add to objects layout
        self.objects_layout.addWidget(self.helper_ambient, stretch=1)
        self.objects_layout.addWidget(self.helper_figure_title, stretch=2)
        self.objects_layout.addWidget(self.helper_figure_box, stretch=10)
        self.objects_layout.addWidget(self.helper_lights_title, stretch=2)
        self.objects_layout.addWidget(self.helper_lights_box, stretch=10)

        # prepare editor section
        # buttons row
        self.helper_buttons = QWidget()
        self.helper_buttons.setStyleSheet("border: 2px solid black;")
        self.buttons_area = QHBoxLayout()
        self.cursor_button = QPushButton("^")
        
        self.arrows_button = QPushButton("move camera")
        self.arrows_button.setCheckable(True) 
        self.arrows_button.toggled.connect(self.toggle_camera_mode) 

        self.hand_button = QPushButton("hand")
        self.buttons_area.addWidget(self.cursor_button)
        self.buttons_area.addWidget(self.arrows_button)
        self.buttons_area.addWidget(self.hand_button)
        self.helper_buttons.setLayout(self.buttons_area)
        
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
        self.param_frame_number = QLabel("Frame not chosen", self)
        self.parameters_frame_area.addWidget(self.param_frame_number)
        self.helper_parameters_frame.setLayout(self.parameters_frame_area)
        # add to editor layout
        self.editor_layout.addWidget(self.helper_buttons, stretch=1)
        self.editor_layout.addWidget(self.helper_parameters_object, stretch=12)
        self.editor_layout.addWidget(self.helper_parameters_frame, stretch=12)
        
        #prepare animation section
        self.helper_animation_header = QWidget()
        self.helper_animation_header.setStyleSheet("border: 2px solid black;")
        self.helper_animation_frames = QWidget() 
        self.helper_animation_frames.setStyleSheet("border: 2px solid black;")
        self.animation_header_layout = QHBoxLayout() 
        self.animation_frames_layout = QHBoxLayout() 
        
        #header
        self.animation_label = QLabel("Animation")
        self.add_frame = QPushButton("+")
        self.delete_frame = QPushButton("X")
        self.frame_number = QLabel("Frame #")
        self.download = QPushButton("Download film")
        self.animation_header_layout.addWidget(self.animation_label)
        self.animation_header_layout.addWidget(self.add_frame)
        self.animation_header_layout.addWidget(self.delete_frame)
        self.animation_header_layout.addWidget(self.frame_number)
        self.animation_header_layout.addWidget(self.download)
        self.helper_animation_header.setLayout(self.animation_header_layout)
        
        self.animation_frames_scroll_area = QScrollArea()
        self.animation_frames_scroll_area.setWidgetResizable(True)
        self.animation_frames_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.animation_frames_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 

        self.animation_frames_container = QWidget() 
        self.animation_frames_layout_internal = QHBoxLayout(self.animation_frames_container) 
        self.animation_frames_layout_internal.setContentsMargins(0,0,0,0)
        self.animation_frames_layout_internal.setSpacing(2)

        for i in range(40): 
            btn = QPushButton(f"{i+1}")
            btn.setFixedSize(40,40) 
            self.animation_frames_layout_internal.addWidget(btn)
        
        self.animation_frames_scroll_area.setWidget(self.animation_frames_container)

        _layout_for_helper_animation_frames = QVBoxLayout(self.helper_animation_frames)
        _layout_for_helper_animation_frames.addWidget(self.animation_frames_scroll_area)

        #add to animation layout
        self.animation_layout.addWidget(self.helper_animation_header)
        self.animation_layout.addWidget(self.helper_animation_frames) 

        #put layouts inside one another
        self.objects_gl_editor_layout.addLayout(self.objects_layout, stretch=2)
        self.objects_gl_editor_layout.addWidget(self.gl_widget, stretch=5)
        self.objects_gl_editor_layout.addLayout(self.editor_layout, stretch=2)
        self.objects_gl_editor_widget.setLayout(self.objects_gl_editor_layout)
        self.animation_widget.setLayout(self.animation_layout)
        self.everything_layout.addWidget(self.objects_gl_editor_widget, stretch=26)
        self.everything_layout.addWidget(self.animation_widget, stretch=7)

        self.setLayout(self.everything_layout)
        self.resize(1200, 800) 

    def toggle_camera_mode(self, checked):
        self.gl_widget.camera_interaction_mode = checked
        if checked:
            self.gl_widget.setFocus() 
            print("Tryb kamery (tylko mysz) WŁĄCZONY")
        else:
            self.gl_widget.clearFocus() 
            self.gl_widget.unsetCursor() 
            print("Tryb kamery (tylko mysz) WYŁĄCZONY")

    def on_button_click(self):
        self.gl_widget.change_background_color(0.2, 0.0, 0.5)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())
