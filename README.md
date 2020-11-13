description: this tool takes data from a csv file, calculates the wpe, and saves plots to a directory. the user has flexibility to choose which columns of the file to  run the wpe on, which tau values to plot, where the plots should be saved, as well as the other parameters of the wpe calculation: weight and window size.

prerequisites: the only two pieces of software we need on the machine are python2.7 and the associated pip (python package manager). pip will automatically be installed with the command

brew install python2

(on mac) or

sudo apt-get install python2

on linux. aside for mac users: if you don't yet have brew, first type the command

xcode-select --install

followed by

ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

verify that they are both installed with

python2 -V
pip -V

setup: unzip the file and put it somewhere easy to remember. navigate to the directory in a terminal instance and run the command

bash setup.sh

This will install all the packages we need in python as well as build some of the precompiled code to make things run faster. there will be some warnings raised here, don't worry about those.

usage: wpe_calculator.py [-h] -f FILE [-tl TAU_LOWER] [-tu TAU_UPPER]
                         [-o OUTPUT_PATH] [-nc NUMBER_OF_COLUMNS]
                         [-uc USE_COLUMNS] [-ws WINDOW_SIZE] [-w WEIGHTED]
                         [-ad AGE_DIRECTION]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  csv file containing data, [age, data1, ...]
  -tl TAU_LOWER, --tau_lower TAU_LOWER
                        tau lower bound
  -tu TAU_UPPER, --tau_upper TAU_UPPER
                        tau upper bound
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        where the output images will be saved
  -nc NUMBER_OF_COLUMNS, --number_of_columns NUMBER_OF_COLUMNS
                        number of columns of isotope data
  -uc USE_COLUMNS, --use_columns USE_COLUMNS
                        which columns of data to use
  -ws WINDOW_SIZE, --window_size WINDOW_SIZE
                        how many data points to consider at each step
  -w WEIGHTED, --weighted WEIGHTED
                        weightedness, 1=weighted - 0=unweighted
  -ad AGE_DIRECTION, --age_direction AGE_DIRECTION
                        which way the age goes, recent->past=1 (typical)

this is the usage for the command line tool (can be seen by running 'python2 wpe_calculator.py -h' from the directory). the only required argument is the file path specifying where the data is found. all the other parameters have defaults. these are the defaults:

tau_lower=1
tau_upper=9
output_path='./'
number_of_columns=1
use_columns='all'
window_size=2400
weighted=1
age_direction=1.

we are mostly concerned with the tau values, the number of columns, and which columns to use.

examples:

i figure it is probably easiest to understand with a couple examples, so i will walk through how i did the run for the data today. in the our main directory we see a data directory with five files [10AmpTilFlatOneOff.txt,  evenDepthData1_15Lin.txt,  evenDepthData1_15Sloped.txt, evenDepthData1_5Lin.txt, evenDepthData75_15Sloped.txt].

we will start with the 10Amp file because it is the simplest. because it only has 1 column of isotope data (along with the age data column of course), we don't have to specify anything except the file path. run the command,

python2 wpe_calculator.py -f data/10AmpTilFlatOneOff.txt

this will create a directory called 'wpe_calculator_output' with an image of the tau values 1-9 run on that data (now that this folder is created it will remain there and all future runs will be put into it). now lets look at a more complicated example where we want to do one of the other files. all the other files have four columns of isotope data, but we only want to do the wpe on the last one. so run

 python2 wpe_calculator.py -f data/evenDepthData1_5Lin.txt -nc 4 -uc 4

here we specify that there are four columns of data, and we only want to use the fourth one. we can have even more control if say we want the second and fourth column, we simply modify our last command to be,

python2 wpe_calculator.py -f data/evenDepthData1_5Lin.txt -nc 4 -uc 24

note that each column will be run with each tau value, and saved to separate images under the name <data_filename>_col_<column_number>.png, in the wpe_calculator_output directory.

ok, i think thats all! just make sure that each file you use is a csv!

please let me know if something breaks or installation doesn't go smoothly!

-mike
