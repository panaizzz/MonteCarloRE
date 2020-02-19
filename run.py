
'''This is an example code for a Monte Carlo Simulation. If you see any improvements (Which I have no doubt that there might be) then let me know'''
import logging
import threading
import queue
import numpy as np
import pandas as pd
from pandas_datareader import data as wb
import matplotlib.pyplot as plt
from scipy.stats import norm
from statistics import mean

def thread_function(name, data, iterations, period_days, plt, results):

    logging.info("Thread %s is starting" ,name)
    log_returns = np.log(1 + data.pct_change())
    u = log_returns.mean()
    var = log_returns.var()
    drift = u - (0.5 * var)
    stdev = log_returns.std()
    daily_returns = np.exp(drift.values + stdev.values * norm.ppf(np.random.rand(period_days, iterations)))
    S0 = data.iloc[-1]
    price_list = np.zeros_like(daily_returns)
    price_list[0] = S0

    for t in range(1, period_days):
        price_list[t] = price_list[t - 1] * daily_returns[t]

    # This line returns the mean of the last entries of all the lists
    #print(np.mean(price_list[-1]))
    plt.plot(price_list)
    #plt.show()

    results.put(np.mean(price_list[-1]))


def get_simulation(ticker, name):
    data = pd.DataFrame()
    data[ticker] = wb.DataReader(ticker, data_source='yahoo', start='2005-1-1')['Adj Close']


    # The next few lines are a plot mate with matplotlib.
    # The first number in the line below is how long the x-axis of the plot should be and the second number is the length of the Y-axis
    plt.figure(figsize=(10 ,6))
    # Below is the code to set the title of the plot. Name is derived from the input of the function
    plt.title("1 Year Monte Carlo Simulation for " + name)
    # The next two lines are the x and y label
    plt.ylabel("Price (P)")
    plt.xlabel("Time (Days)")
    # This is the line of code that actually plots every single list that we have
    threads = list()
    results=queue.Queue()
    for index in range(8):
        logging.info("Main    : create and start thread %d.", index)

        x = threading.Thread(target=thread_function, args=(index, data, 50000, 365, plt, results ))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)


    print(mean(list(results.queue)))
    plt.savefig('tempplot2.png')
    #plt.show()



companyname = input("What is the name of the company you are wanting to simulate? ")
ticker = input(f"What is the ticker of {companyname}? ")
get_simulation(ticker, companyname)
