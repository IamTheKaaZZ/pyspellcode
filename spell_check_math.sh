#!/bin/bash

cd ..

# Something about rev/fun/inverse is causing all of Eigen to be pulled in and
# spellchecked. The other files that include Eigen somehow don't do that.

export files=$(find math/stan/math/fwd/ -type f \( \( -name "*.hpp" -o -name "*.cpp" \) -not \( -wholename "*rev/fun/inverse.hpp" \) \) )

pyspellcode/spell-check.py -std=c++14 --collect --show-file-progress -fparse-all-comments --personal-dict=pyspellcode/stan_math_dictionary --extra-clang-arg='-D_REENTRANT' --include-dir=math/. --include-dir=math/lib/eigen_3.3.3 --include-dir=math/lib/boost_1.72.0 --include-dir=math/lib/tbb_2019_U8/include --include-dir=math/lib/sundials_5.1.0/include --include-dir=math/lib/gtest_1.8.1 $files
