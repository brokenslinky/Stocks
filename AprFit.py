class AprFit:
    '''
    Estimate and store an exponential curve of the for y = y_0 * (1 + R) ^ (t - t_0)

    Members:
        rate:  The effective increase in y per unit of time t (APR if t is in units of years)
        t_0:   The basis time. Adjusted to reduce standard deviation of the fit.
        y_0:   The value of at t_0
        stdev: The relative uncertainty of estimates provided by the fit curve
    '''

    import datetime
    rate:  float
    t_0:   float
    y_0:   float
    stdev: float
    
    def __init__(self, t: list, y: list):
        if len(t) != len(y):
            raise Exception("t and y lists must be the same length.")

        import math

        def calculate_rate_and_stdev(t_0:float, y_0:float):
            # Calculate the rate by least-squares method
            sum_dtlny      = 0.
            sum_dt         = 0.
            sum_dt_squared = 0.
            for index in range(len(t)):
                sum_dtlny      += (t[index] - t_0) * math.log(y[index])
                sum_dt         += (t[index] - t_0)
                sum_dt_squared += (t[index] - t_0) * (t[index] - t_0)
            rate = math.exp((sum_dtlny - math.log(y_0) * sum_dt) / sum_dt_squared) - 1.

            # Measure the standard deviation of this fit to the provided data
            stdev = 0.
            for index in range(len(t)):
                stdev += ((y_0 * (1 + rate) ** (t[index] - t_0) - y[index]) ** 2) / (y[index] ** 2)
            stdev /= len(t) - 1.
            stdev = math.sqrt(stdev)

            return rate, stdev

        best_zero_index       = len(t) - 1
        best_rate, best_stdev = calculate_rate_and_stdev(t_0=t[best_zero_index], y_0=y[best_zero_index])

        number_of_steps = 16
        for step in range(number_of_steps):
            tmp_index = int(len(t) * step / number_of_steps)
            tmp_rate, tmp_stdev = calculate_rate_and_stdev(t_0=t[tmp_index], y_0=y[tmp_index])
            if tmp_stdev < best_stdev:
                best_zero_index = tmp_index
                best_rate       = tmp_rate
                best_stdev      = tmp_stdev

        self.rate  = best_rate
        self.t_0   = t[best_zero_index]
        self.y_0   = y[best_zero_index]
        self.stdev = best_stdev

    def plot(self, t:list, y:list):
        import matplotlib.pyplot as plt
        assert(len(t) == len(y))
        plt.plot(t, y)
        fit_y = []
        for t_i in t:
            fit_y.append(self.y_0 * (1 + self.rate) ** (t_i - self.t_0))
        plt.plot(t, fit_y)
        plt.show()