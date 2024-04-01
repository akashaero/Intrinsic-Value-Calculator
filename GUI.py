'''
Authored by: @akashaero
07/26/2023

Calculates the fair value of a stock using Discounted Free Cash Flow (DCF)
model given, 
  Number of future years to run analysis for (assumed to be 7 years by default)
  Revenue growth rate
  Free cash flow margin
  Required rate of return aka. "Discount Rate" (assumed to be 10% by default).
  Terminal growth rate (assumed to be 2.5% by default)

Also provides reverse DCF functionality where the required revenue growth rate, 
free cash flow margin, and rate of return are calculated based on current stock 
price.
'''

import sys
import numpy as np
import yfinance as yf
import pandas as pd
from scipy.optimize import minimize_scalar
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtWidgets import QPlainTextEdit, QSizePolicy, QToolButton
from PySide6.QtWidgets import QGridLayout, QTextEdit, QTableWidgetItem, QSlider
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QHoverEvent
from PySide6.QtCore import Qt, QSize, QEvent
from src.provider import *
from src.gui_elements import *
import warnings
import qdarktheme
warnings.simplefilter(action='ignore', category=FutureWarning)

class DCFApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intrinsic Value Calculator")
        self.setMinimumSize(700, 800)

        # Activate dark mode by default
        qdarktheme.setup_theme("dark")

        # Set icon
        my_icon = QIcon()
        my_icon.addFile('logo/llama_stocks.jpeg')
        self.setWindowIcon(my_icon)

        # Load font
        self.font_size = 12

        # Create widgets
        self.input_frame = QWidget()
        self.output_frame = QWidget()

        # Create frames
        self.create_input_frame()
        self.create_output_frame()

        # Add frames to main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.input_frame)
        main_layout.addWidget(self.output_frame)

        # Form the final GUI
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_input_frame(self):
        # Toggle Button for Dark Mode
        self.toggle_button, theme_layout = get_dark_mode_toggle_button(self.valuechange)
                
        # Ticker input
        self.ticker_entry, ticker_layout = get_text_entry_box("Ticker:     ", self.font_size)

        # Revenue growth rate input
        self.rev_growth_entry, rev_growth_layout = get_text_entry_box("Revenue Growth Rate (%):    ", self.font_size)

        # FCF margin input
        self.fcf_margin_entry, fcf_margin_layout = get_text_entry_box("Free Cash Flow (FCF) Margin (%):    ", self.font_size)

        # Number of years input with default value
        self.nyears_entry, nyears_layout = get_text_entry_box("Number of Years:    ", self.font_size)
        self.nyears_entry.setText("7")

        # WACC input
        self.wacc_entry, wacc_layout = get_text_entry_box("Discount Rate / WACC (%):    ", self.font_size)
        self.wacc_entry.setText("10")

        # Terminal growth rate input
        self.tgr_entry, tgr_layout = get_text_entry_box("Terminal Growth Rate (%):    ", self.font_size)
        self.tgr_entry.setText("2.5")

        # Information Layout
        self.info_text, info_layout = get_information_layout(self.font_size)

        # Buttons (Reset, Calculate, and Populate Info)
        self.reset_button, self.calculate_button, self.populate_button, button_layout = get_central_buttons(self.reset_fields, \
                                                                                                            self.calculate_dcf, \
                                                                                                            self.populate_info, \
                                                                                                            self.font_size)

        # Layout Framework
        final_layout    = QVBoxLayout()
        prefinal_layout = QVBoxLayout()
        upper_layout    = QGridLayout()

        # Start Arranging Layouts in Input Frame
        upper_layout.addLayout(ticker_layout,     0, 0)
        upper_layout.addLayout(rev_growth_layout, 1, 0)
        upper_layout.addLayout(fcf_margin_layout, 2, 0)
        upper_layout.addLayout(nyears_layout,     3, 0)
        upper_layout.addLayout(wacc_layout,       4, 0)
        upper_layout.addLayout(tgr_layout,        5, 0)

        prefinal_layout.addLayout(theme_layout)
        prefinal_layout.addLayout(upper_layout)
        prefinal_layout.addLayout(info_layout)

        final_layout.addLayout(prefinal_layout)
        final_layout.addLayout(button_layout)

        self.input_frame.setLayout(final_layout)

    def create_output_frame(self):
        output_layout = QGridLayout()
        
        # Main output boxes
        self.fv_entry, fv_layout = get_text_entry_box("Fair Value:    ", int(1.5*self.font_size), bold=True, readOnly=True)
        self.cp_entry, cp_layout = get_text_entry_box("Current Price:    ", self.font_size, bold=True, readOnly=True)
        self.ud_entry, ud_layout = get_text_entry_box("Upside/Downside (%):    ", self.font_size, bold=True, readOnly=True)

        # Start of reverse DCF outputs
        self.rev_dcf_start = get_label("\nTo Justify the Current Price", self.font_size, bold=True)

        # Reverse DCF outputs
        self.rrev_entry, rrev_layout = get_text_entry_box("Required Revenue Growth at Current FCF Margin (%):     ", self.font_size, readOnly=True)
        self.sep1 = get_label(" Or ", self.font_size)
        self.rfcf_entry, rfcf_layout = get_text_entry_box("Required Free Cash Flow Margin at Current Revenue Growth (%):     ", self.font_size, readOnly=True)
        self.sep2 = get_label(" Or ", self.font_size)
        self.rwacc_entry, rwacc_layout = get_text_entry_box("Obtained Compounded Return Rate for Selected Number of Years:     ", self.font_size, readOnly=True)

        # Lay out the output frame
        rev_dcf_layout = QVBoxLayout()
        rev_dcf_layout.addWidget(self.rev_dcf_start, alignment=Qt.AlignCenter)
        rev_dcf_layout.addLayout(rrev_layout)
        rev_dcf_layout.addWidget(self.sep1, alignment=Qt.AlignCenter)
        rev_dcf_layout.addLayout(rfcf_layout)
        rev_dcf_layout.addWidget(self.sep2, alignment=Qt.AlignCenter)
        rev_dcf_layout.addLayout(rwacc_layout)

        output_layout.addLayout(fv_layout, 0, 0)
        output_layout.addLayout(cp_layout, 1, 0)
        output_layout.addLayout(ud_layout, 2, 0)
        output_layout.addLayout(rev_dcf_layout, 3, 0)

        # Finalize output frame
        self.output_frame.setLayout(output_layout)

    def valuechange(self):
        if self.toggle_button.text() == "Turn Dark Mode OFF":
            qdarktheme.setup_theme("light")
            self.toggle_button.setText("Turn Dark Mode ON")
        else:
            qdarktheme.setup_theme("dark")
            self.toggle_button.setText("Turn Dark Mode OFF")

    def populate_info(self):
        self.info_text.clear()
        _, _, _, _, _, info_str = get_info(self.ticker_entry.text().upper())
        lines = info_str.splitlines()
        lines[-1] = lines[-1] + '     '
        for i, line in enumerate(lines):
            self.info_text.append(line)
            self.info_text.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    def calculate_dcf(self):
        ticker = self.ticker_entry.text().upper()
        rev_growth_rate = float(self.rev_growth_entry.text()) / 100
        fcf_margin      = float(self.fcf_margin_entry.text()) / 100
        nyears          = int(self.nyears_entry.text())
        wacc            = float(self.wacc_entry.text()) / 100
        tgr             = float(self.tgr_entry.text()) / 100

        try:
            self.fv_entry.clear()
            self.cp_entry.clear()
            self.ud_entry.clear()
            self.info_text.clear()
            self.rrev_entry.clear()
            self.rfcf_entry.clear()
            self.rwacc_entry.clear()
            current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, info_str = get_info(ticker)
            lines = info_str.splitlines()
            lines[-1] = lines[-1] + '     '
            for line in lines:
                self.info_text.append(line)
                self.info_text.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            results = dcf(rev_growth_rate, fcf_margin, nyears, starting_rev, wacc, tgr, total_shares, current_price)
            fair_value, req_rg, req_wacc, req_fcf, curr_rev_growth = results
            self.fv_entry.setText("$"+str(fair_value))
            self.cp_entry.setText("$"+str(current_price))
            self.ud_entry.setText(str(calc_up_downside(fair_value, current_price))+"%")
            self.rev_dcf_start.setText("\nTo Justify the Current Price of ${}".format(current_price))
            self.rrev_entry.setText(str(req_rg))
            self.rfcf_entry.setText(str(req_fcf))
            self.rwacc_entry.setText(str(req_wacc))
        except Exception as e:
            self.fv_entry.setText(f"Error")

    def reset_fields(self):
        self.ticker_entry.clear()
        self.rev_growth_entry.clear()
        self.fcf_margin_entry.clear()
        self.fv_entry.clear()
        self.cp_entry.clear()
        self.ud_entry.clear()
        self.info_text.clear()
        self.rrev_entry.clear()
        self.rfcf_entry.clear()
        self.rwacc_entry.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dcf_app = DCFApp()
    dcf_app.show()
    sys.exit(app.exec())