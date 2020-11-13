#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import ordinal_TSA
import scipy.stats as stats
import pandas as pd
import time
import progressbar
np.random.seed(0)

def plot_dual(x1, y1, x2, y2, labels):
    '''
    plots two data sets on the twin y axes. the axes are returned
    so that the user can add labels, legends, etc.
    '''
    if len(x1) != len(y1) or len(x2) != len(y2):
        raise ValueError('make sure the x and y arrays have the same length for both \
                          data sets.')
    if len(labels) != 2:
        raise ValueError('make sure your labels list is length 2')
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(x1, y1, 'g', alpha=.5, label=labels[0])
    ax1.plot(np.nan, 'b', label=labels[1])
    ax2.plot(x2, y2, 'b', alpha=.5)
    ax1.legend(loc=1)
    return ax1, ax2

def calculate_pe(age_array, data_array, tau, weight, window, dimension=4):
    '''
    calculates permuatation entropy of a time series based on a set of input
    parameters. returns the age and entropy arrays.
    '''
    if len(age_array) != len(data_array):
        raise ValueError('age and data array must be same length')
    if weight != 0 and weight != 1:
        raise ValueError('weight must be 0 (unweighted) or 1 (weighted)')
    if window > len(age_array):
        raise ValueError('window must be smaller than length of time series')
    TS = np.asarray(data_array)
    TS = np.reshape(TS, (len(TS), 1))
    result = ordinal_TSA.windowed_permutation_entropy(data=TS,
                                                      window_size=window-2-3*(tau-1),
                                                      dim=dimension,
                                                      max_window_size=window-2-3*(tau-1),
                                                      step=tau,w=weight)
    return np.asarray(age_array[window:]), np.asarray(result)

def rolling_average(age_array, data_array, window):
    '''
    simple moving average.
    '''
    if len(age_array) != len(data_array):
        raise ValueError('age and data array must be same length')
    if window > len(age_array):
        raise ValueError('window must be smaller than length of time series')
    result = np.cumsum(np.asarray(data_array), dtype=float)
    result[window:] = result[window:] - result[:-window]
    return age_array[window-1:], result[window -1:] / window

def plot_correlation(x, y):
    '''
    plots x vs y, and calculates the r-squared values as well as the line of
    best fit.
    '''
    if len(x) != len(y):
        raise ValueError('make sure x and y are same length')
    f, ax = plt.subplots()
    ax.plot(x, y, 'r.', alpha=.4)
    slope, intercept, r_value, p_value_, std_err = stats.linregress(x, y)
    ax.annotate('r-squared: {:.3f}'.format(r_value**2), xy=(1, 0),
                xycoords='axes fraction', fontsize=16,
                xytext=(-5, 5), textcoords='offset points',
                ha='right', va='bottom',
                bbox={'facecolor':'black', 'alpha':0.3, 'pad':5})
    ax.plot(x, np.asarray(x)*slope + intercept, c='k', alpha=1, label='line of best fit')
    ax.legend()
    return ax

def binned_average(age_array, data_array, bin_size):
    '''
    a dimension reduction tool that takes a binned average of data and age.
    '''
    if bin_size > len(age_array):
        raise ValueError('bin size can not excede length of data')
    if len(age_array) != len(data_array):
        raise ValueError('age and data array must be same length')
    n = bin_size
    num_bins = len(age_array) // bin_size
    average_age, average_data = [], []
    for i in range(num_bins):
        average_age.append(np.asarray(age_array[n*i : n*(i+1)]).mean())
        average_data.append(np.asarray(data_array[n*i : n*(i+1)]).mean())
    return np.asarray(average_age), np.asarray(average_data)

def binned_midpoint(age_array, data_array, bin_size):
    '''
    a dimension reduction tool that takes a binned midpoint of data and age.
    '''
    if bin_size > len(age_array):
        raise ValueError('bin size can not excede length of data')
    if len(age_array) != len(data_array):
        raise ValueError('age and data array must be same length')
    n = bin_size
    num_bins = len(age_array) // bin_size
    midpoint_age, midpoint_data = [], []
    for i in range(num_bins):
        if bin_size % 2 == 1:
            midpoint_age.append(age_array[n*i+(bin_size+1)/2])
            midpoint_data.append(data_array[n*i+(bin_size+1)/2])
        else:
            m_1 = n*i+(bin_size)/2
            midpoint_age.append(np.mean([age_array[m_1], age_array[m_1+1]]))
            midpoint_data.append(np.mean([data_array[m_1], data_array[m_1+1]]))

    return np.asarray(midpoint_age), np.asarray(midpoint_data)

