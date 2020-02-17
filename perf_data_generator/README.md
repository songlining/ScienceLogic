# Description

This is a Dynamic App script that can be used to generate psudo data to simulate business transactions during weekdays (high volume) and weekends (low volume).

The bell curve shape is generated using [Standard Normal Distribution function](https://en.wikipedia.org/wiki/Normal_distribution).

The script can be run locally by setting "TEST = True", matplotlib has to be installed.

To use with SL1, manually create a virtual device and align this DA to it, run it every 5 or 10 mins depending on your settings. You can also change the object name of the output to simulate any metrics you want to name.

Here's a [sample image](./curve_sample.png) when plotting locally.
