#!/bin/bash

sort stan_math_dictionary | uniq -u > temp
mv temp stan_math_dictionary
