'''
Authored by: @akashaero
07/26/2023

Provides important utilities to main programs for stock valuation
'''

import numpy as np
import yfinance as yf
import os, csv, time
from tabulate import tabulate
from scipy.optimize import minimize_scalar

def get_info(ticker):
  stock      = yf.Ticker(ticker)
  income     = stock.income_stmt
  cashflow   = stock.cashflow
  stock_info = stock.info

  # 3 years, 2 years, 1 year
  def get_rates(df):
    results = []
    for i in range(len(df) - 1):
      if np.isnan(df[0]) or np.isnan(df[(len(df) - 1)-i]):
        results.append('-')
      else:
        results.append(((df[0] / df[(len(df) - 1)-i])**(1/((len(df)-1)-i))) - 1)
    return results

  # 3 years, 2 years, 1 year
  def get_margins(r, fcf):
    results = []
    if len(r) != len(fcf):
      return ['-', '-', '-']
    else:
      for i in range(len(r)-1):
        if np.isnan(fcf[i]) or np.isnan(r[i]):
          results.append('-')
        else:
          results.append(fcf[i]/r[i])
      results.reverse()
      return results

  def make_list(label, ar):
    if len(ar) > 3:
      ar = ar[1:]
    tmp_list = [label, '-', '-', '-']
    if len(ar) == 2:
      start_idx = 2
    elif len(ar) == 1:
      start_idx = 3
    else:
      start_idx = 1
    for i in range(len(ar)):
      if ar[0] != '-':
        tmp_list[start_idx] = str(round(100*ar[i], 2))+'%'
      start_idx += 1
      if start_idx >= len(tmp_list):
        break;
    return tmp_list[0:4]

  starting_fcf    = float(cashflow.loc['Free Cash Flow'][0]) if not np.isnan(cashflow.loc['Free Cash Flow'][0]) else '-'
  starting_rev    = float(income.loc['Total Revenue'][0]) if not np.isnan(income.loc['Total Revenue'][0]) else '-'
  FCF_Margin      = round(100*starting_fcf / starting_rev, 2) if not starting_fcf == '-' or not starting_rev == '-' else '-'
  current_price   = round(stock_info['previousClose'], 2)
  total_shares    = stock_info['sharesOutstanding'] if 'sharesOutstanding' in stock_info else income.loc['Basic Average Shares'][0]
  starting_rev    = income.loc['Total Revenue'][0]
  rev_growth      = get_rates(income.loc['Total Revenue'])
  buybacks        = get_rates(income.loc['Diluted Average Shares'])
  fcf_growth      = get_rates(cashflow.loc['Free Cash Flow'])
  fcf_margins     = get_margins(income.loc['Total Revenue'], cashflow.loc['Free Cash Flow'])
  prev_rev_growth = rev_growth[-1]
  prev_fcf_margin = fcf_margins[-1]

  business_summary = stock_info['longBusinessSummary'] if not np.isnan(stock_info['longBusinessSummary']) else '-'
  fwdPE            = stock_info['forwardPE'] if not np.isnan(stock_info['forwardPE']) else '-'
  avgVol           = stock_info['averageVolume'] if not np.isnan(stock_info['averageVolume']) else '-'
  mcap             = stock_info['marketCap'] if not np.isnan(stock_info['marketCap']) else '-'
  ttm_PS           = stock_info['priceToSalesTrailing12Months'] if not np.isnan(stock_info['priceToSalesTrailing12Months']) else '-'
  currency         = stock_info['currency'] if not np.isnan(stock_info['currency']) else '-'
  floatShares      = stock_info['floatShares'] if not np.isnan(stock_info['floatShares']) else '-'
  totalShares      = stock_info['sharesOutstanding'] if not np.isnan(stock_info['sharesOutstanding']) else '-'
  percent_short    = stock_info['shortPercentOfFloat'] if not np.isnan(stock_info['shortPercentOfFloat']) else '-'
  book_val         = stock_info['bookValue'] if not np.isnan(stock_info['bookValue']) else '-'
  pb               = stock_info['priceToBook'] if not np.isnan(stock_info['priceToBook']) else '-'
  PEG              = stock_info['pegRatio'] if not np.isnan(stock_info['pegRatio']) else '-'
  name1            = stock_info['shortName'] if not np.isnan(stock_info['shortName']) else '-'
  name2            = stock_info['longName'] if not np.isnan(stock_info['longName']) else '-'
  total_debt       = stock_info['totalDebt'] if not np.isnan(stock_info['totalDebt']) else '-'
  ROA              = stock_info['returnOnAssets'] if not np.isnan(stock_info['returnOnAssets']) else '-'
  ROE              = stock_info['returnOnEquity'] if not np.isnan(stock_info['returnOnEquity']) else '-'

  if 'forwardPE' in stock_info and 'pegRatio' in stock_info:
    if np.isnan(stock_info['forwardPE']) or np.isnan(stock_info['pegRatio']):
      analyst_growth = '-'
    elif stock_info['pegRatio'] == 0.0:
      analyst_growth = '-'
    else:
      analyst_growth  = str(round(stock_info['forwardPE'] / stock_info['pegRatio'], 2))+'%'
  else:
    analyst_growth = '-'

  header = ['$'+ticker, '3 Years', '2 Years', '1 Year']
  table_data = []
  table_data.append(make_list('Revenue Growth', rev_growth))
  table_data.append(make_list('Dilution(+)/Buybacks(-)', buybacks))
  table_data.append(make_list('FCF Margins', fcf_margins))
  table_data.append(['Analyst Expected Growth (5Y)', analyst_growth, '-', '-'])
  return current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, tabulate(table_data, headers=header)

