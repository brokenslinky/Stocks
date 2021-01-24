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
    if response.isnumeric:
        return float(response)
    elif response == "":
        return AskYears()
    else:
        print("That is not a number.")
        return AskYears()

def MainTestCase():
    symbols = [ 'TEVA', 'WM', 'SIG', 'PEGI', 'F', 'SMHB', 'LVHI', 'EPD', 'IBM', 'SIX', 'UVV', 'UG', 'CM', 'BCE', 'BNS']
    #symbols = [ 'PEGI', 'EPD', 'UVV', 'UG', 'CM', 'BCE', 'BNS']
    from Stocks import Stock
    stocks = []

    for symbol in symbols:
        stock = Stock.ShyRetrieve(symbol=symbol, downloadAll=True)
        if len(stock._history) > 0:
            stocks.append(stock)
            print(f"{stocks[-1].name} added to stocks array. \n{len(stocks)} stocks are in the array.")

    import datetime
    today = datetime.datetime.now()

    import matplotlib.pyplot as plt

    while True:
        yearsToConsider = AskYears()
        minimumYield = AskMinYield()
        if yearsToConsider == "break":
            break
        if minimumYield == "break":
            break

        print("Plotting...")
        fig, ax = plt.subplots(nrows=2, ncols=1)
        ax = fig.add_subplot("311")
        ax.set_xlabel("Date")
        ax.set_ylabel("Dividend Yield (% / year)")
        from dateutil.parser import parse
        ax.set_xlim(left=parse("1/1/2000"), right=today)
        ax.set_ylim(bottom=0., top=20.)

        bx = fig.add_subplot("312")
        bx.set_xlabel("Date")
        bx.set_ylabel("Inflation Adjusted Growth (%)")
        bx.set_xlim(left=parse("1/1/2000"), right=today)
        bx.set_ylim(bottom=-100, top=100)

        cx = fig.add_subplot("313")
        cx.set_xlabel("Date")
        cx.set_ylabel("Annual Yield (%)")
        cx.set_xlim(left=parse("1/1/2000"), right = today)
        cx.set_ylim(bottom=-100, top=100)

        for stock in stocks:
            if today - stock.history[0].date < datetime.timedelta(days=365*yearsToConsider):
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
            #prices = []
            #dividends = []
            relGrowth = []
            divYieldPercent = []
            latest = stock.history[-1]
            for snapshot in stock.history:
                if snapshot.price == 0.0:
                    continue
                dates.append(snapshot.date)
                #prices.append(snapshot.price)
                #dividends.append(snapshot.annualDividend)
                relGrowth.append(100. * (snapshot.price / latest.price) * 1.02 ** (latest.date.year - snapshot.date.year))
                divYieldPercent.append(100. * snapshot.annualDividend / snapshot.price)
            ax.plot(dates, divYieldPercent, label=stock.symbol)
            bx.plot(dates, relGrowth, label=stock.symbol)

            annualYield = []
            yDates = []
            for index in range(200, len(stock.history)):
                snapshot = stock.history[index]
                priceLastYear = stock.history[index - 200].price
                if priceLastYear == 0.0:
                    continue
                yDates.append(snapshot.date)
                annualYield.append((100. * (snapshot.price - priceLastYear) + snapshot.annualDividend) / priceLastYear)
            cx.plot(yDates, annualYield, label=stock.symbol)
            
        bx.plot([parse("1/1/2000"), today], [0, 0], label='Zero')
        cx.plot([parse("1/1/2000"), today], [0, 0], label='Zero')
        fig.tight_layout()
        fig.autofmt_xdate()
        ax.legend()
        bx.legend()
        cx.legend()
        fig.show()
        
        #fig, ax = plt.subplots()
        #bx = ax.twinx()
        #ax.plot(dates, prices, label='Cost of Stock')
        #ax.set_xlabel('Date')
        #ax.set_ylabel('Cost Per Stock (USD)')
        #bx.plot(dates, dividends, label='Annualized Dividends')
        #bx.set_ylabel('Annualized Dividends (USD)')
        #fig.tight_layout()
        plt.show()
