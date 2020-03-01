#!/bin/bash

cd ..


export files=$(find math/stan/math/prim/meta -type f \( -name "*.hpp" -o -name "*.cpp" \))

pyspellcode/spell-check.py -std=c++14 --collect -fparse-all-comments --include-dir=math/. --include-dir=math/lib/eigen_3.3.3 --include-dir=math/lib/boost_1.72.0 --include-dir=math/lib/tbb_2019_U8/include --include-dir=math/lib/sundials_5.1.0/include --include-dir=math/lib/gtest_1.8.1 --personal-dict=pyspellcode/dictionary $files
