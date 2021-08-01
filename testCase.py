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
    if response.replace('.','').isnumeric():
        return float(response)
    else:
        print("That is not a number.")
        return AskYears()

# Define the symbols we want to use for test cases
green   = ['FSLEX', 'ALTEX', 'NEXTX', 'GAAEX', 'NALFX', 'BEP', 'QCLN', 'ACES', 'ICLN', 'PBW', 'TAN', 'FAN', 'DRIV', 'SMOG', 'PDB', 'ERTH']
energy  = ['EPD', 'ENB', 'KMI', 'TOT', 'PSX', 'NEE']
utility = ['BCE', 'T', 'VOD', 'WM']
banks   = ['CM', 'BNS']
reits   = ['ABR', 'NHI', 'AGNC', 'KREF', 'MPW', 'ACRE', 'NLY']
etfs    = ['SSSS', 'IRCP', 'ELP', 'ORC', 'MBT', 'QIWI', 'GECC', 'FSK', 'FSKR', 'VIV', 'ARR', 'EFC', 'PRU']
crypto  = ['ETH-USD', 'BTC-USD', 'LTC-USD', 'ZEC-USD', 'ADA-USD', 'BCH-USD', 'XLM-USD', 'ETC-USD', 'DOGE-USD']
tech    = ['MSFT', 'AMZN', 'AAPL', 'NFLX', 'GOOG', 'SQ']

# Exclude the ones which don't perform as well so setup is faster.
exclude = ['PSX', 'T', 'VOD', 'IRCP', 'ELP', 'QIWI', 'GECC', 'FSKR', 'VIV', 'TRP', 'TEVA']

symbols = list((set(green) | set(energy) | set(utility) | set(banks) | set(reits) | set(etfs) | set(crypto) | set(tech)) - set(exclude))
    
top_five = ['MSFT', 'AMZN', 'NEE', 'BEP', 'ORC']
#symbols = list(set(top_five))

plot = False

# Import the class now since it will be used for all test cases
from Stocks import Stock
import datetime, math

class Score:
    ''' Structure to store scores of the different stock in test cases '''
    stock : Stock
    score : float
    def __init__(self, stock:Stock, score:float):
        self.stock = stock
        self.score = score

def TestCaseWithFit():
    from AprFit import AprFit
    from winsound import Beep
    
    # Pull the stock data into memory.
    stocks = []
    for symbol in symbols:
        stock = Stock.ShyRetrieve(symbol=symbol, minDate=(datetime.datetime.now() - datetime.timedelta(days=5)))
        if len(stock._history) > 0:
            stocks.append(stock)
    
    Beep(300, 500) # Let the user know it's done importingscore.symbol

    today = datetime.datetime.now()

    # In a loop so data stays in memory if the user wants to change parameters.
    while True:
        yearsToConsider = AskYears()
        minimumYield = AskMinYield()
        if yearsToConsider == "break":
            break
        if minimumYield == "break":
            break
        scores = []

        startDate = today - datetime.timedelta(seconds = 366 * yearsToConsider * 60 * 60 * 24)

        for stock in stocks:
            if stock.history[0].date > startDate:
                continue
                # Only plot stocks which have enough history.

            try:
                apr_fit = stock.get_apr_fit(years=yearsToConsider)
            except:
                # Looks like I need to do some sanitizing of the data from yFinance. BEP hits a math domain error here and previously gave strange results in other tests.
                print(f"Failed to fit curve onto data from {stock.symbol}")
                continue

            # Determine how much this stock is currently overvalued/undervalued
            total_dividends_since_t_0 = 0.
            index = len(stock.history) - 1
            while (stock.history[index].date - today).total_seconds() >= apr_fit.t_0 * 31557600.:
                total_dividends_since_t_0 += stock.history[index].dividend
                if index == 0:
                    break
                index -= 1
            undervalue = apr_fit.y_0 * (1 + apr_fit.rate) ** (0. - apr_fit.t_0) - (stock.history[-1].price + total_dividends_since_t_0)
            undervalue /= stock.history[-1].price + total_dividends_since_t_0

            N_STDEVS = 2. # Number of standard deviations to use for fitness
            if apr_fit.stdev * N_STDEVS > 1.:
                score = Score(stock, 0.)
            else:
                score = Score(stock, 100. * (apr_fit.rate + undervalue / 8.) * (1. - N_STDEVS * apr_fit.stdev) - apr_fit.stdev * N_STDEVS)
                # stdev applies as both uncertainty in the fit and as potential loss

            # Bias towards green investments
            if stock.symbol in green:
                score.score *= 1.25

            # Attach metadata to the score so I can print it.
            score.rate        = 100. * apr_fit.rate
            score.undervalue  = 100. * undervalue
            score.uncertainty = 100. * apr_fit.stdev
            scores.append(score)

        scores.sort(key=lambda x:x.score)
        scores.reverse()

        # Recommend how much would have been good to allocated to each
        number_of_recommendations = 0
        sum = 0
        for candidate in scores:
            if math.isnan(candidate.score):
                continue
            if candidate.score <= 0.:
                continue
            sum += candidate.score
            if candidate.score / sum < 0.05:
                sum -= candidate.score
                break
            number_of_recommendations += 1
        print("Recommended distribution:")
        recommendations = []
        for i in range(number_of_recommendations):
            stock = scores[i].stock
            recommended_percent = 100 * scores[i].score / sum
            print(f"{recommended_percent:.2f}% in {stock.symbol}    Score: {scores[i].score:.2f}    <APR>: {scores[i].rate:.2f}    undervalued by {scores[i].undervalue:.2f}%    uncertainty: {scores[i].uncertainty:.2f}%")

            if plot:
                stock.get_apr_fit(years=yearsToConsider, plot=True)

        Beep(300, 500)

