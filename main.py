from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QScrollArea, QFileDialog, QMessageBox
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader, QMatrix4x4, QVector3D
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QSize
from OpenGL.GL import *
from OpenGL.GLU import *
from utils.cube import generate_cube
from loader.obj_loader import load_obj
import numpy as np
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
        self.additional_vaos = []
        self.additional_vbos = []
        self.additional_vertex_counts = []

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        self.initShaders()
        self.initCube()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader_program.bind()

        # Matryce
        model = QMatrix4x4()
        model.translate(0.0, 0.0, 0.0)

        view = QMatrix4x4()
        view.lookAt(QVector3D(3, 3, 5), QVector3D(0, 0, 0), QVector3D(0, 1, 0))

        projection = QMatrix4x4()
        projection.perspective(45.0, self.width() / self.height(), 0.1, 100.0)

        self.shader_program.setUniformValue("M", model)
        self.shader_program.setUniformValue("view", view)
        self.shader_program.setUniformValue("projection", projection)
        self.shader_program.setUniformValue("lightPos", 5.0, 5.0, 5.0)
        self.shader_program.setUniformValue("viewPos", 3.0, 3.0, 5.0)
        self.shader_program.setUniformValue("objectColor", 1.0, 0.3, 0.3)
        self.shader_program.setUniformValue("lightColor", 1.0, 1.0, 1.0)

        self.shader_program.setUniformValue("material_ambient", 0.2, 0.2, 0.2)
        self.shader_program.setUniformValue("material_diffuse", 1.0, 1.0, 1.0)
        self.shader_program.setUniformValue("material_shininess", 32.0)
        self.shader_program.setUniformValue("color", 1.0, 0.3, 0.3)
        self.shader_program.setUniformValue("camera_position", 3.0, 3.0, 5.0)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        # glBindVertexArray(0)

        for vao, count in zip(self.additional_vaos, self.additional_vertex_counts):
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLES, 0, count)
        glBindVertexArray(0)

        self.shader_program.release()

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
        vertices = generate_cube()  # use function that generates the cube

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Positions
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # Normals
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)


    def loadModel(self, vertices_np):
        self.makeCurrent()  # activate OpenGL context


        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices_np.nbytes, vertices_np, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices_np.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices_np.itemsize, ctypes.c_void_p(3 * vertices_np.itemsize))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)


        # save to list to draw in paintGL
        self.additional_vaos.append(vao)
        self.additional_vbos.append(vbo)
        self.additional_vertex_counts.append(len(vertices_np) // 6)



        self.doneCurrent()  # free context
        self.update()



    def perspective(self, fov, aspect, near, far):
        f = 1.0 / np.tan(np.radians(fov) / 2)
        m = np.zeros((4, 4), dtype=np.float32)
        m[0, 0] = f / aspect
        m[1, 1] = f
        m[2, 2] = (far + near) / (near - far)
        m[2, 3] = (2 * far * near) / (near - far)
        m[3, 2] = -1.0
        return m

    def lookAt(self, eye, target, up):
        f = (target - eye)
        f /= np.linalg.norm(f)
        s = np.cross(f, up)
        s /= np.linalg.norm(s)
        u = np.cross(s, f)

        m = np.identity(4, dtype=np.float32)
        m[0, 0:3] = s
        m[1, 0:3] = u
        m[2, 0:3] = -f
        m[0, 3] = -np.dot(s, eye)
        m[1, 3] = -np.dot(u, eye)
        m[2, 3] = np.dot(f, eye)
        return m

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
        self.figure_add.clicked.connect(self.load_model)

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
        
        # prepare animation section
        self.helper_animation_header = QWidget()
        self.helper_animation_header.setStyleSheet("border: 2px solid black;")
        self.helper_animation_frames = QWidget()
        self.helper_animation_frames.setStyleSheet("border: 2px solid black;")
        self.animation_header = QHBoxLayout()
        self.animation_frames = QHBoxLayout()
        # header
        self.animation_label = QLabel("Animation")
        self.add_frame = QPushButton("+")
        self.delete_frame = QPushButton("X")
        self.frame_number = QLabel("Frame #")
        self.download = QPushButton("Download film")
        self.animation_header.addWidget(self.animation_label)
        self.animation_header.addWidget(self.add_frame)
        self.animation_header.addWidget(self.delete_frame)
        self.animation_header.addWidget(self.frame_number)
        self.animation_header.addWidget(self.download)
        self.helper_animation_header.setLayout(self.animation_header)
        # frames 
        for i in range(40):
            self.animation_frames.addWidget(QPushButton(""))
        self.helper_animation_frames.setLayout(self.animation_frames)
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
        self.resize(400, 500)



    def load_model(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose OBJ file", "", "OBJ Files (*.obj)")
        if not file_path:
            return  # user canceled action

        try:
            vertices_list, faces  = load_obj(file_path)
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
                normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else np.array([0.0, 0.0, 1.0])

                for idx in face[:3]:  # triangles are assumed
                    pos = vertices_list[idx]
                    vertex_data.extend([*pos, *normal])

            vertices_np = np.array(vertex_data, dtype=np.float32)


            self.gl_widget.loadModel(vertices_np)



        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać modelu:\n{str(e)}")

    def on_button_click(self):
        self.gl_widget.change_background_color(0.2, 0.0, 0.5)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())
