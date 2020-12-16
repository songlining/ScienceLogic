import datetime
import numpy as np
from random import gauss
import math

# https://en.wikipedia.org/wiki/Normal_distribution, to get the bell curve
def normfun(x,mu,sigma):
    pdf = np.exp(-((x - mu)**2)/(2*sigma**2)) / (sigma * np.sqrt(2*np.pi))
    return pdf

# this function is for testing purpose, to generate a list of datetime points
def generate_datetime(start, end, interval):
    # sample start: 2019-01-01 10:00
    date, time = start.split()
    year, month, day = date.split("-")
    hour, minute = time.split(":")
    d1 = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))

    date, time = end.split()
    year, month, day = date.split("-")
    hour, minute = time.split(":")
    d2 = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    delta = datetime.timedelta(minutes=interval)
    times = []
    while d1 < d2:
        times.append(d1)
        d1 += delta
    times.append(d2)
    return times

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

# Set to True for plotting, False for production
TEST = False

if TEST is True:
    import matplotlib.pyplot as plt
    dt_list = generate_datetime("2019-01-01 00:00", "2019-01-14 00:00", 5)

busyhour_start = "09:00"
busyhour_end = "17:00"

bs_h, bs_m = map(int, busyhour_start.split(":"))
be_h, be_m = map(int, busyhour_end.split(":"))

mean = ((be_h * 60 + be_m) - (bs_h * 60 + bs_m)) / 2 + (bs_h * 60 + bs_m)
std = ((be_h * 60 + be_m) - (bs_h * 60 + bs_m)) / 2 / 2


if TEST is True:
    x_axis = []
    y1_axis = []
    y2_axis = []
    for dt in dt_list:
        year, month, day, hour, minute = map(int, dt.strftime("%Y:%m:%d:%H:%M").split(":"))
        minute_of_day = hour * 60 + minute
        x = day*24*60 + hour * 60 + minute
        y = get_value(dt, mean, std)
        x_axis.append(x)
        y1_axis.append(y + gauss(30, 15))
        y2_axis.append(y*2 + gauss(100, 50))

    # print(x_axis)
    # print(y_axis)
    plt.plot(x_axis, y1_axis)
    plt.show()

else:
    y = get_value(datetime.datetime.now(), mean, std)
    result_handler["val01"] = [(0, math.floor(y + gauss(30, 15)))]
    result_handler["val02"] = [(0, math.floor(y*2 + gauss(100, 50)))]