def calculate_pe_python(age, ts, tau, word_length, window):
    '''
    a custom implementation of the PE calculation
    '''
    if len(age) != len(ts):
        raise ValueError('make sure the age and time series are the same length')
    if window > len(age):
        raise ValueError('window can not be larger than the time series')

    num_windows = len(age) - window + 1
    ordinals_per_window = window - tau*word_length + 1

    result = []
    pmf = {}
    # finding initial pmf --- from here on out can just change one value at a time
    for j in range(ordinals_per_window):
        current = ts[j:j+word_length*tau:tau]
        current_ordinal = sort_ordinal(current)
        try:
            pmf[tuple(current_ordinal)] += 1
        except KeyError:
            pmf[tuple(current_ordinal)] = 1

    result.append(evaluate_pmf_pe(pmf, ordinals_per_window, word_length))

    # one val at a time is removed and analyzed
    bar = progressbar.ProgressBar()
    for i in bar(range(num_windows)):
        current = ts[i:i+word_length*tau:tau]
        current_ordinal = sort_ordinal(current)
        pmf[tuple(current_ordinal)] -= 1
        if pmf[tuple(current_ordinal)] == 0:
            del pmf[tuple(current_ordinal)]
        current = ts[i+window-word_length*tau:i+window:tau]
        current_ordinal = sort_ordinal(current)
        try:
            pmf[tuple(current_ordinal)] += 1
        except KeyError:
            pmf[tuple(current_ordinal)] = 1

        temp = evaluate_pmf_pe(pmf, ordinals_per_window, word_length)
        result.append(temp)
        if temp == np.nan:
            raise ValueError('nan given as a result! bad news here')
    return age[window-2:], result

def calculate_wpe_python(age, ts, tau, word_length, window):
    '''
    a custom implementation of the WPE calculation
    '''
    if len(age) != len(ts):
        raise ValueError('make sure the age and time series are the same length')
    if window > len(age):
        raise ValueError('window can not be larger than the time series')

    num_windows = len(age) - window + 1
    ordinals_per_window = window - tau*word_length + 1

    result = []
    pmf = {}
    total_weight = 0
    # finding initial pmf --- from here on out can just change one value at a time
    for j in range(ordinals_per_window):
        current = ts[j:j+word_length*tau:tau]
        current_ordinal = sort_ordinal(current)
        current_weight = get_weight(current)
        total_weight += current_weight
        try:
            pmf[tuple(current_ordinal)] += current_weight
        except KeyError:
            pmf[tuple(current_ordinal)] = current_weight

    for key in pmf:
        pmf[key] /= total_weight

    result.append(evaluate_pmf_wpe(pmf, ordinals_per_window, word_length))

    for key in pmf:
        pmf[key] *= total_weight

    # one val at a time is removed and analyzed
    bar = progressbar.ProgressBar()
    for i in bar(range(num_windows)):
        current = ts[i:i+word_length*tau:tau]
        current_ordinal = sort_ordinal(current)
        current_weight = get_weight(current)
        total_weight -= current_weight
        pmf[tuple(current_ordinal)] -= current_weight

        if pmf[tuple(current_ordinal)] < .000001:
            del pmf[tuple(current_ordinal)]

        current = ts[i+window-word_length*tau:i+window:tau]
        current_weight = get_weight(current)
        total_weight += current_weight
        current_ordinal = sort_ordinal(current)
        try:
            pmf[tuple(current_ordinal)] += current_weight
        except KeyError:
            pmf[tuple(current_ordinal)] = current_weight

        for key in pmf:
            pmf[key] /= total_weight

        temp = evaluate_pmf_wpe(pmf, ordinals_per_window, word_length)
        result.append(temp)

        for key in pmf:
            pmf[key] *= total_weight

    return age[window-2:], result

def sort_ordinal(ordinal):
    '''
    returns the permuatation of a given ordinal: ie 9,4,7 => 2,0,1
    '''
    temp = np.argsort(np.asarray(ordinal))
    return temp.argsort()

def get_weight(ordinal):
    '''
    gets the weight of each ordinal used to calculate wpe
    '''
    return np.var(ordinal)

def evaluate_pmf_pe(pmf, ordinals_per_window, word_length):
    '''
    turns a pmf into a permuatation calculation
    '''
    pe = 0
    for ordinal in pmf:
        prob = float(pmf[ordinal]) / float(ordinals_per_window)
        pe += prob * np.log2(prob)
    return(-1*pe / np.log2(np.math.factorial(word_length)))

def evaluate_pmf_wpe(pmf, ordinals_per_window, word_length):
    '''
    turns a pmf into a permuatation calculation
    '''
    wpe = 0
    for ordinal in pmf:
        prob = pmf[ordinal]
        wpe += prob * np.log2(prob)
    return(-1*wpe / np.log2(np.math.factorial(word_length)))

def write_to_file(x,y):
    x, y = list(x), list(y)
    with open('debug.csv', mode='w') as csv_file:
        csv_file.write('age,wpe'+'\n')
        for i in range(len(x)):
            csv_file.write(str(x[i])+','+str(y[i])+'\n')
    csv_file.close()
    return

def main():
    x, y = np.arange(0, 10000), np.arange(0, 10000)
    temp_x, temp_y = binned_midpoint(x, y, 6)
    print(temp_x, temp_y)

if __name__ == '__main__':
    main()
