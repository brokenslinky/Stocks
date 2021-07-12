class AprFit:
    '''
    Estimate and store an exponential curve of the for y = y_0 * (1 + R) ^ (t - t_0)

    Members:
        rate:  The effective increase in y per unit of time t (APR if t is in units of years)
        t_0:   The y-averaged time of provided data (t_0 = sum(y * t) / sum(y)
        y_0:   The value of y at t_0
        stdev: The relative uncertainty of estimates provided by the fit line
    '''

    import datetime
    rate:        float
    t_0:         float
    y_0:         float
    uncertainty: float
    
    def __init__(self, t: list, y: list):
        if len(t) != len(y):
            raise Exception("t and y lists must be the same length.")

        # Calculate t_0 (The y-averaged time of provided data)
        sum_yt = 0.
        sum_y  = 0.
        for index in range(len(t)):
            sum_yt += y[index] * t[index]
            sum_y  += y[index]
        self.t_0 = sum_yt / sum_y

        # Interpolate the y value at t_0
        last_t = t[0]
        last_y = y[0]
        self.y_0 = 0.
        for index in range(len(t)):
            if t[index] == self.t_0:
                self.y_0 = y[index]
                break
            if t[index] > self.t_0:
                self.y_0 = last_y + (self.t_0 - last_t) * (y[index] - last_y) / (t[index] - last_t)
                break
            last_t = t[index]
            last_y = y[index]

        # Calculate the rate by least-squares method
        import math
        sum_dtlny      = 0.
        sum_dt         = 0.
        sum_dt_squared = 0.
        for index in range(len(t)):
            sum_dtlny      += (t[index] - self.t_0) * math.log(y[index])
            sum_dt         += (t[index] - self.t_0)
            sum_dt_squared += (t[index] - self.t_0) * (t[index] - self.t_0)
        self.rate = math.exp((sum_dtlny - math.log(self.y_0) * sum_dt) / sum_dt_squared) - 1.

        # Measure the standard deviation of this fit to the provided data
        self.stdev = 0.
        for index in range(len(t)):
            self.stdev += ((self.y_0 * (1 + self.rate) ** (t[index] - self.t_0) - y[index]) ** 2) / (y[index] ** 2)
        self.stdev /= len(t) - 1.
        self.stdev = math.sqrt(self.stdev)

    def plot(self, t:list, y:list):
        import matplotlib.pyplot as plt
        assert(len(t) == len(y))
        plt.plot(t, y)
        fit_y = []
        for t_i in t:
            fit_y.append(self.y_0 * (1 + self.rate) ** (t_i - self.t_0))
        plt.plot(t, fit_y)
        plt.show()