
# Intrinsic Value Calculator

The key to valuing a business is to forecast how much of cash flow you will have in hand for next few years and to discount that cash flow in terms of today's dollars. **$100 today is not the same as $100 in 5 years**. If someone tries to sell you a security that is worth $100 in 5 years and promises a 5% annual, risk-free return rate, you'd pay $78.35 for that security today which will bloom into $100 in 5 years at an annual rate of 5% compounded!

As Warren Buffett has famously said,
> "Price is What You Pay, Value is What You Get"

The same principle applies when you are valuing a business (stock of a business). If a business promises to generate a certain amount of dollars in cumulative cash flow in the future, you would want to discount that cash flow in today's dollars assuming you want to get a certain percentage of annualized return rate. You definitely would not want to pay for future cash flow as the face value (because that ensures a solid 0% return given your assumptions about the company are correct). Now, assuming that the company you are evaluating will still be in the business after your analysis period, you'd calculate the terminal value of a business by using the terminal growth rate and add that to your fair value calculations as well. This tool assumes a terminal growth rate of 2.5% with the user option to change it with each analysis. The terminal growth rate suggests that when the company reaches maturity, it will likely grow at the long-term growth rate of the economy.

Currently, this tool runs a **Discounted Cash Flow (DCF)** analysis to calculate the fair value of a stock. In the future, more models will be added such as "Earnings Per Share Based Model", and "Dividend Discount Model (DDM)". 

No model or technique is perfect and nothing is going to give you an exact price at which a business should be bought. What this model helps with is getting you closer to the true value of a business while taking your assumptions about the business at face value. This should not be relied on as the only data point you look at before making your financial decisions.

This tool also has a functionality where, for the current stock price, how much of revenue growth (keeping the assumed free cash flow margin and required rate of return constant), or what free cash flow margin (keeping the assumed revenue growth and required rate of return constant), or what required rate of return is priced into the stock is calculated after each fair value evaluation. 

For example, if a company stock's fair value is $62.8 for assumed revenue growth of 12%, free cash flow margin of 25%, and required rate of return of 10% for the next 7 years but it is trading at $445.15. To justify the current stock price of $445.15, Either,

This company would have 
> to grow at a 52.05% average annual rate for the next 7 years
> or               have a free cash flow margin of 176.98%
> or               give you a 3.65% annualized return for the next 7 years compared to assumed 10.0%

Some quick notes. DCF models do not value bank stocks well. For banks, multiples of their book value are a preferred way of valuation. Do not get carried away with assuming unrealistically high growth rates especially when you are applying that rate for several years in the future. Some companies do not have their data available online and in that case, this program might throw an error. Please open up the issue and I will look into that.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Arguments](#arguments)
- [Examples](#examples)
- [Upcoming Features](#upcomingfeatures)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository to your local machine:

```
git clone https://github.com/akashaero/Intrinsic-Value-Calculator.git
cd Intrinsic-Value-Calculator
```

2. (Optional) Set up a virtual environment or conda environment to isolate the dependencies:

```
python -m venv stonks           # Create Virtual Environment
source stonks/bin/activate      # Activate For Linux/macOS
stonks\Scripts\activate.bat     # Activate For Windows
```
or for the Conda environment

```
conda create --name stonks
conda activate stonks
```

3. Install the required dependencies:

```
python -m pip install -r requirements.txt
```

## Usage

There are two modes users can run this tool in.

### Single Stock Evaluation
If you want to get started quickly or just have a handful of stocks to evaluate, this mode is best to stay in. To evaluate a stock's fair value, run the following command with your assumptions

```
python get_fair_value.py <ticker> <future_revenue_growth> <free_cash_flow_margin> --N <number_of_years_in_future> --rrr <required_rate> --tgr <terminal_growth_rate>
```

#### Arguments
Here, the only mandatory arguments are **ticker**, **future_revenue_growth**, and **free_cash_flow_Margin**.

1. **ticker**                                  : Stock ticker of the company you want to evaluate
2. **future_revenue_growth**                   : Assumption about the future revenue growth for the next N years
3. **free_cash_flow_margin**                   : Assumption about the future free cash flow margin for the next N years
4. **- -N (Optional)**: Number of years for which you want to forecast revenue growth and free cash flow margins (Default 7)
5. **- -rrr (Optional)**: Required rate of return (Default 10%)
6. **- -tgr (Optional)**: Terminal growth rate of a company (Default 2.5%)

#### Examples

Here's how you can use this tool for stock evaluations

```bash
# Example 1: Single stock valuation mode
python get_fair_value.py MSFT 12.05 28.3

or 

python get_fair_value.py MSFT 12.05 28.3 --N 8 --rrr 10.25 --tgr 2.7
```

### Batch Mode Stock Evaluations
If you want to evaluate the fair value of multiple stocks in one go, you can run this tool in batch mode. All you need is a CSV file with 3 columns in following format (look at example file in ./batch_mode_files/example.csv).

```
Stock_Ticker  , Rev_Growth_Estimate, FCF_Margin_Estimate
  Value 1-1   ,     Value 2-1      ,     Value 3-1
  Value 1-2   ,     Value 2-2      ,     Value 3-2
  Value 1-3   ,     Value 2-3      ,     Value 3-3
  Value 1-4   ,     Value 2-4      ,     Value 3-4
     .                 .                    .
     .                 .                    .
     .                 .                    .
  Value 1-N   ,     Value 2-N      ,     Value 3-N
```
The tool has an argument that allows users to use a list of stock tickers and build the CSV file by interactively providing revenue growth and free cash flow margin estimates.

```
python batch_mode.py <csv_file_name>
```
#### Arguments

**csv_file** : CSV file with revenue growth and free cash flow margin assumptions in the "./batch_mode_files" folder

or
```
python batch_mode.py --gen_file <ticker_text_file>
```
#### Arguments

**- -gen_file**  : Switches on the CSV file generation for batch mode
**ticker_text_file**  : File of ticker list in "./ticker_groups" folder

#### Examples

```
# Example 1: Generate csv file for batch mode evaluations (Optional).
python batch_mode.py --gen_file example.txt

# Example 2: Run the tool in batch mode
python batch_mode.py example.csv
```
## Upcoming Features
* A simple graphical user interface is in the works for this application and will be released soon here!
* A theoretical guide for discounted cash flow model will be posted in the form of a blog post.
* More financial models are being worked on including the "Dividend Discount Model", and "EPS based Fair Value Model"

## Contributing

If you'd like to contribute, please open up a pull request and if it is addressing any issues, please state so clearly. All contributions are very welcome!

## License

Apache 2.0 License

Apache 2.0 License © [Akash Patel](https://github.com/akashaero)
