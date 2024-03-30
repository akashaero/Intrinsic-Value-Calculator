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

syntax of usage:
$ python get_fair_value.py <ticker> <rev_growth_rate> <fcf_margin> -N <n_future years> -rrr <required rate of return> -tgr <terminal growth rate>

Only ticker, revenue growth rate, and fcf margin are required arguments, 
rest are optional with default values assumed. Ticker name is NOT case sensitive
-N         = 7             Number of Years for Analysis
-rrr       = 10            Required Rate of Return (%)
-tgr       = 2.5           Terminal Growth Rate (%)

To silent the terminal output (especially in batch mode), use -S flag

examples of usage:
$ python get_fair_value.py intc 12.2 20
or
$ python get_fair_value.py INTC 12.2 20.0 --N 7 --rrr 10 --tgr 2.5
or
$ python get_fair_value.py INTC 12.2 20 --N 7 --rrr 10 --tgr 2.5 -S
'''

import sys
import numpy as np
import yfinance as yf
from scipy.optimize import minimize_scalar
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QPlainTextEdit, QSizePolicy
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from PySide6.QtCore import Qt, QSize
from provider import *

class DCFApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intrinsic Value Calculator")
        self.setStyleSheet("background-color: #000000; color: #ffffff;")
        self.setMinimumSize(800, 600)

        # Load custom font
        QFontDatabase.addApplicationFont("path/to/your/font.ttf")
        self.font = QFont("Your Font", 12)

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
        input_layout = QVBoxLayout()

        # Ticker input
        ticker_layout = QHBoxLayout()
        ticker_label = QLabel("Ticker:")
        ticker_label.setFont(self.font)
        self.ticker_entry = QLineEdit()
        self.ticker_entry.setFont(self.font)
        ticker_layout.addWidget(ticker_label, alignment=Qt.AlignLeft)
        ticker_layout.addWidget(self.ticker_entry, alignment=Qt.AlignLeft)

        # Revenue growth rate input
        rev_growth_layout = QHBoxLayout()
        rev_growth_label = QLabel("Revenue Growth Rate (%):")
        rev_growth_label.setFont(self.font)
        self.rev_growth_entry = QLineEdit()
        self.rev_growth_entry.setFont(self.font)
        rev_growth_layout.addWidget(rev_growth_label, alignment=Qt.AlignLeft)
        rev_growth_layout.addWidget(self.rev_growth_entry, alignment=Qt.AlignLeft)

        # FCF margin input
        fcf_margin_layout = QHBoxLayout()
        fcf_margin_label = QLabel("FCF Margin (%):")
        fcf_margin_label.setFont(self.font)
        self.fcf_margin_entry = QLineEdit()
        self.fcf_margin_entry.setFont(self.font)
        fcf_margin_layout.addWidget(fcf_margin_label, alignment=Qt.AlignLeft)
        fcf_margin_layout.addWidget(self.fcf_margin_entry, alignment=Qt.AlignLeft)

        # Buttons
        button_layout = QHBoxLayout()
        calculate_button = QPushButton("Calculate")
        calculate_button.setFont(self.font)
        calculate_button.setStyleSheet("background-color: #333333; color: #ffffff; padding: 10px; border-radius: 5px;")
        calculate_button.setIconSize(QSize(24, 24))
        calculate_button.setIcon(QIcon("path/to/calculate_icon.png"))
        calculate_button.clicked.connect(self.calculate_dcf)
        reset_button = QPushButton("Reset")
        reset_button.setFont(self.font)
        reset_button.setStyleSheet("background-color: #333333; color: #ffffff; padding: 10px; border-radius: 5px;")
        reset_button.setIconSize(QSize(24, 24))
        reset_button.setIcon(QIcon("path/to/reset_icon.png"))
        reset_button.clicked.connect(self.reset_fields)
        button_layout.addWidget(reset_button)
        button_layout.addWidget(calculate_button)
        

        input_layout.addLayout(ticker_layout)
        input_layout.addLayout(rev_growth_layout)
        input_layout.addLayout(fcf_margin_layout)
        input_layout.addLayout(button_layout)

        self.input_frame.setLayout(input_layout)

    def create_output_frame(self):
        output_layout = QVBoxLayout()

        self.output_text = QPlainTextEdit()
        self.output_text.setFont(self.font)
        self.output_text.setStyleSheet("background-color: #333333; color: #ffffff;")
        self.output_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        output_layout.addWidget(self.output_text)

        self.output_frame.setLayout(output_layout)

    def calculate_dcf(self):
        ticker = self.ticker_entry.text().upper()
        rev_growth_rate = float(self.rev_growth_entry.text()) / 100
        fcf_margin = float(self.fcf_margin_entry.text()) / 100

        try:
            current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin = get_info(ticker)
            results = dcf(rev_growth_rate, fcf_margin, 7, starting_rev, 0.1, 0.025, total_shares, current_price)
            output = get_calculated_info(results, current_price, round(100 * fcf_margin, 2),
                                          round(100 * prev_rev_growth, 2), round(100 * prev_fcf_margin, 2), ticker,
                                          2.5, 10.0, 7)
            self.output_text.setPlainText(output)
        except Exception as e:
            self.output_text.setPlainText(f"Error: {e}")

    def reset_fields(self):
        self.ticker_entry.clear()
        self.rev_growth_entry.clear()
        self.fcf_margin_entry.clear()
        self.output_text.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dcf_app = DCFApp()
    dcf_app.show()
    sys.exit(app.exec())