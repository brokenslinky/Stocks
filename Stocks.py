class Stock:
    """A class to represent a publicly traded stock."""
    import pandas
    import datetime

    @property
    def symbol(self):
        """The symbol used to identify this Stock on exchange markets."""
        return self._symbol
    @symbol.setter
    def symbol(self, symbol):
        """Set the symbol of this Stock"""
        self._symbol = symbol

    @property
    def name(self):
        """The name of the company associated with this Stock."""
        return self._name
    @name.setter
    def name(self, name):
        """Set the name of this Stock."""
        self._name = name

    @property
    def market(self):
        """The market this Stock is traded in."""
        return self._market
    @market.setter
    def market(self, market):
        """Set the market this Stock is traded in."""
        self._market = market

    @property
    def history(self):
        """(List[Stock.Snapshot]) The known history of this Stock."""
        return self._history
    @history.setter
    def history(self, market):
        """Set the history of this Stock."""
        self._history = history

    class Snapshot:
        """A snapshot of the Stock at a single moment in time."""
        import datetime
        def __init__(self, price, date=datetime.datetime.now(), annualDividend=0.):
            """
            Create a new Stock Snapshot

            Parameters:
                price (USD): The cost of one unit of Stock at this time.
                date: The timestamp for this Snapshot.
                annualDividend (USD/year): The total dividends paid in one year.
            """
            self.price = price
            self.date = date
            self.annualDividend = annualDividend

    def __init__(self, symbol, name=None, market=None, history=None):
        """
        Create a new Stock with the given symbol.

        Parameters:
            symbol: The symbol used to identify this Stock on the exchange market.
            name: The name of the company represented by this Stock.
            market: The name of the market this Stock is traded in.
            history ([Stock.Snapshot]): The known history of this Stock.
        """
        self._symbol = symbol
        self._name = name
        if name == None:
            self._name = symbol
        self._market = market
        if history != None:
            self._history = history
        else:
            self._history = []
        
    def AddSnapshot(self, price, date=datetime.datetime.now(), annualDividend=0.):
        """
        Add a Snapshot to the Stock's history.

        Parameters:
            price (USD): The cost of one unit of Stock at this time.
            date: The timestamp for this Snapshot.
            annualDividend (USD/year): The total dividends paid in one year.
        """
        self._AddSnapshot(self.Snapshot(price=price, date=date, annualDividend=annualDividend))
        
    def _AddSnapshot(self, snapshot):
        """
        Add a Snapshot to the Stock's history.

        Parameters:
            snapshot (Stock.Snapshot): The Snapshot to add to this Stock's history.
        """
        if self._history.count(snapshot) == 0:
            self._history.append(snapshot)
            
    def Update(self):
        """Updates the Stock's history based on the most recent data from the yfinance API."""
        print(f"Updating {self.name} from yfinance API...")
        import yfinance as yf
        import datetime
        stock = yf.Ticker(self._symbol)
        if self.name == None or self.name == self.symbol:
            if "shortName" in stock.info:
                self.name = stock.info['shortName']
        yhistory = stock.history(period="max")
        print(yhistory)
        print()

        dividends = []
        for date, row in yhistory.iterrows():
            dividends.append((date, row['Dividends']))
            if row['Dividends'] != 0.:
                while date - dividends[0][0] > datetime.timedelta(days=360):
                    dividends.remove(dividends[0])
            else:
                while date - dividends[0][0] > datetime.timedelta(days=370):
                    dividends.remove(dividends[0])

            annualDividend = 0.
            for dividend in dividends:
                annualDividend += dividend[1]
                
            self.AddSnapshot(price=row['Open'], date=date, annualDividend=annualDividend)
            self.AddSnapshot(price=row['Close'], date=date, annualDividend=annualDividend)
        print(f"History for {self.name} updated. Press any key...")
        input()

    @staticmethod
    def FromYfinance(symbol):
        """
        Create a new Stock using the yfinance API.

        Parameters:
            symbol: The symbol used to identify this Stock on exchange markets
        """
        stock = Stock(symbol)
        stock.Update()
        return stock
    
    def SaveToCSV(self):
        """Save this stock to a CSV file."""
        import csv 
        csvfile = open(f"Stocks/{self.symbol}.csv", "w", newline='')
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow([self.symbol, self.name, self.market])
        writer.writerow(['Date', 'Price', 'Annualized Dividend'])
        for snapshot in self._history:
            writer.writerow([snapshot.date.strftime("%m/%d/%Y"), snapshot.price, snapshot.annualDividend])
        csvfile.close()
        print(f"{self.name} saved to /Stocks/{self.symbol}.csv")

    @staticmethod
    def ParseCSV(path):
        """
        Return Stock data from a CSV file.

        Parameters:
            path: Relative path to the CSV file to parse.

        Returns:
            Stock parsed from the given CSV file.
        """

        import csv
        csvfile = open(path, newline='')
        reader = csv.reader(csvfile, delimiter=',')
        stock = Stock(symbol=symbol)

        rowNum = 0
        from dateutil.parser import parse
        for row in reader:
            if rowNum == 0:
                stock.name = row[1]
                stock.market = row[2]
            elif rowNum > 1:
                #row[1] is header information "date, price, dividend"
                stock.AddSnapshot(price=float(row[1]), date=parse(row[0]), annualDividend=float(row[2]))
            rowNum += 1

        csvfile.close()
        return stock
    
    def SaveToJSON(self):
        """
        !NOT IMPLEMENTED! 
        Save this stock to a JSON file.
        """
        import json

        f = open(f"/Stocks/{self.symbol}.JSON", "w")
        j = {"name": self.name, "symbol": self.symbol}

        f.write("{\"name\":\"" + str(self.name) + "\", ")
        f.write(json.dumps(j))
        f.close()

        print("Warning: SaveToJSON not fully implemented.")

    @staticmethod
    def ShyRetrieve(symbol, downloadAll=None):
        """
        Retrieve a Stock from CSV if available, else retrieve the Stock from yfinance API.
        
        Parameters:
            symbol: The symbol used to identify this Stock in exchange markets
            downloadAll (bool): Permission to download all missing Stocks from yfinance.

        Returns:
            A Stock pulled from local hard drive if available, pulled from yfinance API otherwise.
        """
        import os
        for file in os.listdir("Stocks"):
            if file == f"{symbol}.csv":
                print(f"Parsing {symbol} from local drive.")
                return Stock.ParseCSV("Stocks/" + file)

        def okayToDownload():
            if downloadAll != None:
                if downloadAll == True:
                    return True
                if downloadAll == False:
                    return False
            print(f"{symbol} not found in local drive. Okay to download from yfinance? (y/n)")
            response = input()
            if response.lower() == "y":
                return True
            elif response.lower() == "n":
                return False
            else:
                print("Please respond \"y\" or \"n\".")
                return okayToDownload()

        if okayToDownload():
            #stock = Stock.FromYfinance(symbol=symbol)
            stock = Stock(symbol=symbol)
            stock.Update()
            stock.SaveToCSV()
            print(f"{stock.name} downloaded from yfinance API.")
            return stock
        else:
            return Stock(symbol=symbol)

