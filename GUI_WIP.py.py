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

import tkinter as tk
from tkinter import ttk
import numpy as np
import yfinance as yf
from scipy.optimize import minimize_scalar
import argparse
from provider import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class DCFApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Discounted Cash Flow (DCF) Calculator")
        self.geometry("500x400")

        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)

        ttk.Label(input_frame, text="Ticker:").grid(row=0, column=0, padx=5, pady=5)
        self.ticker_entry = ttk.Entry(input_frame)
        self.ticker_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="Enter the stock ticker symbol").grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="Revenue Growth Rate (%):").grid(row=1, column=0, padx=5, pady=5)
        self.rev_growth_entry = ttk.Entry(input_frame)
        self.rev_growth_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="Enter the expected revenue growth rate as a percentage").grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="FCF Margin (%):").grid(row=2, column=0, padx=5, pady=5)
        self.fcf_margin_entry = ttk.Entry(input_frame)
        self.fcf_margin_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="Enter the expected free cash flow margin as a percentage").grid(row=2, column=2, padx=5, pady=5)

        # Create buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.calculate_button = ttk.Button(button_frame, text="Calculate", command=self.calculate_dcf)
        self.calculate_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_fields)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Create output area
        output_frame = ttk.LabelFrame(self, text="Output")
        output_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def calculate_dcf(self):
        ticker = self.ticker_entry.get().upper()
        rev_growth_rate = float(self.rev_growth_entry.get()) / 100
        fcf_margin = float(self.fcf_margin_entry.get()) / 100

        try:
            current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin = get_info(ticker)
            results = dcf(rev_growth_rate, fcf_margin, 7, starting_rev, 0.1, 0.025, total_shares, current_price)
            output = get_calculated_info(results, current_price, round(100 * fcf_margin, 2),
                                           round(100 * prev_rev_growth, 2), round(100 * prev_fcf_margin, 2), ticker,
                                           2.5, 10.0, 7)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, output)
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {e}")

    def reset_fields(self):
        self.ticker_entry.delete(0, tk.END)
        self.rev_growth_entry.delete(0, tk.END)
        self.fcf_margin_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)

if __name__ == "__main__":
    app = DCFApp()
    app.mainloop()