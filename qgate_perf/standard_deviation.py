import math


class StandardDeviation:
    """
    Welford's alg for incrementally calculation of standard deviation
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
        return self.M2 / (self.n - self.ddof)

    @property
    def std(self):
        """ Standard deviation """
        return math.sqrt(self.variance)