def dcf(rev_growth_array, fcf_margins_array, n_future_years, latest_revenue, \
        wacc, tgr, total_shares, current_price, reverse_dcf_mode=False):
  if np.array([rev_growth_array]).shape == (1,):
    rev_growth_array = np.full(n_future_years, rev_growth_array)

  if np.array([fcf_margins_array]).shape == (1,):
    fcf_margins_array = np.full(n_future_years, fcf_margins_array)

  # Project FCF
  proj_fcf = []
  rev_inc = latest_revenue
  for i in range(0, n_future_years):
    rev_inc = rev_inc * (1+rev_growth_array[i])
    proj_fcf.append(rev_inc*fcf_margins_array[i])

  # Get discount factors
  discount_factors = []
  for i in range(0,n_future_years):
    discount_factors.append((1+wacc)**(i+1))

  # Total discounted fcf for n_future_years
  discounted_fcf = 0
  for i, p in enumerate(proj_fcf):
    discounted_fcf += p/discount_factors[i]

  # Terminal value (discounted)
  terminal_value = (proj_fcf[-1] * (1+tgr))/(wacc - tgr)
  terminal_value /= discount_factors[-1]

  # Total value for all shares
  todays_value = discounted_fcf + terminal_value

  # Fair value per share.
  fair_value = todays_value/total_shares

  assumed_cagr = calc_cagr(rev_growth_array, n_future_years)

  if reverse_dcf_mode:
    return fair_value

  # Reverse DCF Functions
  def reverse_dcf_revenue(rev_growth_rate, fcf_margins_array, n_future_years, \
                        latest_revenue, wacc, tgr, total_shares, current_price):
    return abs(dcf(np.full(n_future_years,rev_growth_rate), fcf_margins_array, \
                           n_future_years, latest_revenue, wacc, tgr, total_shares, current_price, reverse_dcf_mode=True)\
               - current_price)

  def reverse_dcf_fcf_margin(fcf_margin, rev_growth_array, n_future_years, \
                             latest_revenue, wacc, tgr, total_shares, \
                             current_price):
    return abs(dcf(rev_growth_array, np.full(n_future_years,fcf_margin), \
                   n_future_years, latest_revenue, wacc, tgr, total_shares, current_price, reverse_dcf_mode=True) \
               - current_price)

  def reverse_dcf_discount_rate(wacc, rev_growth_array, fcf_margins_array, \
                                n_future_years, latest_revenue, tgr, \
                                total_shares, current_price):
    return abs(dcf(rev_growth_array, fcf_margins_array, n_future_years, \
                   latest_revenue, wacc, tgr, total_shares, current_price, reverse_dcf_mode=True) - current_price)

  required_rev_growth    = round(100*minimize_scalar(reverse_dcf_revenue, \
                         args=(fcf_margins_array, n_future_years, latest_revenue, \
                               wacc, tgr, total_shares, \
                               current_price)).x, 2)

  required_discount_rate = round(100*minimize_scalar(reverse_dcf_discount_rate, \
                           args=(rev_growth_array, fcf_margins_array, n_future_years, \
                                 latest_revenue, tgr, total_shares, \
                                 current_price)).x, 2)

  required_fcf_margin    = round(100*minimize_scalar(reverse_dcf_fcf_margin, \
                           args=(rev_growth_array, n_future_years, latest_revenue, \
                                 wacc, tgr, total_shares, \
                                 current_price)).x, 2)

  

  return round(fair_value, 2), required_rev_growth, required_discount_rate, required_fcf_margin, assumed_cagr

