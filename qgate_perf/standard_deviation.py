from math import sqrt


class StandardDeviation:
    """
    Welford's alg for incrementally calculation of standard deviation

    NOTE: You can see the same outputs as in functions 'STDEVPA' and 'STDEV.P' in Microsoft Excel
    """

    def __init__(self, ddof = 1):
        self.ddof, self.n, self.mean, self.M2 = ddof, 0, 0.0, 0.0

    def include(self, data):
        self.n += 1
        self.delta = data - self.mean
        self.mean += self.delta / self.n
        self.M2 += self.delta * (data - self.mean)

    @property
    def variance(self):
        return self.M2 / (self.n - self.ddof) if self.n > 0 else 0

    @property
    def std(self):
        """ Standard deviation """
        return sqrt(self.variance)
