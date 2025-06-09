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
    QInputDialog,
)
from PyQt5.QtGui import (
    QOpenGLShaderProgram,
    QOpenGLShader,
    QMatrix4x4,
    QVector3D,
    QMouseEvent,
    QWheelEvent,
    QKeyEvent,
    QImage,
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
import math
import sys
import imageio.v2 as iio

from loader.obj_loader import load_obj
from utils.camera import Camera, Direction
from items import LightItem, FigureItem
from my_gl_widget import MyGLWidget
from utils.styles import (
    pressed_button_style,
    std_border_style,
    camera_controls_group_style,
)

phong_vert = "shaders/phong.vert"
phong_frag = "shaders/phong.frag"





class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Program do animacji")

        self.lights_ever = 0

        # two main sections
        self.objects_gl_editor_widget = QWidget()
        self.animation_widget = QWidget()
        self.chosen_figure_item = None  # referencja do zaznaczonej figury
        self.chosen_frame_number = 1  # domyślnie pierwsza klatka

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
        self.helper_ambient.setStyleSheet(std_border_style)
        self.ambient_area = QHBoxLayout()
        self.ambient_label = QLabel("Ambient: ", self)
        self.ambient_label.setStyleSheet("border: none;")
        self.ambient_textbox = QLineEdit(self)
        self.ambient_area.addWidget(self.ambient_label)
        self.ambient_area.addWidget(self.ambient_textbox)
        self.helper_ambient.setLayout(self.ambient_area)
        # figures title
        self.helper_figure_title = QWidget()
        self.helper_figure_title.setStyleSheet(std_border_style)
        self.figure_title_row = QHBoxLayout()
        self.figure_label = QLabel("Figures ", self)
        self.figure_label.setStyleSheet("border: none;")

        self.figure_add = QPushButton("+")
        self.figure_add.clicked.connect(self.load_model)
        self.figure_add.setStyleSheet(pressed_button_style)

        self.figure_title_row.addWidget(self.figure_label)
        self.figure_title_row.addWidget(self.figure_add)
        self.helper_figure_title.setLayout(self.figure_title_row)
        # figures scrollable box
        self.helper_figure_box = QWidget()
        self.helper_figure_box.setStyleSheet(std_border_style)
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
        self.helper_lights_title.setStyleSheet(std_border_style)
        self.lights_title_row = QHBoxLayout()
        self.lights_label = QLabel("Lights ", self)
        self.lights_label.setStyleSheet("border: none;")
        self.lights_add = QPushButton("+")
        self.lights_add.setStyleSheet(pressed_button_style)
        self.lights_add.clicked.connect(self.add_light)
        self.lights_title_row.addWidget(self.lights_label)
        self.lights_title_row.addWidget(self.lights_add)
        self.helper_lights_title.setLayout(self.lights_title_row)
        # lights scrollable box
        self.helper_lights_box = QWidget()
        self.helper_lights_box.setStyleSheet(std_border_style)
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
        self.camera_controls_group.setStyleSheet(camera_controls_group_style)
        self.camera_controls_layout = QHBoxLayout()

        self.move_camera_button = QPushButton("Move")
        self.move_camera_button.setCheckable(True)
        self.move_camera_button.toggled.connect(
            self.gl_widget.set_camera_interaction_active
        )

        self.reset_camera_button = QPushButton("Reset")
        self.reset_camera_button.clicked.connect(self.reset_camera_view)
        self.reset_camera_button.setStyleSheet(pressed_button_style)

        self.camera_controls_layout.addWidget(self.move_camera_button)
        self.camera_controls_layout.addWidget(self.reset_camera_button)
        self.camera_controls_group.setLayout(self.camera_controls_layout)

        # parameters of an object
        self.helper_parameters_object = QWidget()
        self.helper_parameters_object.setStyleSheet(std_border_style)
        self.parameters_object_area = QVBoxLayout()
        self.param_object_name = QLabel("Object not chosen", self)
        self.parameters_object_area.addWidget(self.param_object_name)
        self.helper_parameters_object.setLayout(self.parameters_object_area)
        # parameters of a frame
        self.helper_parameters_frame = QWidget()
        self.helper_parameters_frame.setStyleSheet(std_border_style)
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
        self.helper_animation_header.setStyleSheet(std_border_style)
        self.helper_animation_frames = QWidget()
        self.helper_animation_frames.setStyleSheet(std_border_style)
        self.animation_header_layout = QHBoxLayout()
        self.animation_frames_layout = QHBoxLayout()

        # header
        self.animation_label = QLabel("Animation")
        self.add_frame_btn = QPushButton("+")
        self.add_frame_btn.setStyleSheet(pressed_button_style)
        self.add_frame_btn.clicked.connect(self.add_frame)
        self.delete_frame_btn = QPushButton("X")
        self.delete_frame_btn.clicked.connect(self.delete_frame)
        self.delete_frame_btn.setStyleSheet(pressed_button_style)
        self.frame_number = QLabel("Frame #")
        self.download = QPushButton("Download film")
        self.download.clicked.connect(self.generate_animation_movie)
        self.download.setStyleSheet(pressed_button_style)
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

        self.frame_buttons = []
        for i in range(100):
            btn = QPushButton(f"{i+1}")
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked=False, n=i + 1: self.frame_chosen(n))
            self.animation_frames_layout_internal.addWidget(btn)
            self.frame_buttons.append(btn)
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
        self.add_light()
        self.resize(1200, 800)

    def set_chosen_figure(self, figure_item):
        if self.chosen_figure_item and self.chosen_figure_item != figure_item:
            self.chosen_figure_item.name_button.setStyleSheet("")  # reset stylu
            self.chosen_figure_item.is_selected = False

        self.chosen_figure_item = figure_item
        figure_item.is_selected = True
        figure_item.name_button.setStyleSheet("background-color: lightblue;")

        figure_item.display_figure_params()

    def delete_frame(self):
        chosen_frame_number = self.get_chosen_frame()
        if chosen_frame_number == -1:
            return
        if (
            chosen_frame_number in self.frame_numbers
        ):  # we do nothing if this frame is empty
            for i in range(self.figure_box.count()):
                figure = self.figure_box.itemAt(i)
                figure_widget = figure.widget()
                if isinstance(figure_widget, FigureItem):
                    figure_widget.params_in_frames.pop(chosen_frame_number)
            # TODO usuwanie klatki ze słowników obiektów świateł
            self.frame_numbers.remove(chosen_frame_number)
            button = self.animation_frames_layout_internal.itemAt(
                chosen_frame_number - 1
            ).widget()
            button.setStyleSheet("background-color: none;")

    def add_frame(self):
        chosen_frame_number = self.get_chosen_frame()
        if (
            chosen_frame_number != -1 and chosen_frame_number not in self.frame_numbers
        ):  # we do nothing if there is already frame inside
            self.frame_numbers.append(chosen_frame_number)
            self.frame_numbers.sort()
            for i in range(self.figure_box.count()):
                figure = self.figure_box.itemAt(i)
                figure_widget = figure.widget()
                if isinstance(figure_widget, FigureItem):
                    params = figure_widget.get_params_for_ui_display(
                        chosen_frame_number
                    )
                    set_frame_to_figure(figure_widget, chosen_frame_number, params)
            # TODO dodawanie klatki do słowników obiektów świateł
            # pokoloruj klatkę jeśli jest pełna
            button = self.animation_frames_layout_internal.itemAt(
                chosen_frame_number - 1
            ).widget()
            button.setStyleSheet("background-color: lightblue; border: 4px solid red;")

    def frame_chosen(self, number):
        self.chosen_frame_number = number
        self.frame_number.setText(f"Frame #{number}")

        for i, btn in enumerate(self.frame_buttons):
            is_keyframe_for_animation = (i + 1) in self.frame_numbers
            if (i + 1) == number and is_keyframe_for_animation:
                btn.setStyleSheet("background-color: lightblue; border: 4px solid red;")
            elif (i + 1) == number:
                btn.setStyleSheet("border: 4px solid red;")
            elif is_keyframe_for_animation:
                btn.setStyleSheet("background-color: lightblue;")
            else:
                btn.setStyleSheet("")

        print(f"CHOSEN FRAME: {number}")

        for i in range(self.figure_box.count()):
            figure_widget_item = self.figure_box.itemAt(i).widget()
            if isinstance(figure_widget_item, FigureItem):
                figure_widget_item.update_visual_state(number)

        self.gl_widget.update()

        if self.chosen_figure_item:
            print(f"AKTYWNA FIGURA: {self.chosen_figure_item.name}")
            self.chosen_figure_item.display_figure_params()
        else:
            print("Nie znaleziono zaznaczonej figury.")

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
            figure_item = FigureItem(
                file_name,
                self.gl_widget,
                index,
                self.figure_box,
                self,
                centroid,
                vertices_np,
            )
            for frame in self.frame_numbers:
                set_frame_to_figure(figure_item, frame)
            self.figure_box.addWidget(figure_item)

        except Exception as e:
            QMessageBox.critical(
                self, "Błąd", f"Nie udało się wczytać modelu:\n{str(e)}"
            )
    
    def add_light(self):
        if len(self.gl_widget.lights) >= 8:
            QMessageBox.warning(
                self, "Ostrzeżenie", "Maksymalna liczba świateł to 8."
            )
            return
        index = len(self.gl_widget.lights)
        light = {
            "position": QVector3D(5, 5, 5), 
            "ambient": QVector3D(0.25, 0.25, 0.25), 
            "diffuse": QVector3D(0.75, 0.75, 0.75), 
            "specular": QVector3D(1.0, 1.0, 1.0)
        }

        light_item = LightItem("light_"+str(self.lights_ever), light, self.gl_widget, index, self.lights_box, self)
        self.lights_ever += 1
        self.lights_box.addWidget(light_item)
        self.gl_widget.add_light(light)

    def get_chosen_frame(self):
        chosen_frame_text = self.frame_number.text()
        find_hash = chosen_frame_text.find("#")
        chosen_frame_number_str = chosen_frame_text[find_hash + 1 :]
        if chosen_frame_number_str != "":
            chosen_frame_number = int(chosen_frame_number_str)
            return chosen_frame_number
        return -1

    def on_button_click(self):
        self.gl_widget.change_background_color(0.2, 0.0, 0.5)

    def generate_animation_movie(self):
        if len(self.frame_numbers) < 2:
            QMessageBox.warning(
                self, "Animation Error", "Define at least 2 key frames."
            )
            return

        fps, ok = QInputDialog.getInt(
            self, "FPS Animation", "Define frames per second (FPS):", 30, 1, 120
        )
        if not ok:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save video", "", "WebM Files (*.webm);"
        )
        if not path:
            return
        if not path.endswith(".webm"):
            path += ".webm"

        min_frame = self.frame_numbers[0]
        max_frame = self.frame_numbers[-1]

        current_ui_frame_to_restore = self.get_chosen_frame()

        try:
            with iio.get_writer(path, fps=fps, codec='vp9', macro_block_size=None) as writer:
                for frame_num in range(min_frame, max_frame + 1):
                    for i in range(self.figure_box.count()):
                        figure = self.figure_box.itemAt(i).widget()
                        if isinstance(figure, FigureItem):
                            params = figure.get_interpolated_params(frame_num)

                            temp_vertices = figure.original_vertices.copy()
                            figure.apply_scale(
                                params["size_x"],
                                params["size_y"],
                                params["size_z"],
                                temp_vertices,
                            )
                            figure.apply_rotation(
                                params["rot_x"],
                                params["rot_y"],
                                params["rot_z"],
                                temp_vertices,
                            )
                            figure.apply_location(params["centroid"], temp_vertices)

                            self.gl_widget.updateModelVertices(
                                figure.index, temp_vertices
                            )

                    self.gl_widget.update()
                    QApplication.processEvents()
                    frame_image = self.gl_widget.grabFramebuffer()
                    writer.append_data(qimage_to_numpy(frame_image))  # pyright: ignore

            QMessageBox.information(self, "Success", f"Video saved to: {path}")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error occured while generating video: {e}"
            )
        finally:
            self.frame_chosen(current_ui_frame_to_restore)


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
    if len(params) == 0:
        figure_widget.params_in_frames[chosen_frame_number] = {
            "centroid": figure_widget.centroid,
            "size_x": figure_widget.size_x,
            "size_y": figure_widget.size_y,
            "size_z": figure_widget.size_z,
            "rot_x": 0,
            "rot_y": 0,
            "rot_z": 0,
        }
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




def qimage_to_numpy(qimage: QImage):
    if qimage.format() != QImage.Format_RGBA8888:
        qimage = qimage.convertToFormat(QImage.Format_RGBA8888)

    width = qimage.width()
    height = qimage.height()

    ptr = qimage.bits()
    ptr.setsize(height * width * 4)  # 4 kanały: RGBA
    arr = np.array(ptr, dtype=np.uint8).reshape((height, width, 4))
    return arr


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
