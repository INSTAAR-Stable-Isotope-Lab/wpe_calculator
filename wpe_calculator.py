#!/usr/bin/env python2

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
import numpy as np
import matplotlib.pyplot as plt
import information_theory_tools as itt
import argparse
import os, errno
import pandas as pd

def create_output_dir(save_location):
    ''' creates the output directory in specified save location if
    it doesn't already exist.
    '''
    if save_location[-1] != '/': save_location.append('/')
    print('creating output directory ...')
    directory = 'wpe_calculator_output'
    try:
        os.makedirs(save_location+directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return

def read_data(data_location, number_data_cols=1):
    ''' reads data from file into pandas dataframe based on number of columns
    '''
    print('reading in data ...')
    labels = ['isotope_col_{}'.format(ii+1) for ii in range(int(number_data_cols))]
    labels = ['age'] + labels
    return pd.read_csv(data_location, names=labels)

def calculate_pe(age, data, window_size=2400, weighted=1,
                age_direction=1, tau_lower=1, tau_upper=9):
    ''' calculates the permutation entropy of a given dataframe with specified
    parameters. see argparser for description of each argument of this function.
    returns a dict in form {tau: {pe_age:arr, pe_data:arr}}
    '''
    output = {}
    age_flip = np.flip(age, 0); data_flip = np.flip(data, 0)
    for tau in range(int(tau_lower), int(tau_upper+1)):
        pe_age, pe_data = itt.calculate_pe(age_flip, data_flip, tau, weighted, window_size)
        output[tau] = {'pe_age':pe_age, 'pe_data':pe_data}
    return output

def plot_pe(pe_dict, output_path, file_path):
    ''' plots and saves contents of a perm entropy dictionary returns from
    calculate_pe
    '''
    title = get_filename(file_path)
    print('plotting {}'.format(title))
    fig, ax = plt.subplots(figsize = (15,7))
    ax.set_ylim(0,1)
    for tau in pe_dict.keys():
        ax.plot(pe_dict[tau]['pe_age'], pe_dict[tau]['pe_data'], label = tau)
    ax.set_ylabel('WPE', size=15); ax.set_xlabel('Time', size=15)
    ax.set_title(title, size = 17)
    plt.legend(loc=4)
    plt.savefig(output_path+'wpe_calculator_output/{}.png'.format(title))
    return

def get_filename(path):
    ''' given a file path return the name of the file
    '''
    res = ''; found = False
    for letter in range(len(path)-1, -1, -1):
        if (path[letter] != '/') and (found == False):
            res += path[letter]
        else: found = True
    return res[::-1]

def main():
    print('welcome to the pe calculator!')

    # parse cl arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True,
                        help='csv file containing data, [age, data1, ...]')
    parser.add_argument('-tl', '--tau_lower', default=1,
                        help='tau lower bound')
    parser.add_argument('-tu', '--tau_upper', default=9,
                        help='tau upper bound')
    parser.add_argument('-o', '--output_path', default='./',
                        help='where the output images will be saved')
    parser.add_argument('-nc', '--number_of_columns', default='1',
                        help='number of columns of isotope data')
    parser.add_argument('-uc', '--use_columns', default='all',
                        help='which columns of data to use')
    parser.add_argument('-ws', '--window_size', default=2400,
                        help='how many data points to consider at each step')
    parser.add_argument('-w', '--weighted', default=1,
                        help='weightedness, 1=weighted - 0=unweighted')
    parser.add_argument('-ad', '--age_direction', default=1,
                        help='which way the age goes, recent->past=1 (typical)')

    args = vars(parser.parse_args())
    create_output_dir(args['output_path'])
    df = read_data(args['file'], args['number_of_columns'])
    print(df.head())

    if args['use_columns'] == 'all':
        for col in range(int(args['number_of_columns'])):
            res_dict = calculate_pe(df['age'].values, df['isotope_col_{}'.format(col+1)],
                                    window_size=args['window_size'], weighted=args['weighted'],
                                    age_direction=args['age_direction'], tau_lower=args['tau_lower'],
                                    tau_upper=args['tau_upper'])
            plot_pe(res_dict, args['output_path'], args['file'][:-4]+'_col_{}'.format(col+1))
    else:
        for col in list(args['use_columns']):
            res_dict = calculate_pe(df['age'].values, df['isotope_col_{}'.format(col)],
                                    window_size=args['window_size'], weighted=args['weighted'],
                                    age_direction=args['age_direction'], tau_lower=args['tau_lower'],
                                    tau_upper=args['tau_upper'])
            plot_pe(res_dict, args['output_path'], args['file'][:-4]+'_col_{}'.format(col))

if __name__ == '__main__':
    main()
