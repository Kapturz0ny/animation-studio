import math
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
)
from PyQt5.QtGui import QVector3D
from utils.styles import pressed_button_style


class LightItem(QWidget):
    def __init__(self, name, light, gl_widget, index, parent_layout, main_window):
        super().__init__()
        self.name = name
        self.gl_widget = gl_widget
        self.parent_layout = parent_layout
        self.main_window = main_window
        self.index = index
        self.light = light

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
        self.gl_widget.lights[self.index]["visible"] = current_state
        self.update_icon()
        self.gl_widget.update()

    def on_name_button_clicked(self):
        self.display_figure_params()
        # self.main_window.set_chosen_figure(self)
    
    def update_icon(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setText("✖")  # figure visible
        else:
            self.toggle_button.setText("")  # figure invisible

    def fill_params_for_frame_1(self):
        self.params_in_frames[1] = {
            'position': self.light['position'],
            'ambient': self.light['ambient'],
            'diffuse': self.light['diffuse'],
            'specular': self.light['specular']
        }

    def delete_self(self):
        try:
            index = self.parent_layout.indexOf(self)
            if index != -1:
                self.gl_widget.delete_light(index)
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
        section_layout = self.main_window.parameters_frame_area
        clear_layout(section_layout)

        chosen_frame_number = self.main_window.get_chosen_frame()
        if chosen_frame_number == -1:
            chosen_frame_number = 1  # jeśli nic nie wybrano, ustawiamy frame 1


        self.main_window.param_frame_number.setText(f"Parameters for {self.name} in frame #{chosen_frame_number}")


        if 1 not in self.params_in_frames or not self.params_in_frames[1]:
            self.fill_params_for_frame_1()

        # Jeśli brak parametrów dla wybranego frame, użyj frame 1 jako domyślnych
        if chosen_frame_number not in self.params_in_frames or not self.params_in_frames[chosen_frame_number]:
            current_params = self.params_in_frames.get(1, {})
        else:
            current_params = self.params_in_frames[chosen_frame_number]

        # position = current_params.get("position", (0.0, 0.0, 0.0))
        # ambient = current_params.get("ambient", (0.25, 0.25, 0.25))
        # diffuse = current_params.get("diffuse", (0.75, 0.75, 0.75))
        # specular = current_params.get("specular", (1.0, 1.0, 1.0))
        position = self.light.get("position", QVector3D(0.0, 0.0, 0.0))
        ambient = self.light.get("ambient", QVector3D(0.25, 0.25, 0.25))
        diffuse = self.light.get("diffuse", QVector3D(0.75, 0.75, 0.75))
        specular = self.light.get("specular", QVector3D(1.0, 1.0, 1.0))

        # Position
        self.position_title = QLabel("Position")
        self.position_box = QHBoxLayout()
        self.pos_x_text = QLineEdit(str(position[0]))
        self.pos_y_text = QLineEdit(str(position[1]))
        self.pos_z_text = QLineEdit(str(position[2]))
        self.position_box.addWidget(QLabel("x:"))
        self.position_box.addWidget(self.pos_x_text)
        self.position_box.addWidget(QLabel("y:"))
        self.position_box.addWidget(self.pos_y_text)
        self.position_box.addWidget(QLabel("z:"))
        self.position_box.addWidget(self.pos_z_text)
        # Ambient
        self.ambient_title = QLabel("Ambient (RGB)")
        self.ambient_box = QHBoxLayout()
        self.amb_r_text = QLineEdit(str(ambient[0]))
        self.amb_g_text = QLineEdit(str(ambient[1]))
        self.amb_b_text = QLineEdit(str(ambient[2]))
        self.ambient_box.addWidget(QLabel("R:"))
        self.ambient_box.addWidget(self.amb_r_text)
        self.ambient_box.addWidget(QLabel("G:"))
        self.ambient_box.addWidget(self.amb_g_text)
        self.ambient_box.addWidget(QLabel("B:"))
        self.ambient_box.addWidget(self.amb_b_text)
        # Diffuse
        self.diffuse_title = QLabel("Diffuse (RGB)")
        self.diffuse_box = QHBoxLayout()
        self.diff_r_text = QLineEdit(str(diffuse[0]))
        self.diff_g_text = QLineEdit(str(diffuse[1]))
        self.diff_b_text = QLineEdit(str(diffuse[2]))
        self.diffuse_box.addWidget(QLabel("R:"))
        self.diffuse_box.addWidget(self.diff_r_text)
        self.diffuse_box.addWidget(QLabel("G:"))
        self.diffuse_box.addWidget(self.diff_g_text)
        self.diffuse_box.addWidget(QLabel("B:"))
        self.diffuse_box.addWidget(self.diff_b_text)
        # Specular
        self.specular_title = QLabel("Specular (RGB)")
        self.specular_box = QHBoxLayout()
        self.spec_r_text = QLineEdit(str(specular[0]))
        self.spec_g_text = QLineEdit(str(specular[1]))
        self.spec_b_text = QLineEdit(str(specular[2]))
        self.specular_box.addWidget(QLabel("R:"))
        self.specular_box.addWidget(self.spec_r_text)
        self.specular_box.addWidget(QLabel("G:"))
        self.specular_box.addWidget(self.spec_g_text)
        self.specular_box.addWidget(QLabel("B:"))
        self.specular_box.addWidget(self.spec_b_text)
        # Apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_light_params)
        # Add to layout
        section_layout.addWidget(self.position_title)
        section_layout.addLayout(self.position_box)
        section_layout.addWidget(self.ambient_title)
        section_layout.addLayout(self.ambient_box)
        section_layout.addWidget(self.diffuse_title)
        section_layout.addLayout(self.diffuse_box)
        section_layout.addWidget(self.specular_title)
        section_layout.addLayout(self.specular_box)
        section_layout.addWidget(self.apply_btn)

    def apply_light_params(self):
        self.light["position"] = QVector3D(
            float(self.pos_x_text.text()),
            float(self.pos_y_text.text()),
            float(self.pos_z_text.text())
        )
        self.light["ambient"] = QVector3D(
            float(self.amb_r_text.text()),
            float(self.amb_g_text.text()),
            float(self.amb_b_text.text())
        )
        self.light["diffuse"] = QVector3D(
            float(self.diff_r_text.text()),
            float(self.diff_g_text.text()),
            float(self.diff_b_text.text())
        )
        self.light["specular"] = QVector3D(
            float(self.spec_r_text.text()),
            float(self.spec_g_text.text()),
            float(self.spec_b_text.text())
        )
        # Update the light in the OpenGL widget
        self.gl_widget.lights[self.index] = self.light
        self.gl_widget.update()

class FigureItem(QWidget):
    def __init__(
        self, name, gl_widget, index, parent_layout, main_window, centroid, vertices_np
    ):
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
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0
        self.diffuse = [0.0, 0.0, 0.0, 0.0]  # rozproszone odbicie swiatla
        self.specular = [0.0, 0.0, 0.0, 0.0]  # odbicie zwierciadlane

        self.original_vertices = vertices_np
        self.current_vertices = vertices_np.copy()

        self.params_in_frames = {}

        layout = QHBoxLayout()
        self.name_button = QPushButton(name)
        self.name_button.clicked.connect(self.on_name_button_clicked)
        self.name_button.setStyleSheet(pressed_button_style)

        self.toggle_button = QPushButton("✖")
        self.toggle_button.setStyleSheet(pressed_button_style)
        self.toggle_button.setFixedSize(24, 24)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self.toggle_visibility)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(
            "background-color: lightgray; color: black; padding: 0px; margin: 0px;"
            + pressed_button_style
        )
        self.delete_button.setFixedSize(60, 24)
        self.delete_button.clicked.connect(self.delete_self)

        layout.addWidget(self.name_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.delete_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def get_default_transform_params(self):
        return {
            "centroid": self.centroid,
            "size_x": self.size_x,
            "size_y": self.size_y,
            "size_z": self.size_z,
            "rot_x": self.rot_x,
            "rot_y": self.rot_y,
            "rot_z": self.rot_z,
        }

    def get_interpolated_params(self, frame_num):
        keyframes = sorted(self.params_in_frames.keys())

        if not keyframes:
            return self.get_default_transform_params()

        if frame_num <= keyframes[0]:
            return self.params_in_frames[keyframes[0]]
        if frame_num >= keyframes[-1]:
            return self.params_in_frames[keyframes[-1]]

        prev_kf = keyframes[0]
        next_kf = keyframes[-1]
        for kf in keyframes:
            if kf <= frame_num:
                prev_kf = kf
            if kf >= frame_num:
                next_kf = kf
                break

        if prev_kf == next_kf:
            return self.params_in_frames[prev_kf]

        params1 = self.params_in_frames[prev_kf]
        params2 = self.params_in_frames[next_kf]

        segment_len = float(next_kf - prev_kf)
        t = (frame_num - prev_kf) / segment_len

        interp_p = {
            "centroid": lerp_vec(params1["centroid"], params2["centroid"], t),
            "size_x": lerp(params1["size_x"], params2["size_x"], t),
            "size_y": lerp(params1["size_y"], params2["size_y"], t),
            "size_z": lerp(params1["size_z"], params2["size_z"], t),
            "rot_x": lerp(params1["rot_x"], params2["rot_x"], t),
            "rot_y": lerp(params1["rot_y"], params2["rot_y"], t),
            "rot_z": lerp(params1["rot_z"], params2["rot_z"], t),
        }
        return interp_p

    def get_params_for_ui_display(self, frame_num_in_ui):
        figure_keyframes = sorted(
            [
                k
                for k in self.params_in_frames.keys()
                if self.params_in_frames[k] is not None
            ]
        )

        if not figure_keyframes:
            return self.get_default_transform_params()

        if frame_num_in_ui in self.params_in_frames:
            return self.params_in_frames[frame_num_in_ui]

        if frame_num_in_ui < figure_keyframes[0]:
            return self.params_in_frames[figure_keyframes[0]]

        last_defined_kf_before_or_at_ui_frame = figure_keyframes[0]
        for kf in figure_keyframes:
            if kf <= frame_num_in_ui:
                last_defined_kf_before_or_at_ui_frame = kf
            else:
                break

        return self.params_in_frames[last_defined_kf_before_or_at_ui_frame]

    def toggle_visibility(self):
        current_state = self.toggle_button.isChecked()
        self.gl_widget.additional_visible_flags[self.index] = current_state
        self.update_icon()
        self.gl_widget.update()

    def on_name_button_clicked(self):
        self.display_figure_params()
        self.main_window.set_chosen_figure(self)
        # self.display_frame_figure()

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
        self.main_window.parameters_object_area.addWidget(
            self.main_window.param_object_name
        )
        self.main_window.parameters_frame_area.addWidget(
            self.main_window.param_frame_number
        )
        self.setParent(None)
        self.parent_layout.removeWidget(self)
        self.deleteLater()

    def display_figure_params(self):
        section_layout = self.main_window.parameters_object_area
        clear_layout(section_layout)

        chosen_frame_number = self.main_window.get_chosen_frame()
        if chosen_frame_number == -1:
            chosen_frame_number = 1  # jeśli nic nie wybrano, ustawiamy frame 1

        self.main_window.param_object_name.setText(
            f"Parameters for {self.name} in frame #{chosen_frame_number}"
        )

        params_to_show = self.get_params_for_ui_display(chosen_frame_number)

        # Location
        self.location_title = QLabel("Location")
        self.location_box = QHBoxLayout()
        self.loc_x_text = QLineEdit(str(params_to_show["centroid"][0]))
        self.loc_y_text = QLineEdit(str(params_to_show["centroid"][1]))
        self.loc_z_text = QLineEdit(str(params_to_show["centroid"][2]))
        self.location_box.addWidget(QLabel("x:"))
        self.location_box.addWidget(self.loc_x_text)
        self.location_box.addWidget(QLabel("y:"))
        self.location_box.addWidget(self.loc_y_text)
        self.location_box.addWidget(QLabel("z:"))
        self.location_box.addWidget(self.loc_z_text)

        # Scale
        self.size_title = QLabel("Scale")
        self.size_box = QHBoxLayout()
        self.siz_x_text = QLineEdit(str(params_to_show["size_x"]))
        self.siz_y_text = QLineEdit(str(params_to_show["size_y"]))
        self.siz_z_text = QLineEdit(str(params_to_show["size_z"]))
        self.size_box.addWidget(QLabel("x:"))
        self.size_box.addWidget(self.siz_x_text)
        self.size_box.addWidget(QLabel("y:"))
        self.size_box.addWidget(self.siz_y_text)
        self.size_box.addWidget(QLabel("z:"))
        self.size_box.addWidget(self.siz_z_text)

        # Rotation
        self.rotation_title = QLabel("Rotation")
        self.rotation_box = QHBoxLayout()
        self.rot_x_text = QLineEdit(str(params_to_show["rot_x"]))
        self.rot_y_text = QLineEdit(str(params_to_show["rot_y"]))
        self.rot_z_text = QLineEdit(str(params_to_show["rot_z"]))
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
        self.apply_btn.setStyleSheet(pressed_button_style)

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

    def apply_location(self, centroid, updated_vertices):
        # 1. Oblicz obecny centroid
        x_total, y_total, z_total = 0.0, 0.0, 0.0
        count = 0

        for i in range(0, len(updated_vertices), 6):
            x_total += updated_vertices[i]
            y_total += updated_vertices[i + 1]
            z_total += updated_vertices[i + 2]
            count += 1

        current_centroid = (
            x_total / count,
            y_total / count,
            z_total / count,
        )

        # 2. Oblicz przesunięcie
        delta_x = centroid[0] - current_centroid[0]
        delta_y = centroid[1] - current_centroid[1]
        delta_z = centroid[2] - current_centroid[2]

        # 3. Przesuń wszystkie wierzchołki
        for i in range(0, len(updated_vertices), 6):
            updated_vertices[i] += delta_x  # x
            updated_vertices[i + 1] += delta_y  # y
            updated_vertices[i + 2] += delta_z  # z

    def apply_scale(self, scale_x, scale_y, scale_z, updated_vertices):
        # 1. Oblicz centroid (środek figury)
        x_total, y_total, z_total = 0.0, 0.0, 0.0
        count = 0

        for i in range(0, len(updated_vertices), 6):
            x_total += updated_vertices[i]
            y_total += updated_vertices[i + 1]
            z_total += updated_vertices[i + 2]
            count += 1

        centroid_x = x_total / count
        centroid_y = y_total / count
        centroid_z = z_total / count

        # 2–4. Przesuń -> Skaluj -> Przesuń z powrotem
        for i in range(0, len(updated_vertices), 6):
            # Przesuń do środka
            x = updated_vertices[i] - centroid_x
            y = updated_vertices[i + 1] - centroid_y
            z = updated_vertices[i + 2] - centroid_z

            # Skaluj
            x *= scale_x
            y *= scale_y
            z *= scale_z

            # Przesuń z powrotem
            updated_vertices[i] = x + centroid_x
            updated_vertices[i + 1] = y + centroid_y
            updated_vertices[i + 2] = z + centroid_z

    def apply_rotation(self, rot_x, rot_y, rot_z, updated_vertices):
        # Konwersja stopnie -> radiany
        rx = math.radians(rot_y)
        ry = math.radians(rot_x)
        rz = math.radians(rot_z)

        # 1. Oblicz centroid
        x_total, y_total, z_total = 0.0, 0.0, 0.0
        count = 0

        for i in range(0, len(updated_vertices), 6):
            x_total += updated_vertices[i]
            y_total += updated_vertices[i + 1]
            z_total += updated_vertices[i + 2]
            count += 1

        centroid_x = x_total / count
        centroid_y = y_total / count
        centroid_z = z_total / count

        # 2–4. Obracaj wierzchołki wokół centroidu
        for i in range(0, len(updated_vertices), 6):
            # Przesuń do układu lokalnego (centrum na 0,0,0)
            x = updated_vertices[i] - centroid_x
            y = updated_vertices[i + 1] - centroid_y
            z = updated_vertices[i + 2] - centroid_z

            # Obrót wokół X
            y1 = y * math.cos(rx) - z * math.sin(rx)
            z1 = y * math.sin(rx) + z * math.cos(rx)
            y, z = y1, z1

            # Obrót wokół Y
            x1 = x * math.cos(ry) + z * math.sin(ry)
            z1 = -x * math.sin(ry) + z * math.cos(ry)
            x, z = x1, z1

            # Obrót wokół Z
            x1 = x * math.cos(rz) - y * math.sin(rz)
            y1 = x * math.sin(rz) + y * math.cos(rz)
            x, y = x1, y1

            # Cofnij przesunięcie do globalnego układu
            updated_vertices[i] = x + centroid_x
            updated_vertices[i + 1] = y + centroid_y
            updated_vertices[i + 2] = z + centroid_z

    def apply_figure_params(self):
        # Pobierz aktualny wybrany frame (jeśli brak, użyj 1)
        chosen_frame_number = self.main_window.get_chosen_frame()
        if chosen_frame_number == -1:
            chosen_frame_number = 1  # fallback na frame

        # Upewnij się, że ten frame istnieje
        if chosen_frame_number not in self.params_in_frames:
            QMessageBox.warning(
                self,
                "Update Params Error",
                "Cannot change object params without keyframe selected."
                "Please create a keyframe first.",
            )
            return

        try:
            centroid = (
                float(self.loc_x_text.text()),
                float(self.loc_y_text.text()),
                float(self.loc_z_text.text()),
            )
            self.params_in_frames[chosen_frame_number]["centroid"] = centroid
            size_x = float(self.siz_x_text.text())
            size_y = float(self.siz_y_text.text())
            size_z = float(self.siz_z_text.text())
            rot_x = float(self.rot_x_text.text())
            rot_y = float(self.rot_y_text.text())
            rot_z = float(self.rot_z_text.text())

            self.params_in_frames[chosen_frame_number]["size_x"] = size_x
            self.params_in_frames[chosen_frame_number]["size_y"] = size_y
            self.params_in_frames[chosen_frame_number]["size_z"] = size_z
            self.params_in_frames[chosen_frame_number]["rot_x"] = rot_x
            self.params_in_frames[chosen_frame_number]["rot_y"] = rot_y
            self.params_in_frames[chosen_frame_number]["rot_z"] = rot_z
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

            self.update_visual_state(chosen_frame_number)

        except ValueError:
            print("Błąd: wprowadzone wartości muszą być liczbami")

    def update_visual_state(self, frame_num_to_display_state_of):
        params = self.get_params_for_ui_display(frame_num_to_display_state_of)

        self.current_vertices = self.original_vertices.copy()
        self.apply_scale(
            params["size_x"], params["size_y"], params["size_z"], self.current_vertices
        )
        self.apply_rotation(
            params["rot_x"], params["rot_y"], params["rot_z"], self.current_vertices
        )
        self.apply_location(params["centroid"], self.current_vertices)

        self.gl_widget.updateModelVertices(self.index, self.current_vertices)

    def validate_inputs(self):
        valid = all(
            is_valid_float(edit.text())
            for edit in [
                self.loc_x_text,
                self.loc_y_text,
                self.loc_z_text,
                self.siz_x_text,
                self.siz_y_text,
                self.siz_z_text,
                self.rot_x_text,
                self.rot_y_text,
                self.rot_z_text,
            ]
        )
        self.apply_btn.setEnabled(valid)

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
    
def lerp(v0, v1, t):
    return v0 * (1 - t) + v1 * t

def lerp_vec(v0_tuple, v1_tuple, t):
    if not isinstance(v0_tuple, (list, tuple)) or not isinstance(
        v1_tuple, (list, tuple)
    ):
        return v0_tuple if v0_tuple is not None else v1_tuple
    if len(v0_tuple) != len(v1_tuple):
        return v0_tuple
    return tuple(lerp(c0, c1, t) for c0, c1 in zip(v0_tuple, v1_tuple))
