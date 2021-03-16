import datetime
import numpy as np
from random import gauss
import math

# https://en.wikipedia.org/wiki/Normal_distribution, to get the bell curve
def normfun(x,mu,sigma):
    pdf = np.exp(-((x - mu)**2)/(2*sigma**2)) / (sigma * np.sqrt(2*np.pi))
    return pdf

def get_value(dt, mean, std):
    year, month, day, hour, minute = map(int, dt.strftime("%Y:%m:%d:%H:%M").split(":"))
    minute_of_day = hour * 60 + minute
    if dt.weekday() == 5 or dt.weekday() == 6:
        # lower values for weekends
        y = normfun(minute_of_day, mean, std) * 10000 + gauss(30, 5)
    else:
        y = normfun(minute_of_day, mean, std) * 100000 + gauss(30, 15)

    return y

#################### MAIN ####################

busyhour_start = "09:00"
busyhour_end = "17:00"

bs_h, bs_m = map(int, busyhour_start.split(":"))
be_h, be_m = map(int, busyhour_end.split(":"))

mean = ((be_h * 60 + be_m) - (bs_h * 60 + bs_m)) / 2 + (bs_h * 60 + bs_m)
std = ((be_h * 60 + be_m) - (bs_h * 60 + bs_m)) / 2 / 2

y = get_value(datetime.datetime.now(), mean, std)
result_handler["val01"] = [(0, math.floor(y + gauss(30, 15)))]
result_handler["val02"] = [(0, math.floor(y*2 + gauss(100, 50)))]
