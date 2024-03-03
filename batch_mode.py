'''
Authored by: @akashaero
07/26/2023

Runs DCF calculator in batch mode using a CSV file of stock lists with revenue 
growths and fcf margins.

python batch_mode.py <filename> --generate_file <OPTIONAL> -N <OPTIONAL> -tgr <OPTIONAL> -rrr <OPTIONAL>


Input CSV sheet can be generated using --generate_file flag. Please
specify tickers in a text file for this.
For example,

$ python batch_mode.py ./ticker_groups/dow30.txt --generate_file

Once you have the CSV file, use following to to run analysis on all 
stocks and get answers in a separate CSV file.

$ python batch_mode.py file.csv -N 7 -rrr 0.1 -tgr 0.025

Following values are optional and remains the same for each stock analysis.
--N   Number of Years for Analysis (Default 7)
--rrr Required Rate of Return aka Discount Rate (Default 10%)
--tgr Terminal Growth Rate (Default 2.5%)

CSV File Format (Also look sample.csv in the folder)

Stock_Ticker  , Rev_Growth_Estimate, FCF_Margin_Estimate
  Value 1-1   ,     Value 2-1      ,     Value 3-1
  Value 1-2   ,     Value 2-2      ,     Value 3-2
  Value 1-3   ,     Value 2-3      ,     Value 3-3
  Value 1-4   ,     Value 2-4      ,     Value 3-4
     .                 .                    .
     .                 .                    .
     .                 .                    .
  Value 1-N   ,     Value 2-N      ,     Value 3-N

'''

import numpy as np
import yfinance as yf
import argparse
import csv
import pandas as pd
from tabulate import tabulate
from provider import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Calculate Intrinsic Value of Businesses Using Batch Mode!')
  parser.add_argument("file", type=str, help="If generating csv file, provide path to stock ticker, else, provide csv file name")
  # Optional arguments with default values
  parser.add_argument("--N", type=int, default=7, \
               help="Number of years to run this analysis for (Default 7 Years).")
  parser.add_argument("--rrr", type=float, default=10, \
               help="Required Rate of Return (Default 10%).")
  parser.add_argument("--tgr", type=float, default=2.5, \
               help="Terminal Growth Rate (Default 2.5%).")
  parser.add_argument('-gen_file', '--gen_file', action='store_true')
  args = parser.parse_args()

  # Condition file extension
  if args.gen_file:
    csv_fname    = args.file.split('.')[0]+'.csv'

  if args.gen_file:
    csv_list = []
    csv_header = ['Stock', 'Rev_Growth_Estimate (%)', 'FCF_Margin_Estimate (%)']
    tickers = np.loadtxt('./ticker_groups/'+args.file, dtype=str)
    for t in tickers:
      tmp_list = []
      tmp_list.append(t)
      print('\nFetching ${} data'.format(t))
      get_info(t)
      print('')
      future_rev_growth  = float(input('Expected Future Revenue Growth for {} Stock? ---------- in % (i.e. 6) : '.format(t)))
      future_fcf_margins = float(input('Expected Future Free Cash Flow Margin for {} Stock?  in % (i.e. 13.6) : '.format(t)))
      tmp_list.append(future_rev_growth)
      tmp_list.append(future_fcf_margins)
      csv_list.append(tmp_list)
      print('-------------------------------------------------------------------------------------------------------------------')

    with open('./batch_mode_files/'+csv_fname, 'w', newline='') as f:
      write = csv.writer(f)
      write.writerow(csv_header)
      write.writerows(csv_list)

    print('\nWrote CSV file at {}, please run \'python batch_mode.py {}\' to get fair values.'.format('./batch_mode_files/'+csv_fname, csv_fname))
  else:
    # Read CSV
    data = pd.read_csv('./batch_mode_files/'+args.file, index_col=0)
    
    # Run subprocesses in silent mode
    csv_list = []
    for t in data.index:
      tmp_list = []
      tmp_list.append(t)
      current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin = get_info(t)
      results = dcf(data.loc[t]['Rev_Growth_Estimate (%)']/100., data.loc[t]['FCF_Margin_Estimate (%)']/100., args.N, starting_rev, args.rrr/100., args.tgr/100., total_shares, current_price)
      fv, r_rg, r_wacc, r_fcf, rev_growth = results
      tmp_list.append('$'+str(round(fv, 2)))
      tmp_list.append('$'+str(round(current_price, 2)))
      tmp_list.append(str(calc_up_downside(fv, current_price))+'%')
      tmp_list.append(str(rev_growth)+'%')
      tmp_list.append(str(round(data.loc[t]['FCF_Margin_Estimate (%)'], 2))+'%')
      tmp_list.append(str(r_rg)+'%')
      tmp_list.append(str(r_fcf)+'%')
      tmp_list.append(str(r_wacc)+'%')
      print('Analyzed ${}\n'.format(t))
      csv_list.append(tmp_list)

    write_batch_mode_csv('dcf_results.csv', csv_list)