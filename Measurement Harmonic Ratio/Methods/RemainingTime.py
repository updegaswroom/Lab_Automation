import time

class timer():
    def __init__(self, *args):
        self.startTime = 0
        self.elapsedTime = 0
        self.averageTime = 0
        self.numIterations = 0
        self.remainingTime = 0

    def setStartTime(self, numIterations):
        self.numIterations = numIterations
        self.startTime = time.time()

    def getRemainingTime(self, currIteration):
        self.elapsedTime = time.time() - self.startTime
        self.averageTime = self.elapsedTime/(currIteration+1) 
        return (self.numIterations - currIteration+1)*self.averageTime
    
    def getRemainingTimeHoursMins(self, currIteration):

        self.elapsedTime = time.time() - self.startTime
        self.averageTime = self.elapsedTime/(currIteration+1) 
        self.remainingTime = (self.numIterations - currIteration+1)*self.averageTime
        Hours = int(self.remainingTime // 3600)
        Mins = int((self.remainingTime // 60)%60)
        return Hours, Mins