if __name__ == '__main__':
    symbols = [ 'SIG','WM', 'PEGI', 'F', 'PEIX', 'GPRE', 'FF', 'FTR', 'HOG', 'CECE', 'VOLVF', 'BIP',
               'PIN', 'SMHB', 'LVHI', 'TSLA', 'LXU', 'TEVA']
    stocks = []

    for symbol in symbols:
        stock = Stock.ShyRetrieve(symbol=symbol, downloadAll=False)
        if len(stock._history) > 0:
            stocks.append(stock)
            print(f"{stocks[-1].name} added to stocks array. \n{len(stocks)} stocks are in the array.")

    print("Plotting...")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.set_xlabel("Date")
    ax.set_ylabel("Dividend Yield (% / year)")

    for stock in stocks:
        if stock.history[-1].annualDividend / stock.history[-1].price < 0.05:
            continue
        print(f"Updating plot with data from {stock.name}...")
        dates = []
        #prices = []
        #dividends = []
        divYieldPercent = []
        for snapshot in stock.history:
            if snapshot.price == 0.0:
                continue
            dates.append(snapshot.date)
            #prices.append(snapshot.price)
            #dividends.append(snapshot.annualDividend)
            divYieldPercent.append(100. * snapshot.annualDividend / snapshot.price)
        ax.plot(dates, divYieldPercent, label=stock.symbol)
    ax.legend()
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
