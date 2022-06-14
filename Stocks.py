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
    def history(self, history):
        """Set the history of this Stock."""
        self._history = history

    @property
    def pe_ratio(self):
        """The latest business revenue per total market cap"""
        if self._pe_ratio == None:
            return float('inf')
        return self._pe_ratio
    @pe_ratio.setter
    def pe_ratio(self, pe_ratio):
        """Set the revenue per market cap."""
        self._pe_ratio = pe_ratio

    @property
    def short_percent_of_float(self):
        """The latest short position as a percent of float"""
        if self._short_percent_of_float == None:
            return 0.
        return self._short_percent_of_float
    @short_percent_of_float.setter
    def short_percent_of_float(self, short_percent_of_float):
        """Set the short percent of float"""
        self._short_percent_of_float = short_percent_of_float

    class Snapshot:
        """
        A snapshot of the Stock at a single moment in time.

        Members:
            price (USD): The cost of one unit of Stock at this time.
            date: The timestamp for this Snapshot.
            dividend (USD): The dividend paid on this day.
            annualDividend (USD/year): The total dividends paid in one year.
        """
        import datetime
        price          : float
        date           : datetime.datetime
        dividend       : float
        annualDividend : float

        def __init__(self, price, date=datetime.datetime.now(), dividend=0., annualDividend=0.):
            """
            Create a new Stock Snapshot

            Parameters:
                price (USD): The cost of one unit of Stock at this time.
                date: The timestamp for this Snapshot.
                dividend (USD): The dividend paid on this day
                annualDividend (USD/year): The total dividends paid in one year.
            """
            self.price          = price
            self.date           = date
            self.dividend       = dividend
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
        
    def AddSnapshot(self, price, date=datetime.datetime.now(), dividend=0., annualDividend=0.):
        """
        Add a Snapshot to the Stock's history.

        Parameters:
            price (USD): The cost of one unit of Stock at this time.
            date: The timestamp for this Snapshot.
            annualDividend (USD/year): The total dividends paid in one year.
        """
        self._AddSnapshot(self.Snapshot(price=price, date=date, dividend=dividend, annualDividend=annualDividend))
        
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
        if (self.name == None or self.name == self.symbol) and stock.info is not None:
            if "shortName" in stock.info:
                self.name = stock.info['shortName']
        yhistory = stock.history(period="max")
        print(yhistory)

        dividends = []
        for date, row in yhistory.iterrows():
            dividend_today = row['Dividends']
            dividends.append((date, dividend_today))
            if dividend_today != 0.:
                while date - dividends[0][0] > datetime.timedelta(days=360):
                    dividends.remove(dividends[0])
            else:
                while date - dividends[0][0] > datetime.timedelta(days=370):
                    dividends.remove(dividends[0])

            annualDividend = 0.
            for dividend in dividends:
                annualDividend += dividend[1]
                
            self.AddSnapshot(price=row['Open'], date=date, dividend=dividend_today, annualDividend=annualDividend)
            #self.AddSnapshot(price=row['Close'], date=date, annualDividend=annualDividend)

        try:
            self.short_percent_of_float = stock.info['shortPercentOfFloat']
        except(KeyError):
            self.short_percent_of_float = 0.
        try:
            self.pe_ratio = stock.info['forwardPE']
        except(KeyError, TypeError):
            self.pe_ratio = float('inf')

        print(f"History for {self.name} updated.")

    def GetInfo(self):
        """ Retrieve the stock info from yFinance API """
        import yfinance as yf
        return yf.Ticker(self._symbol).get_info()

    def AverageDividendPercent(self, years=10):
        """
        The average dividend yield over the specified period

        Parameters:
            years: The number of years into the past to average over.

        Returns:
            The average dividend yield percentage over the specified period
        """
        nSamples = 0
        dividendSum = 0.
        import datetime
        import math
        now = datetime.datetime.now()
        for index in range(len(self._history)):
            snapshot = self._history[-1 - index]
            if now - snapshot.date > datetime.timedelta(days=365*years):
                break
            nSamples += 1
            if not math.isnan(snapshot.annualDividend / snapshot.price):
                dividendSum += snapshot.annualDividend / snapshot.price
        if nSamples == 0:
            return 0.
        avgDiv = 100. * dividendSum / nSamples
        if math.isnan(avgDiv):
            return 0
        return avgDiv

    def DividendPercentUncertainty(self, years=10):
        '''
        The uncertainty in dividend yield over the specified period

        Parameters:
            years: The number of years into the past to average over.

        Returns:
            The average dividend yield percentage over the specified period
        '''
        average_dividend = self.AverageDividendPercent(years)
        nSamples = 0
        uncertainty = 0.
        import datetime
        import math
        now = datetime.datetime.now()
        for index in range(len(self._history)):
            snapshot = self._history[-1 - index]
            if now - snapshot.date > datetime.timedelta(days=365*years):
                break
            nSamples += 1
            if not math.isnan(snapshot.annualDividend / snapshot.price):
                uncertainty += (snapshot.annualDividend / snapshot.price - average_dividend) ** 2
        if nSamples == 0:
            return average_dividend
        uncertainty /= nSamples - 1.
        uncertainty = math.sqrt(uncertainty)
        if math.isnan(uncertainty):
            return average_dividend
        return uncertainty

    def GrowthPercent(self, years=10):
        """
        The total growth over the specified period

        Parameters:
            year: The number of years into the past to compare against.

        Returns:
            The total growth over the specified period in percent.
        """
        pastPrice = 0.
        import datetime
        today = datetime.datetime.now()
        for index in range(0, len(self.history) - 1):
            if today - self.history[index].date < datetime.timedelta(days=365*years):
                pastPrice = self.history[index].price
                break
        if pastPrice == 0.:
            return 0.
        return 100. * (self.history[-1].price - lastYear) / lastYear

    def GrowthAPR(self, years=10):
        """
        The growth over the specified period expressed as APR.

        Parameters:
            year: The number of years into the past to compare against.

        Returns:
            The effective APR over the specified period in percent.
        """
        pastPrice = self.history[-1].price
        import datetime
        today = datetime.datetime.now()
        pastDate = self.history[-1].date
        # TODO: This is an inefficient way to look up a specific date
        for index in range(0, len(self.history) - 1):
            if today - self.history[index].date < datetime.timedelta(days=365.25*years):
                # Assuming the stock data is in chronological order, the first result more recent than X years
                # is a good enough approximation
                pastPrice = self.history[index].price
                pastDate = self.history[index].date
                break
        if pastPrice == 0.:
            return 0.
        n_years = (self.history[-1].date - pastDate).days / 365.25
        if n_years == 0.:
            return 0.
        return 100. * (self.history[-1].price / pastPrice) ** (1. / n_years) - 100.

    def GrowthAPRWithUncertainty(self, years=10):
        """
        The growth over the specified period expressed as APR.

        Parameters:
            year: The number of years into the past to compare against.

        Returns:
            Tuple: The effective APR over the specified period, and associated uncertainy. Both in percent.
        """
        import math, datetime

        average_annual = self.GrowthAPR(years) / 100.
        average_daily = math.pow(1 + average_annual, 1 / 365) - 1.
        
        i = 0
        today = datetime.datetime.now()
        while i < len(self.history):
            if today - self.history[i].date < datetime.timedelta(days=365.25*years):
                break
            i += 1
        uncertainty = 0.
        filter_days = 20
        n_samples = 0
        while i < len(self.history):
            today = self.history[i].price
            previous = self.history[i - 1].price
            change = (today - previous) / previous
            uncertainty += ((1. + change) ** (1 / filter_days) - (1. + average_daily)) ** 2
            n_samples += 1
            i += filter_days
        uncertainty /= n_samples - 1.
        uncertainty = math.sqrt(uncertainty)
        uncertainty *= 365.25 * (1. + average_annual)

        return (100. * average_annual, 100. * uncertainty)

    def get_apr_fit(self, years=10., plot=False):
        '''
        Get a curve fitted to the data with the form y = y_0 * (1 + rate) ^ t where "t" is the number of years from today
        '''
        import AprFit, datetime
        t               = []
        y               = []
        total_dividends = 0.
        today = datetime.datetime.now()
        i = 0
        while i < len(self.history):
            if today - self.history[i].date < datetime.timedelta(days=365.25*years):
                break
            i += 1
        while i < len(self.history):
            total_dividends += self.history[i].dividend
            t.append((self.history[i].date - today).total_seconds() / 31557600.)
            y.append(self.history[i].price + total_dividends)
            i += 1
        apr_fit = AprFit.AprFit(t, y)
        if plot:
            apr_fit.plot(t, y)
        return apr_fit

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
        csvfile = open(f"Cache/{self.symbol}.csv", "w", newline='')
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow([self.symbol, self.name, self.market])
        writer.writerow(['Latest P/E Ratio:', self.pe_ratio])
        writer.writerow(['Short Percent of Float:', self.short_percent_of_float])
        writer.writerow(['Date', 'Price', 'Dividend', 'Annualized Dividend'])
        for snapshot in self._history:
            writer.writerow([snapshot.date.strftime("%m/%d/%Y"), snapshot.price, snapshot.dividend, snapshot.annualDividend])
        csvfile.close()
        print(f"{self.name} saved to /Cache/{self.symbol}.csv")

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
        stock = Stock(symbol=None)

        rowNum = 0
        from dateutil.parser import parse, _parser
        for row in reader:
            if rowNum == 0:
                stock.symbol = row[0]
                stock.name = row[1]
                stock.market = row[2]
            elif row[0] == 'Latest P/E Ratio:':
                try:
                    stock.pe_ratio = float(row[1])
                    if stock.pe_ratio == 0.:
                        stock.pe_ratio = float('inf')
                except(ValueError):
                    stock.pe_ratio = float('inf')
            elif row[0] == 'Short Percent of Float:':
                try:
                    stock.short_percent_of_float = float(row[1])
                except(ValueError):
                    stock.short_percent_of_float = 0.
            elif row[0] != 'Date':
                # Skip the header row
                try:
                    stock.AddSnapshot(price=float(row[1]), date=parse(row[0]), dividend=float(row[2]), annualDividend=float(row[3]))
                except(_parser.ParserError):
                    print(f"WARNING: Un-parsed row in {stock.symbol}: {row[0]}")
            rowNum += 1

        csvfile.close()
        return stock
    
    def SaveToJSON(self):
        """
        !NOT IMPLEMENTED! 
        Save this stock to a JSON file.
        """
        import json

        f = open(f"/Cache/{self.symbol}.JSON", "w")
        j = {"name": self.name, "symbol": self.symbol}

        f.write("{\"name\":\"" + str(self.name) + "\", ")
        f.write(json.dumps(j))
        f.close()

        print("Warning: SaveToJSON not fully implemented.")

    @staticmethod
    def ShyRetrieve(symbol, minDate=None, downloadMissing=None):
        """
        Retrieve a Stock from CSV if available, else retrieve the Stock from yfinance API.
        
        Parameters:
            symbol: The symbol used to identify this Stock in exchange markets
            minDate (datetime): Downloads fresh data from yfinance if cached data is older than this date.
            downloadMissing (bool): Permission to download all missing Stocks from yfinance.

        Returns:
            A Stock pulled from local hard drive if available, pulled from yfinance API otherwise.
        """
        import os
        for file in os.listdir("Cache"):
            if file == f"{symbol}.csv":
                print(f"Parsing {symbol} from local drive.")
                stock = Stock.ParseCSV("Cache/" + file)
                if len(stock.history) != 0 and (minDate == None or stock.history[-1].date >= minDate):
                    return stock

        def okayToDownload():
            if minDate != None:
                return True
            if downloadMissing != None:
                return downloadMissing
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
    from testCase import OriginalTestCase, TestCaseWithFit
    TestCaseWithFit()
    #OriginalTestCase()