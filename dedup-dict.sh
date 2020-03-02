#!/bin/bash

sort stan_math_dictionary | uniq > temp
mv temp stan_math_dictionary
