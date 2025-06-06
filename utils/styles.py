pressed_button_style = """
QPushButton:pressed {
	background-color: #3e8e41; /* Kolor tła po wciśnięciu */
	border-style: inset; /* Efekt "wciśnięcia" ramki */
	padding: 9px 15px 7px 17px; /* Lekkie przesunięcie tekstu/paddingu dla efektu wciśnięcia */
}
"""

std_border_style = "border: 2px solid black;"

camera_controls_group_style = """
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
