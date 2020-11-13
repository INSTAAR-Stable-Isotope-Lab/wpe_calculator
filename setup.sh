#!/usr/bin/env bash
echo "make sure python2 and pip2 are installed!"
echo "installing necessary packages ..."
sudo pip2 install matplotlib numpy pandas Cython scipy bottleneck progressbar2

echo "building cython file ... "
python2 setup.py build_ext --inplace
rm -rf ordinal_TSA.c ordinal_TSA.o build/
