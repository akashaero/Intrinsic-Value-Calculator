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

pyinstaller.exe GUI.py --clean --onedir -i logo/icon.ico --noconsole --exclude-module PyQt6 --name Intrinsic-Value-Calculator-OS
'''

import sys
from scipy.optimize import minimize_scalar
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtWidgets import QGridLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
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
        my_icon.addFile('logo/icon.ico')
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
        self.ticker_entry, ticker_label = get_text_entry_box_two("Ticker: ", self.font_size)

        # Revenue growth rate input
        self.rev_growth_entry, rev_growth_label = get_text_entry_box_two("Revenue Growth Rate (%): ", self.font_size)

        # FCF margin input
        self.fcf_margin_entry, fcf_margin_label = get_text_entry_box_two("Free Cash Flow Margin (%): ", self.font_size)

        # Number of years input with default value
        self.nyears_entry, nyears_label = get_text_entry_box_two("Number of Years: ", self.font_size)
        self.nyears_entry.setText("7")

        # WACC input
        self.wacc_entry, wacc_label = get_text_entry_box_two("Discount Rate / WACC (%): ", self.font_size)
        self.wacc_entry.setText("10")

        # Terminal growth rate input
        self.tgr_entry, tgr_label = get_text_entry_box_two("Terminal Growth Rate (%): ", self.font_size)
        self.tgr_entry.setText("2.5")

        # Latest revenue input
        self.curr_rev_entry, cr_label = get_text_entry_box_two("Latest Yearly Revenue: ", self.font_size, readOnly=True)

        # Total shares input
        self.total_shares_entry, tshares_label = get_text_entry_box_two("Total Shares Out: ", self.font_size, readOnly=True)

        # Percentage float input
        self.perc_float_entry, pfloat_label = get_text_entry_box_two("Total Float %: ", self.font_size, readOnly=True)

        # Percentage short input
        self.perc_short_entry, pshort_label = get_text_entry_box_two("Total Short %: ", self.font_size, readOnly=True)

        # Average volume input
        self.avg_vol_entry, avgvol_label = get_text_entry_box_two("Average Volume: ", self.font_size, readOnly=True)

        # Average volume input
        self.mcap_entry, mcap_label = get_text_entry_box_two("Market Cap: ", self.font_size, readOnly=True)

        # Information Layout
        self.info_text, info_layout = get_information_layout(self.font_size)

        # Buttons (Reset, Calculate, and Populate Info)
        self.reset_button, self.calculate_button, self.populate_button, button_layout = get_central_buttons(self.reset_fields, \
                                                                                                            self.calculate_dcf, \
                                                                                                            self.populate_info, \
                                                                                                            self.font_size)

        # Layout Framework
        final_layout       = QVBoxLayout()
        prefinal_layout    = QVBoxLayout()
        upper_left_layout  = QGridLayout()
        upper_right_layout = QGridLayout()
        upper_layout       = QHBoxLayout()

        upper_left_layout.addWidget(ticker_label,     0, 0, alignment=Qt.AlignRight)
        upper_left_layout.addWidget(rev_growth_label, 1, 0, alignment=Qt.AlignRight)
        upper_left_layout.addWidget(fcf_margin_label, 2, 0, alignment=Qt.AlignRight)
        upper_left_layout.addWidget(nyears_label,     3, 0, alignment=Qt.AlignRight)
        upper_left_layout.addWidget(wacc_label,       4, 0, alignment=Qt.AlignRight)
        upper_left_layout.addWidget(tgr_label,        5, 0, alignment=Qt.AlignRight)

        upper_left_layout.addWidget(self.ticker_entry,     0, 1, alignment=Qt.AlignLeft)
        upper_left_layout.addWidget(self.rev_growth_entry, 1, 1, alignment=Qt.AlignLeft)
        upper_left_layout.addWidget(self.fcf_margin_entry, 2, 1, alignment=Qt.AlignLeft)
        upper_left_layout.addWidget(self.nyears_entry,     3, 1, alignment=Qt.AlignLeft)
        upper_left_layout.addWidget(self.wacc_entry,       4, 1, alignment=Qt.AlignLeft)
        upper_left_layout.addWidget(self.tgr_entry,        5, 1, alignment=Qt.AlignLeft)

        upper_right_layout.addWidget(cr_label,      0, 0, alignment=Qt.AlignRight)
        upper_right_layout.addWidget(tshares_label, 1, 0, alignment=Qt.AlignRight)
        upper_right_layout.addWidget(pfloat_label,  2, 0, alignment=Qt.AlignRight)
        upper_right_layout.addWidget(pshort_label,  3, 0, alignment=Qt.AlignRight)
        upper_right_layout.addWidget(avgvol_label,  4, 0, alignment=Qt.AlignRight)
        upper_right_layout.addWidget(mcap_label,    5, 0, alignment=Qt.AlignRight)

        upper_right_layout.addWidget(self.curr_rev_entry,     0, 1, alignment=Qt.AlignLeft)
        upper_right_layout.addWidget(self.total_shares_entry, 1, 1, alignment=Qt.AlignLeft)
        upper_right_layout.addWidget(self.perc_float_entry,   2, 1, alignment=Qt.AlignLeft)
        upper_right_layout.addWidget(self.perc_short_entry,   3, 1, alignment=Qt.AlignLeft)
        upper_right_layout.addWidget(self.avg_vol_entry,      4, 1, alignment=Qt.AlignLeft)
        upper_right_layout.addWidget(self.mcap_entry,         5, 1, alignment=Qt.AlignLeft)
   
        upper_layout.addLayout(upper_left_layout)
        upper_layout.addLayout(upper_right_layout)

        prefinal_layout.addLayout(theme_layout)
        prefinal_layout.addLayout(upper_layout)
        prefinal_layout.addLayout(info_layout)

        final_layout.addLayout(prefinal_layout)
        final_layout.addLayout(button_layout)

        self.input_frame.setLayout(final_layout)

    def create_output_frame(self):
        output_layout = QGridLayout()
        
        # Main output boxes
        self.fv_entry, fv_layout = get_text_entry_box("Fair Value: ", int(1.5*self.font_size), bold=True, readOnly=True)
        self.cp_entry, cp_layout = get_text_entry_box("Current Price: ", self.font_size, bold=True, readOnly=True)
        self.ud_entry, ud_layout = get_text_entry_box("Upside/Downside (%): ", self.font_size, bold=True, readOnly=True)
        self.erev_entry, erev_layout = get_text_entry_box("Yearly Revenue After N Years: ", self.font_size, bold=True, readOnly=True)

        # Start of reverse DCF outputs
        self.rev_dcf_start = get_label("\nTo Justify the Current Price", self.font_size, bold=True)

        # Credit Label
        self.credit_label = get_label('\nMade by Akash Patel | '+'''<a href='https://github.com/akashaero'>Github -> @akashaero</a>''', 14, bold=False)
        self.credit_label.setOpenExternalLinks(True)

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
        rev_dcf_layout.addWidget(self.credit_label, alignment=Qt.AlignCenter)

        output_layout.addLayout(fv_layout, 0, 0)
        output_layout.addLayout(cp_layout, 1, 0)
        output_layout.addLayout(ud_layout, 2, 0)
        output_layout.addLayout(erev_layout, 3, 0)
        output_layout.addLayout(rev_dcf_layout, 4, 0)

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
        _, _, _, _, _, info_str, extra_info = get_info(self.ticker_entry.text().upper())
        lines = info_str.splitlines()
        lines[-1] = lines[-1] + '     '
        for i, line in enumerate(lines):
            self.info_text.append(line)
            self.info_text.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.curr_rev_entry.setText(extra_info[0])
        self.total_shares_entry.setText(extra_info[1])
        self.perc_float_entry.setText(extra_info[2])
        self.perc_short_entry.setText(extra_info[3])
        self.avg_vol_entry.setText(extra_info[4])
        self.mcap_entry.setText(extra_info[5])

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
            self.curr_rev_entry.clear()
            self.total_shares_entry.clear()
            self.perc_float_entry.clear()
            self.perc_short_entry.clear()
            self.avg_vol_entry.clear()
            self.mcap_entry.clear()
            self.erev_entry.clear()
            current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, info_str, extra_info = get_info(ticker)
            lines = info_str.splitlines()
            lines[-1] = lines[-1] + '     '
            for line in lines:
                self.info_text.append(line)
                self.info_text.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            results = dcf(rev_growth_rate, fcf_margin, nyears, starting_rev, wacc, tgr, total_shares, current_price)
            fair_value, req_rg, req_wacc, req_fcf, curr_rev_growth = results
            fair_value = np.round(fair_value / extra_info[-1], 2)
            final_rev = '$' + get_out_str((starting_rev/extra_info[-1])*(1+rev_growth_rate)**(float(nyears))) # Revenue after N years
            self.curr_rev_entry.setText(extra_info[0])
            self.total_shares_entry.setText(extra_info[1])
            self.perc_float_entry.setText(extra_info[2])
            self.perc_short_entry.setText(extra_info[3])
            self.avg_vol_entry.setText(extra_info[4])
            self.mcap_entry.setText(extra_info[5])
            self.fv_entry.setText("$"+str(fair_value))
            self.cp_entry.setText("$"+str(current_price))
            self.ud_entry.setText(str(calc_up_downside(fair_value, current_price))+"%")
            self.rev_dcf_start.setText("\nTo Justify the Current Price of ${}".format(current_price))
            self.rrev_entry.setText(str(req_rg))
            self.rfcf_entry.setText(str(req_fcf))
            self.rwacc_entry.setText(str(req_wacc))
            self.erev_entry.setText(final_rev)
        except Exception as e:
            self.fv_entry.setText(f"Error")

    def reset_fields(self):
        # Can improve this by making a running list of entries to reset and run a for loop
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
        self.curr_rev_entry.clear()
        self.total_shares_entry.clear()
        self.perc_float_entry.clear()
        self.perc_short_entry.clear()
        self.avg_vol_entry.clear()
        self.mcap_entry.clear()
        self.erev_entry.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dcf_app = DCFApp()
    dcf_app.show()
    sys.exit(app.exec())