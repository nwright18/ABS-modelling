"""Timer class"""

from time import time
import logging
from functools import wraps

class Timer(object):

    _warnThreshold = 60
    _warnDict = {0 : _warnThreshold, 1 : (_warnThreshold/60), 2 : (_warnThreshold/3600)}

    def __init__(self, config = 'seconds'):

        #Treshold for warning (in seconds)

        self._start_time = 0.0
        self._end_time = 0.0
        self._time_taken = 0.0
        self._config = 0  #0,1,2 if config sec,min,hours respectively
        if config in ['seconds','minutes','hours']:  #checks and stores config selection
            self.setConfig(config)
        else:
            logging.info(f'{config} is not a valid configuration. Please select : seconds, minutes or hours.')

    def start(self): #starts the timer, notifies if timer already running
        if self._start_time == 0.0:
            self._start_time = time()
        else:
            logging.info('Timer already running')

    def end(self): #ends the timer and prints the result, notifies if timer has not yet started
        if self._start_time != 0.0:
            self._end_time = time()
            self._time_taken = (self._end_time - self._start_time)/(60**self._config)
            logFunc = logging.info if self._time_taken < Timer._warnDict.get(self._config) else logging.warning
            logFunc(f' Time Taken : {self._time_taken:.7f}')
            self.reset() #resets the timer start and end values
        else:
            logging.info('Timer has not started yet')

    def retrieveLastResult(self): #returns the previous value of time taken
        return self._time_taken

    def reset(self): #resets the timer
        self._start_time = 0.0
        self._end_time = 0.0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self,type,value,traceback):
        self.end()

    def setConfig(self,config): #sets output config to sec, mins, hours and converts the time taken accordingly
        configDict = {'seconds': 0, 'minutes': 1, 'hours': 2}
        newconfig = configDict.get(config,'seconds')
        if newconfig == None:
            logging.info(f'{config} is not a valid configuration. Please select : seconds, minutes or hours.')
        else:
            self._time_taken *= 60 ** (self._config - newconfig)
            self._config = newconfig

def Time(func): #timer decorator
    timer = Timer()
    @wraps(func)
    def wrapped(*args,**kwargs):
        timer.start()
        result = func(*args,**kwargs)
        timer.end()
        return result
    return wrapped