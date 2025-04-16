from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QScrollArea
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QSize
from OpenGL.GL import *
import sys

class MyGLWidget(QOpenGLWidget):
    def __init__(self):
        super(MyGLWidget, self).__init__()
        self.color = [0.1, 0.1, 0.1]

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)

    def paintGL(self):
        glClearColor(*self.color, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def change_background_color(self, r, g, b):
        self.color = [r, g, b]
        self.update()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Program do animacji")
        self.setGeometry(700, 300, 500, 500)
        label5 = QLabel("#5", self)
        label5.setStyleSheet("background-color: purple;")

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
        self.animation_layout.addWidget(label5)

        #put layouts inside one another
        self.objects_gl_editor_layout.addLayout(self.objects_layout, stretch=2)
        self.objects_gl_editor_layout.addWidget(self.gl_widget, stretch=5)
        self.objects_gl_editor_layout.addLayout(self.editor_layout, stretch=2)
        self.objects_gl_editor_widget.setLayout(self.objects_gl_editor_layout)
        self.animation_widget.setLayout(self.animation_layout)
        self.everything_layout.addWidget(self.objects_gl_editor_widget, stretch=26)
        self.everything_layout.addWidget(self.animation_widget, stretch=7)

        self.setLayout(self.everything_layout)
        self.resize(400, 500)

    def on_button_click(self):
        self.gl_widget.change_background_color(0.2, 0.0, 0.5)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())
