import sys
import numpy as np
import yfinance as yf
import pandas as pd
from scipy.optimize import minimize_scalar
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QPlainTextEdit, QSizePolicy, QToolButton, QGridLayout, QTextEdit, QTableWidgetItem, QSlider
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QHoverEvent
from PySide6.QtCore import Qt, QSize, QEvent
from src.provider import *
import warnings, platform
import qdarktheme
warnings.simplefilter(action='ignore', category=FutureWarning)

font_name = "Consolas"

def get_push_button(text, funct, font_size):
	button = QPushButton(text)
	font = QFont(font_name, font_size)
	font.setStyleHint(QFont.Monospace)
	font.setPointSize(font_size)
	button.setFont(font)
	button.setStyleSheet("QPushButton { background-color: #333333; \
		                  color: #ffffff; } \
		                  QPushButton::pressed \
		                  { background-color: light-blue }; \
		                  padding: 8px; border-radius: 10px;")
	button.setIconSize(QSize(24, 24))
	button.clicked.connect(funct)
	return button

def get_text_entry_box(label, font_size, bold=False, readOnly=False):
	layout = QHBoxLayout()
	field_text = QLabel(label)
	font = QFont(font_name, font_size)
	font.setStyleHint(QFont.Monospace)
	font.setPointSize(font_size)
	field_text.setFont(font)
	if bold: field_text.setStyleSheet("font-weight: bold")
	field_entry = QLineEdit()
	field_entry.setFont(font)
	if bold: field_entry.setStyleSheet("font-weight: bold")
	if readOnly: field_entry.setReadOnly(True)
	layout.addWidget(field_text, alignment=Qt.AlignRight)
	layout.addWidget(field_entry, alignment=Qt.AlignLeft)
	return field_entry, layout

def get_dark_mode_toggle_button(funct):
	theme_layout = QGridLayout()
	button = get_push_button("Turn Dark Mode OFF", funct, 10)
	theme_layout.addWidget(button, 0, 0)
	theme_layout.addWidget(QLabel("\t"), 0, 1)
	theme_layout.addWidget(QLabel("\t"), 0, 2)
	theme_layout.addWidget(QLabel("\t"), 0, 3)
	return button, theme_layout

def get_information_layout(font_size):
	info_layout = QVBoxLayout()
	info_text = QTextEdit()
	font = QFont(font_name, font_size)
	font.setStyleHint(QFont.Monospace)
	font.setPointSize(font_size)
	info_text.setFont(font)
	info_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
	info_text.setReadOnly(True)
	info_layout.addWidget(info_text, alignment=Qt.AlignBottom)
	return info_text, info_layout

def get_central_buttons(funct_reset, funct_calc, funct_populate, font_size):
	layout = QHBoxLayout()
	reset_button = get_push_button("Reset", funct_reset, font_size)
	calc_button = get_push_button("Calculate Fair Value", funct_calc, font_size)
	populate_button = get_push_button("Populate Info", funct_populate, font_size)
	layout.addWidget(reset_button)
	layout.addWidget(calc_button)
	layout.addWidget(populate_button)
	return reset_button, calc_button, populate_button, layout

def get_label(text, font_size, bold=False):
	label  = QLabel(text)
	font = QFont(font_name, font_size)
	font.setStyleHint(QFont.Monospace)
	font.setPointSize(font_size)
	label.setFont(font)
	if bold: label.setStyleSheet("font-weight: bold")
	label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
	return label