def AskMinYield():
    print("How much annual yield do we need? (% per year) (type \"break\" to break)")
    response = input()
    if response == "break":
        return "break"
    if not response.isnumeric:
        print("That is not a number.")
        return AskMinYield()
    if response == "":
        return AskMinYield()
    return float(response)

def AskYears():
    print("How many years worth of data do you want to consider?")
    response = input()
    if response == "break":
        return "break"
    elif response == "":
        return AskYears()
    if response.isnumeric():
        return float(response)
    else:
        print("That is not a number.")
        return AskYears()

def MainTestCase():
    #symbols = [ 'TEVA', 'WM', 'SIG', 'PEGI', 'F', 'SMHB', 'LVHI', 'EPD', 'IBM', 'SIX', 'UVV', 'UG', 'CM', 'BCE', 'BNS']
    symbols = [ 'CM', 'BCE', 'BNS', 'EPD', 'AMZN', 'GDDY', 'PRU']

    # Import the modules now so it will crash before doing work if a module is missing.
    from Stocks import Stock
    import datetime
    import matplotlib.pyplot as plt
    from dateutil.parser import parse

    # Pull the stock data into memory.
    stocks = []
    for symbol in symbols:
        stock = Stock.ShyRetrieve(symbol=symbol, minDate=(datetime.datetime.now() - datetime.timedelta(days=5)))
        if len(stock._history) > 0:
            stocks.append(stock)

    today = datetime.datetime.now()

    # In a loop so data stays in memory if the user wants to change parameters.
    while True:
        yearsToConsider = AskYears()
        minimumYield = AskMinYield()
        if yearsToConsider == "break":
            break
        if minimumYield == "break":
            break

        startDate = today - datetime.timedelta(days = 365 * yearsToConsider)

        print("Plotting...")
        fig, subplots = plt.subplots(nrows=2, ncols=1)
        dividend_plot = subplots[0]
        #growth_plot = subplots[1]
        total_yield_plot = subplots[1]
        dividend_plot.set_ylabel("Dividend (%/yr)")
        dividend_plot.set_xlim(left=startDate, right=today)
        max_dividend = 0.
        min_dividend = 0.

        #growth_plot.set_ylabel("Growth Since (%/yr inflation adjusted)")
        #growth_plot.set_xlim(left=startDate, right=today)
        max_growth = 0.
        min_growth = 0.

        total_yield_plot.set_ylabel("Total Yield (%/yr)")
        total_yield_plot.set_xlim(left=startDate, right=today)
        max_total = 0.
        min_total = 0.

        for stock in stocks:
            if stock.history[0].date > startDate:
                continue
                # Only plot stocks which have enough history.

            filteredGrowth = 0.
            for years in range(1, int(yearsToConsider) + 1):
                filteredGrowth += stock.GrowthAPR(years)
            filteredGrowth /= yearsToConsider
            annualYield = stock.AverageDividendPercent(yearsToConsider) + filteredGrowth
            if annualYield < minimumYield:
                continue
                # Only plot stocks with combined margin better than 10% per year over the past 10 years.
            print(f"Updating plot with data from {stock.name}...")
            print(f"{stock.symbol} {annualYield}% annual yield")
            print("")
            dates = []
            relGrowth = []
            divYieldPercent = []
            latest = stock.history[-1]
            for snapshot in stock.history:
                if snapshot.date < startDate:
                    continue
                if snapshot.price == 0.0:
                    continue
                if (latest.date - snapshot.date).days == 0.0:
                    continue
                annual_growth = 100. * (latest.price / snapshot.price - 1.) * 1.02 ** ((snapshot.date - latest.date).days / 365.25) / \
                    ((latest.date - snapshot.date).days / 365.25)
                if annual_growth > 1. * (latest.date - snapshot.date).days:
                    annual_growth = 1. * (latest.date - snapshot.date).days
                if annual_growth < -1. * (latest.date - snapshot.date).days:
                    annual_growth = -1. * (latest.date - snapshot.date).days
                dates.append(snapshot.date)
                relGrowth.append(annual_growth)
                divYieldPercent.append(100. * snapshot.annualDividend / snapshot.price)
                if relGrowth[-1] > max_growth:
                    max_growth = relGrowth[-1]
                elif relGrowth[-1] < min_growth:
                    min_growth = relGrowth[-1]
                if divYieldPercent[-1] > 100.:
                    print(f"{dates[-1]}: {stock.symbol} has {divYieldPercent[-1]}% dividend?")
                if divYieldPercent[-1] > max_dividend:
                    max_dividend = divYieldPercent[-1]
                elif divYieldPercent[-1] < min_dividend:
                    min_dividend = divYieldPercent[-1]

            dividend_plot.plot(dates, divYieldPercent, label=stock.symbol)
            #growth_plot.plot(dates, relGrowth, label=stock.symbol)

            annualYield = []
            yDates = []
            for index in range(200, len(stock.history)):
                snapshot = stock.history[index]
                if snapshot.date < startDate:
                    continue
                priceLastYear = stock.history[index - 200].price
                if priceLastYear == 0.0:
                    continue
                yDates.append(snapshot.date)
                annualYield.append(100. * ((snapshot.price - priceLastYear) + snapshot.annualDividend) / priceLastYear)
                if annualYield[-1] > max_total:
                    max_total = annualYield[-1]
                elif annualYield[-1] < min_total:
                    min_total = annualYield[-1]
            total_yield_plot.plot(yDates, annualYield, label=stock.symbol)
            
        #growth_plot.plot([parse("1/1/2000"), today], [0, 0], label='Zero')
        total_yield_plot.plot([parse("1/1/2000"), today], [0, 0], label='Zero')
        fig.tight_layout()
        fig.autofmt_xdate()
        dividend_plot.set_ylim(bottom=min_dividend, top=max_dividend)
        #growth_plot.set_ylim(bottom=min_growth, top=max_growth)
        total_yield_plot.set_ylim(bottom=min_total, top=max_total)
        dividend_plot.legend()
        #growth_plot.legend()
        #total_yield_plot.legend()
        plt.show()

if __name__ == "__main__":
    MainTestCase()