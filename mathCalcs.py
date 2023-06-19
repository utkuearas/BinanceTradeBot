
import math
class taMath:

    def calcALMA(self,data,kwargs):

        if "window" in kwargs:
            window = kwargs["window"]
        else:
            window = 9

        if "offset" in kwargs:
            offset = kwargs["offset"]
        else:
            offset = .85
        
        if "sigma" in kwargs:
            sigma = kwargs["sigma"]
        else:
            sigma = 6

        data = data[len(data) - window:]

        m = offset * (window - 1)
        s = window / sigma

        summation = 0
        weights = 0

        for i in range(window):

            weight = math.exp(- pow(i - m,2) / (2 * pow(s,2)))
            element = weight * data[i]
            summation += element
            weights += weight

        return summation / weights

    def calcHMA(self,data,kwargs):

        if "window" in kwargs:
            window = kwargs["window"]
        else:
            window = 9

        requiredData = window + int(math.sqrt(window)) - 1
        data = data[len(data) - requiredData:]

        halfPeriod  = int(window/2) 
        sqrtPeriod = int(math.sqrt(window))

        fast = self.calcWMA(data , halfPeriod)

        fast = fast[len(fast) - sqrtPeriod:]
        
        slow = self.calcWMA(data , window)
        lastList = [2*i - slow[index] for index,i in enumerate(fast)]

        return self.calcWMA(lastList, sqrtPeriod)[0]

    def calcWMA(self,data, period):
        wma = []
        norm = period * (period + 1) / 2
        for i in range(len(data) - period + 1):
            chunk = data[i:i+period]
            summation = 0
            for u in range(period):
                summation += chunk[u] * (u + 1)
            wma.append(summation/norm)
        return wma
            