def calc_up_downside(fair_value, current_price):
  if fair_value > current_price:
    # Stock is undervalued compared to current price
    return round(((fair_value-current_price)/current_price)*100, 2)
  else:
    # Current price is overvalued compared to fair value
    return round(-100*((current_price - fair_value)/current_price), 2)

def print_calculated_info(results, current_price, fcf_margins, prev_rev_growth, \
                          prev_fcf_margin, tkr, tgr, wacc, n_future_years):
  fv, r_rg, r_wacc, r_fcf, rev_growth = results
  if np.array([fcf_margins]).shape == (1,):
    pass
  else:
    fcf_margins = np.average(np.array(fcf_margins))

  print('Based on your inputs, for next {} years,'.format(n_future_years))
  print('Assuming {}% of average annual revenue growth,'.format(rev_growth))
  print('         {}% of free cash flow margin, and'.format(fcf_margins))
  print('         {}% of terminal growth rate,\n'.format(tgr))
  print('The fair value for {} stock is ${} to get {}% of annualized return for next {} years.'\
        .format(tkr, fv, wacc, n_future_years))
  print('\nBased on previous close price of ${}, the upside/downside is {}%'\
       .format(current_price, calc_up_downside(fv, current_price)))
  print('\nTo justify the current stock price of ${}, Either,'\
        .format(current_price))
  print('{} would have to grow at {}% average annual rate for next {} years'\
        .format(tkr, r_rg, n_future_years))
  print('  or     have free cash flow margin of {}%'\
        .format(r_fcf))
  print('  or     you get {}% annualized return for next {} years compared to assumed {}% '\
        .format(r_wacc, n_future_years, wacc))

def get_calculated_info(results, current_price, fcf_margins, prev_rev_growth, \
                          prev_fcf_margin, tkr, tgr, wacc, n_future_years):
  fv, r_rg, r_wacc, r_fcf, rev_growth = results
  if np.array([fcf_margins]).shape == (1,):
    pass
  else:
    fcf_margins = np.average(np.array(fcf_margins))

  out_str = ''
  out_str += ('Based on your inputs, for next {} years,'.format(n_future_years))
  out_str += ('Assuming {}% of average annual revenue growth,'.format(rev_growth))
  out_str += ('         {}% of free cash flow margin, and'.format(fcf_margins))
  out_str += ('         {}% of terminal growth rate,\n'.format(tgr))
  out_str += ('The fair value for {} stock is ${} to get {}% of annualized return for next {} years.'\
        .format(tkr, fv, wacc, n_future_years))
  out_str += ('\nBased on previous close price of ${}, the upside/downside is {}%'\
       .format(current_price, calc_up_downside(fv, current_price)))
  out_str += ('\nTo justify the current stock price of ${}, Either,'\
        .format(current_price))
  out_str += ('{} would have to grow at {}% average annual rate for next {} years'\
        .format(tkr, r_rg, n_future_years))
  out_str += ('  or     have free cash flow margin of {}%'\
        .format(r_fcf))
  out_str += ('  or     you get {}% annualized return for next {} years compared to assumed {}% '\
        .format(r_wacc, n_future_years, wacc))
  return out_str

def calc_cagr(rev_growth_array, N):
  if np.array([rev_growth_array]).shape == (1,):
    return round(100*rev_growth_array, 2)
  final_val = 1
  for r in rev_growth_array:
    final_val *= (1+r)
  return round(np.sign(final_val)*100*(np.abs(final_val/1)**(1/N) - 1), 2)

def write_batch_mode_csv(fname, data):
  if not os.path.exists('./batch_mode_files/results'):
    os.mkdir('./batch_mode_files/results')
  csv_header = ['stock', 'fair_value', 'current_price', 'upside/(downside)', \
                'assumed_revenue_growth(%)', 'assumed_fcf_margin (%)', \
                'current_price_rev_growth (%)', 'current_price_fcf_margin (%)', \
                'current_price_required_return (%)']
  timestr = time.strftime("%Y%m%d-%H%M%S")
  print('Writing All Results in {} .....'.format('./batch_mode_files/results/'+timestr+'_'+fname))
  with open('./batch_mode_files/results/'+timestr+'_'+fname, 'w', newline='') as f:
    write = csv.writer(f)
    write.writerow(csv_header)
    write.writerows(data)