def OriginalTestCase():

    # Import the modules now so it will crash before doing work if a module is missing.
    import matplotlib.pyplot as plt
    from dateutil.parser import parse

    # Pull the stock data into memory.
    stocks = []
    for symbol in symbols:
        stock = Stock.ShyRetrieve(symbol=symbol, minDate=(datetime.datetime.now() - datetime.timedelta(days=5)))
        if len(stock._history) > 0:
            stocks.append(stock)

    today = datetime.datetime.now()

    # Let the user know import is complete
    import winsound
    winsound.Beep(600, 100)

    # In a loop so data stays in memory if the user wants to change parameters.
    while True:
        yearsToConsider = AskYears()
        minimumYield = AskMinYield()
        if yearsToConsider == "break":
            break
        if minimumYield == "break":
            break

        startDate = today - datetime.timedelta(days = 365 * yearsToConsider)

        if plot:
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

        annual_yields = []
        scores        = []

        for stock in stocks:
            if stock.history[0].date > startDate:
                continue
                # Only plot stocks which have enough history.

            filteredGrowth, growthUncertainty = stock.GrowthAPRWithUncertainty(yearsToConsider)
            dividendYield = stock.AverageDividendPercent(yearsToConsider)
            dividendUncertainty = stock.DividendPercentUncertainty(yearsToConsider)
            if dividendUncertainty > dividendYield:
                dividendUncertainty = dividendYield # Never apply a penalty for dividends
            annualYield = dividendYield + filteredGrowth
            if annualYield < minimumYield:
                continue
                # Only plot stocks with combined margin better than 10% per year over the past 10 years.
            print(f"{stock.symbol} {annualYield:.1f} ± {growthUncertainty + dividendUncertainty:.1f}% average annual yield over the past {yearsToConsider} years.")
            print(f"{filteredGrowth:.2f}% from growth and {stock.AverageDividendPercent(yearsToConsider):.2f}% from dividends.")
            annual_yields.append((stock.symbol, annualYield))

            score = annualYield - 0.431 * (growthUncertainty + dividendUncertainty) # 33rd percentile
            scores.append((stock.symbol, score))

            if plot:
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
                        print("You may not want to trust this data...")
                    if divYieldPercent[-1] > max_dividend:
                        max_dividend = divYieldPercent[-1]
                    elif divYieldPercent[-1] < min_dividend:
                        min_dividend = divYieldPercent[-1]

                dividend_plot.plot(dates, divYieldPercent, label=stock.symbol)
                #growth_plot.plot(dates, relGrowth, label=stock.symbol)

            annualYield = []
            yDates      = []
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
            if plot:
                total_yield_plot.plot(yDates, annualYield, label=stock.symbol)
                
        annual_yields.sort(key=lambda x:x[1])
        annual_yields.reverse()
        scores.sort(key=lambda x:x[1])
        scores.reverse()

        # Recommend how much would have been good to allocated to each
        number_of_recommendations = 0
        sum = 0
        for candidate in scores:
            if not math.isnan(candidate[1]):
                sum += candidate[1]
            if sum > 0.:
                if candidate[1] / sum < 0.05:
                    sum -= candidate[1]
                    break
            if sum < 0.:
                sum -= candidate[1]
                break
            number_of_recommendations += 1
        print("Recommended distribution:")
        recommendations = []
        for i in range(number_of_recommendations):
            symbol = scores[i][0]
            recommended_percent = 100 * scores[i][1] / sum
            recommendations.append((symbol, recommended_percent))
            print(f"{recommended_percent:.2f}% in {symbol}    Score: {scores[i][1]:.2f}")

        winsound.Beep(300, 500)

        if plot:
            fig.tight_layout()
            fig.autofmt_xdate()

            #growth_plot.plot([parse("1/1/2000"), today], [0, 0], label='Zero')
            total_yield_plot.plot([parse("1/1/2000"), today], [0, 0], label='Zero')

            dividend_plot.set_ylim(bottom=min_dividend, top=max_dividend)
            #growth_plot.set_ylim(bottom=min_growth, top=max_growth)
            total_yield_plot.set_ylim(bottom=min_total, top=max_total)

            dividend_plot.tick_params(labelleft=True, left=True, right=True, bottom=True)
            #growth_plot.tick_params(labelleft=True, left=True, right=True, bottom=True)
            total_yield_plot.tick_params(labelleft=True, left=True, right=True, bottom=True, labelbottom=True)

            dividend_plot.legend()
            #growth_plot.legend()
            #total_yield_plot.legend()
            plt.show()

if __name__ == "__main__":
    TestCaseWithFit()