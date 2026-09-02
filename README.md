# python-currency-cli

A currency converter for the terminal and for your own scripts, built on **official central bank rates**. Zero dependencies, no API key.

```
$ currency convert 100 USD EUR
100 USD = 85.3800 EUR  (rate 0.8538, inverse, ecb 2026-09-02)

$ currency convert 250 GBP INR --bank rbi
$ currency table hmrc
$ currency sources
```

Rates come from the keyless [AllRatesToday](https://allratestoday.com/central-bank-rates-api/) open endpoint, which republishes each institution's own table once a day: ECB, Federal Reserve, Bank of England, RBI, PBoC, HMRC, US Treasury and 100 more. Every answer tells you whether the rate was **published**, an **inverse**, or a **cross** via the bank's home currency, so you can cite it correctly on an invoice or tax return.

## Use this template

Click **Use this template** on GitHub, or:

```sh
pip install -e .
currency convert 100 USD EUR
python -m unittest
```

## In your own code

```python
from currency_cli import convert, latest_table

convert(100, "USD", "EUR", bank="ecb")
# {'amount': 100, 'result': 85.38, 'rate': 0.8538, 'method': 'inverse', 'bank': 'ecb', 'date': '2026-09-02', ...}

latest_table("fed")["rates"]
```

## Live mid-market rates

Official tables are daily fixings. For real-time rates across 160+ currencies, [get a free API key](https://allratestoday.com/register) and:

```sh
export ALLRATES_API_KEY=your_key
currency convert 100 USD EUR --live
```

## Data files instead of an API

The same tables, with full history as CSV, live in [central-bank-exchange-rates](https://github.com/AllRates-Today/central-bank-exchange-rates) and are served by jsDelivr.

## License

MIT. Rate data is free to use with attribution to [AllRatesToday](https://allratestoday.com).
