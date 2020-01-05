def MainTestCase():
    symbols = [ 'SIG','PEGI', 'F', 'SMHB', 'LVHI', 'EPD', 'IBM', 'SIX', 'UVV', 'UG', 'CM', 'BCE', 'BNS']
    from Stocks import Stock
    stocks = []

    for symbol in symbols:
        stock = Stock.ShyRetrieve(symbol=symbol, downloadAll=True)
        if len(stock._history) > 0:
            stocks.append(stock)
            print(f"{stocks[-1].name} added to stocks array. \n{len(stocks)} stocks are in the array.")

    print("Plotting...")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(nrows=2, ncols=1)
    ax = fig.add_subplot("211")
    ax.set_xlabel("Date")
    ax.set_ylabel("Dividend Yield (% / year)")
    import datetime
    from dateutil.parser import parse
    ax.set_xlim(left=parse("1/1/2000"), right=datetime.datetime.now())
    ax.set_ylim(bottom=0., top=50.)
    bx = fig.add_subplot("212")
    bx.set_xlabel("Date")
    bx.set_ylabel("Annualized Dividend ($ / year)")
    bx.set_xlim(left=parse("1/1/2000"), right=datetime.datetime.now())
    bx.set_ylim(bottom=0., top=50.)

    for stock in stocks:
        if stock.AverageDividendPercent(10) < 7.2:
            continue
            # Only plot stocks with dividends better than 7.2% per year over the past 10 years.
        print(f"Updating plot with data from {stock.name}...")
        dates = []
        #prices = []
        dividends = []
        divYieldPercent = []
        for snapshot in stock.history:
            if snapshot.price == 0.0:
                continue
            dates.append(snapshot.date)
            #prices.append(snapshot.price)
            dividends.append(snapshot.annualDividend)
            divYieldPercent.append(100. * snapshot.annualDividend / snapshot.price)
        ax.plot(dates, divYieldPercent, label=stock.symbol)
        bx.plot(dates, dividends, label=stock.symbol)
    ax.legend()
    bx.legend()
    plt.show()
        
    #fig, ax = plt.subplots()
    #bx = ax.twinx()
    #ax.plot(dates, prices, label='Cost of Stock')
    #ax.set_xlabel('Date')
    #ax.set_ylabel('Cost Per Stock (USD)')
    #bx.plot(dates, dividends, label='Annualized Dividends')
    #bx.set_ylabel('Annualized Dividends (USD)')
    #fig.tight_layout()
    plt.show()
