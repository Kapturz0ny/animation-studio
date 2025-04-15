from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtWidgets import QOpenGLWidget
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
        # tutaj rendering 3D itd.

    def change_background_color(self, r, g, b):
        self.color = [r, g, b]
        self.update()  # WYWOŁUJE PONOWNIE paintGL()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Program do animacji")
        self.setGeometry(700, 300, 500, 500)
        label1 = QLabel("#1", self)
        label2 = QLabel("#2", self)
        label3 = QLabel("#3", self)
        label4 = QLabel("#4", self)
        label5 = QLabel("#5", self)

        label1.setStyleSheet("background-color: red;")
        label2.setStyleSheet("background-color: yellow;")
        label3.setStyleSheet("background-color: green;")
        label4.setStyleSheet("background-color: blue;")
        label5.setStyleSheet("background-color: purple;")

        self.objects_gl_editor_widget = QWidget()
        self.animation_widget = QWidget()

        # layouts
        self.everything_layout = QVBoxLayout()
        self.everything_layout.setSpacing(0)
        self.objects_gl_editor_layout = QHBoxLayout()
        self.objects_layout = QVBoxLayout()
        self.gl_widget = MyGLWidget()
        self.editor_layout = QVBoxLayout()
        self.animation_layout = QVBoxLayout()

        self.objects_layout.addWidget(label1)
        self.objects_layout.addWidget(label2)
        self.editor_layout.addWidget(label3)
        self.editor_layout.addWidget(label4)
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
