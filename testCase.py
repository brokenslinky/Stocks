def MainTestCase():
    #symbols = [ 'SIG','PEGI', 'F', 'SMHB', 'LVHI', 'EPD', 'IBM', 'SIX', 'UVV', 'UG', 'CM', 'BCE', 'BNS']
    symbols = [ 'CM', 'BCE', 'BNS']
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
    print("Plotting...")
    fig, ax = plt.subplots(nrows=2, ncols=1)
    ax = fig.add_subplot("211")
    ax.set_xlabel("Date")
    ax.set_ylabel("Dividend Yield (% / year)")
    from dateutil.parser import parse
    ax.set_xlim(left=parse("1/1/2000"), right=today)
    ax.set_ylim(bottom=0., top=20.)
    bx = fig.add_subplot("212")
    bx.set_xlabel("Date")
    bx.set_ylabel("Anual Growth (% / year)")
    bx.set_xlim(left=parse("1/1/2000"), right=today)
    bx.set_ylim(bottom=-20, top=40)

    for stock in stocks:
        if stock.AverageDividendPercent(10) < 5:
            continue
            # Only plot stocks with dividends better than 5% per year over the past 10 years.
        if today - stock.history[0].date < datetime.timedelta(days = 365 * 10):
            continue
            # Only plot stocks which have 10 years of data.
        print(f"Updating plot with data from {stock.name}...")
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
            relGrowth.append((snapshot.price / latest.price) * 1.02 ** (snapshot.date.year - latest.date.year))
            divYieldPercent.append(100. * snapshot.annualDividend / snapshot.price)
        ax.plot(dates, divYieldPercent, label=stock.symbol)

        annualGrowthPercent = []
        gDates = []
        for index in range(200, len(stock.history)):
            snapshot = stock.history[index]
            priceLastYear = stock.history[index - 200].price
            if priceLastYear == 0.0:
                continue
            gDates.append(snapshot.date)
            annualGrowthPercent.append(100. * (snapshot.price - priceLastYear) / priceLastYear)
        bx.plot(gDates, annualGrowthPercent, label=stock.symbol)

    bx.plot([parse("1/1/2000"), today], [0, 0], label='Zero')
    fig.tight_layout()
    fig.autofmt_xdate()
    ax.legend()
    bx.legend()
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
