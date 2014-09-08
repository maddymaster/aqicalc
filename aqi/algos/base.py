# -*- coding: utf-8 -*-

from decimal import *


class BaseAQI(object):
    """
    A generic AQI class
    """

    def iaqi(self, elem, cc):
        """Calculate an intermediate AQI for a given pollutant. This is
        the heart of the algo.

        .. warning:: the concentration is passed as a string so
        :class:`decimal.Decimal` doesn't act up with binary floats.

        :param elem: pollutant constant
        :type elem: int
        :param cc: pollutant contentration (µg/m³ or ppm)
        :type cc: str
        """
        raise NotImplementedError

    def aqi(self, ccs):
        """Calculate the AQI based on a list of pollutants

        :param ccs: a list of tuples of pollutants concentrations with
                    pollutant constant and concentration as values
        :type ccs: list
        """
        iaqis = []
        for (elem, cc) in ccs:
            iaqis.append(self.iaqi(elem, cc))
        return max(iaqis)


class PiecewiseAQI(BaseAQI):
    """
    A piecewise function AQI class (like EPA or MEP)
    """

    piecewise = None

    def iaqi(self, elem, cc):
        if self.piecewise is None:
            raise NameError("piecewise_struct is not defined")

        #getcontext().rounding = ROUND_DOWN
        _cc = Decimal(cc).quantize(self.piecewise['prec'][elem],
                                   rounding=ROUND_DOWN)

        # define breakpoints for this pollutant at this contentration
        bps = self.piecewise['bp'][elem]
        bplo = None
        bphi = None
        idx = 0
        for bp in bps:
            if _cc >= bp[0] and _cc <= bp[1]:
                bplo = bp[0]
                bphi = bp[1]
                break
            idx += 1
        # get corresponding AQI boundaries
        (aqilo, aqihi) = self.piecewise['aqi'][idx]

        # equation
        value = (aqihi - aqilo) / (bphi - bplo) * (_cc - bplo) + aqilo
        return value.quantize(Decimal('1.'), rounding=ROUND_HALF_EVEN)
