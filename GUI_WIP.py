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
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QPlainTextEdit, QSizePolicy, QToolButton, QGridLayout, QTextEdit, QTableWidgetItem
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QHoverEvent
from PySide6.QtCore import Qt, QSize, QEvent
from provider import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class DCFApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intrinsic Value Calculator")
        # self.setStyleSheet("background-color: #000000; color: #ffffff;")
        self.setMinimumSize(900, 800)

        # Load font
        self.font = QFont("Courier New", 14)

        # Create widgets
        self.input_frame = QWidget()
        self.output_frame = QWidget()

        self.create_input_frame()
        self.create_output_frame()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.input_frame)
        main_layout.addWidget(self.output_frame)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_input_frame(self):
        final_layout = QVBoxLayout()
        prefinal_layout = QVBoxLayout() 
        upper_layout = QGridLayout()
        
        # Ticker input
        ticker_layout = QHBoxLayout()
        ticker_label = QLabel("Ticker:    ")
        ticker_label.setFont(self.font)
        self.ticker_entry = QLineEdit()
        self.ticker_entry.setFont(self.font)
        ticker_layout.addWidget(ticker_label, alignment=Qt.AlignRight)
        ticker_layout.addWidget(self.ticker_entry, alignment=Qt.AlignLeft)

        # Revenue growth rate input
        rev_growth_layout = QHBoxLayout()
        rev_growth_label = QLabel("Revenue Growth Rate (%):    ")
        rev_growth_label.setFont(self.font)
        self.rev_growth_entry = QLineEdit()
        self.rev_growth_entry.setFont(self.font)
        rev_growth_layout.addWidget(rev_growth_label, alignment=Qt.AlignRight)
        rev_growth_layout.addWidget(self.rev_growth_entry, alignment=Qt.AlignLeft)

        # FCF margin input
        fcf_margin_layout = QHBoxLayout()
        fcf_margin_label = QLabel("Free Cash Flow (FCF) Margin (%):    ")
        fcf_margin_label.setFont(self.font)
        self.fcf_margin_entry = QLineEdit()
        self.fcf_margin_entry.setFont(self.font)
        fcf_margin_layout.addWidget(fcf_margin_label, alignment=Qt.AlignRight)
        fcf_margin_layout.addWidget(self.fcf_margin_entry, alignment=Qt.AlignLeft)

        # Number of years input
        nyears_layout = QHBoxLayout()
        nyears_label = QLabel("Number of Years:    ")
        nyears_label.setFont(self.font)
        self.nyears_entry = QLineEdit()
        self.nyears_entry.setFont(self.font)
        self.nyears_entry.setText("7")
        nyears_layout.addWidget(nyears_label, alignment=Qt.AlignRight)
        nyears_layout.addWidget(self.nyears_entry, alignment=Qt.AlignLeft)

        # WACC input
        wacc_layout = QHBoxLayout()
        wacc_label = QLabel("Discount Rate / WACC (%):    ")
        wacc_label.setFont(self.font)
        self.wacc_entry = QLineEdit()
        self.wacc_entry.setFont(self.font)
        self.wacc_entry.setText("10")
        wacc_layout.addWidget(wacc_label, alignment=Qt.AlignRight)
        wacc_layout.addWidget(self.wacc_entry, alignment=Qt.AlignLeft)

        # Terminal growth rate input
        tgr_layout = QHBoxLayout()
        tgr_label = QLabel("Terminal Growth Rate (%):    ")
        tgr_label.setFont(self.font)
        self.tgr_entry = QLineEdit()
        self.tgr_entry.setFont(self.font)
        self.tgr_entry.setText("2.5")
        tgr_layout.addWidget(tgr_label, alignment=Qt.AlignRight)
        tgr_layout.addWidget(self.tgr_entry, alignment=Qt.AlignLeft)

        # Information Layout
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setFont(QFont("Courier New", 16))
        # self.info_text.setStyleSheet("background-color: #333333; color: #ffffff;")
        self.info_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text, alignment=Qt.AlignBottom)

        # Buttons
        button_layout = QHBoxLayout()
        calculate_button = QPushButton("Calculate Fair Value")
        calculate_button.setFont(self.font)
        calculate_button.setStyleSheet("background-color: #333333; color: #ffffff; padding: 10px; border-radius: 5px;")
        calculate_button.setIconSize(QSize(24, 24))
        calculate_button.clicked.connect(self.calculate_dcf)
        
        reset_button = QPushButton("Reset")
        reset_button.setFont(self.font)
        reset_button.setStyleSheet("background-color: #333333; color: #ffffff; padding: 10px; border-radius: 5px;")
        reset_button.setIconSize(QSize(24, 24))
        reset_button.clicked.connect(self.reset_fields)

        populate_button = QPushButton("Populate Info")
        populate_button.setFont(self.font)
        populate_button.setStyleSheet("background-color: #333333; color: #ffffff; padding: 10px; border-radius: 5px;")
        populate_button.setIconSize(QSize(24, 24))
        populate_button.clicked.connect(self.populate_info)

        button_layout.addWidget(reset_button)
        button_layout.addWidget(calculate_button)
        button_layout.addWidget(populate_button)

        # Start Arranging Layouts in Input Frame
        upper_layout.addLayout(ticker_layout, 0, 0)
        upper_layout.addLayout(rev_growth_layout, 1, 0)
        upper_layout.addLayout(fcf_margin_layout, 2, 0)
        upper_layout.addLayout(nyears_layout, 3, 0)
        upper_layout.addLayout(wacc_layout, 4, 0)
        upper_layout.addLayout(tgr_layout, 5, 0)

        prefinal_layout.addLayout(upper_layout)
        prefinal_layout.addLayout(info_layout)

        final_layout.addLayout(prefinal_layout)
        final_layout.addLayout(button_layout)

        self.input_frame.setLayout(final_layout)

    def create_output_frame(self):
        output_layout = QGridLayout()
        
        # Fair Value Output Box
        fv_layout = QHBoxLayout()
        fv_label = QLabel("Fair Value:    ")
        fv_label.setFont(self.font)
        self.fv_entry = QLineEdit()
        self.fv_entry.setFont(self.font)
        self.fv_entry.setReadOnly(True)
        fv_layout.addWidget(fv_label, alignment=Qt.AlignRight)
        fv_layout.addWidget(self.fv_entry, alignment=Qt.AlignLeft)

        # Current Price Output Box
        cp_layout = QHBoxLayout()
        cp_label = QLabel("Current Price:    ")
        cp_label.setFont(self.font)
        self.cp_entry = QLineEdit()
        self.cp_entry.setFont(self.font)
        self.cp_entry.setReadOnly(True)
        cp_layout.addWidget(cp_label, alignment=Qt.AlignRight)
        cp_layout.addWidget(self.cp_entry, alignment=Qt.AlignLeft)
        
        # Upside/Downside Output Box
        ud_layout = QHBoxLayout()
        ud_label = QLabel("Upside/Downside (%):    ")
        ud_label.setFont(self.font)
        self.ud_entry = QLineEdit()
        self.ud_entry.setFont(self.font)
        self.ud_entry.setReadOnly(True)
        ud_layout.addWidget(ud_label, alignment=Qt.AlignRight)
        ud_layout.addWidget(self.ud_entry, alignment=Qt.AlignLeft)

        rev_dcf_layout = QVBoxLayout()
        self.rev_dcf_start = QLabel("\nTo Justify the Current Price")
        self.rev_dcf_start.setFont(self.font)
        self.rev_dcf_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        rrev_layout = QHBoxLayout()
        self.rev_revenue = QLabel("Required Revenue Growth at Current FCF Margin (%):     ")
        self.rev_revenue.setFont(self.font)
        self.rrev_entry = QLineEdit()
        self.rrev_entry.setFont(self.font)
        self.rrev_entry.setReadOnly(True)
        self.rev_revenue.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        rrev_layout.addWidget(self.rev_revenue, alignment=Qt.AlignLeft)
        rrev_layout.addWidget(self.rrev_entry, alignment=Qt.AlignRight)

        self.sep1 = QLabel(" Or ")
        self.sep1.setFont(self.font)

        rfcf_layout = QHBoxLayout()
        self.rev_fcf = QLabel("Required Free Cash Flow Margin at Current Revenue Growth (%):     ")
        self.rev_fcf.setFont(self.font)
        self.rfcf_entry = QLineEdit()
        self.rfcf_entry.setFont(self.font)
        self.rfcf_entry.setReadOnly(True)
        self.rev_fcf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        rfcf_layout.addWidget(self.rev_fcf, alignment=Qt.AlignLeft)
        rfcf_layout.addWidget(self.rfcf_entry, alignment=Qt.AlignRight)

        self.sep2 = QLabel(" Or ")
        self.sep2.setFont(self.font)

        rwacc_layout = QHBoxLayout()
        self.rev_wacc = QLabel("Obtained Compounded Return Rate for Selected Number of Years (%):     ")
        self.rev_wacc.setFont(self.font)
        self.rwacc_entry = QLineEdit()
        self.rwacc_entry.setFont(self.font)
        self.rwacc_entry.setReadOnly(True)
        self.rev_wacc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        rwacc_layout.addWidget(self.rev_wacc, alignment=Qt.AlignLeft)
        rwacc_layout.addWidget(self.rwacc_entry, alignment=Qt.AlignRight)

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

        self.output_frame.setLayout(output_layout)

    def populate_info(self):
        self.info_text.clear()
        _, _, _, _, _, info_str = get_info(self.ticker_entry.text().upper())
        lines = info_str.splitlines()
        lines[-1] = lines[-1] + '\t'
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
            lines[-1] = lines[-1] + '\t'
            for line in lines:
                self.info_text.append(line)
                self.info_text.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
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