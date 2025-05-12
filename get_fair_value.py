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

# test only for version control using git

from scipy.optimize import minimize_scalar
import argparse
from src.provider import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Parse user arguments
parser = argparse.ArgumentParser(description='Calculate Intrinsic Value of A Business!')
parser.add_argument("ticker", type=str,   help="Stock Ticker")
parser.add_argument("rev_growth", type=float, nargs="+", \
                   help="Either a single growth rate or a list of growth rates")
parser.add_argument("fcf_margin", type=float, nargs="+", \
                   help="Either single FCF margin or a list of FCF margins")

# Optional arguments with default values
parser.add_argument("--N", type=int, default=7, \
             help="Number of years to run this analysis for (Default 7 Years).")
parser.add_argument("--rrr", type=float, default=10.0, \
             help="Required Rate of Return (Default 10%).")
parser.add_argument("--tgr", type=float, default=2.5, \
             help="Terminal Growth Rate (Default 2.5%).")
parser.add_argument('-S', '--S', action='store_true')

args = parser.parse_args()

# User Defined Parameters
ticker           = args.ticker.upper()      # ticker
n_future_years   = args.N                   # N (OPTIONAL)
discount_rate    = args.rrr/100.            # rrr (OPTIONAL)
rev_growth_rate  = args.rev_growth[0]/100.  # rev_g
fcf_margin       = args.fcf_margin[0]/100.  # fcf_m
term_growth_rate = args.tgr/100.            # tgr (OPTIONAL)

# Get required data and run DCF. Print results immediately if not running in batch mode
current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, data, extra_info = get_info(ticker)
print(data, '\n')
results = dcf(rev_growth_rate, fcf_margin, n_future_years, starting_rev, discount_rate, term_growth_rate, total_shares, current_price)

if not args.S:
  print_calculated_info(results, current_price, \
                        round(100*fcf_margin, 2), \
                        round(100*prev_rev_growth, 2), \
                        round(100*prev_fcf_margin, 2), \
                        ticker, \
                        round(100*term_growth_rate, 2), \
                        round(100*discount_rate, 2),\
                        n_future_years)
