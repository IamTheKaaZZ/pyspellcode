#!/bin/bash

sort stan_dictionary | uniq > temp
mv temp stan_dictionary
