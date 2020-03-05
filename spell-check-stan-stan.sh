#!/bin/bash

cd ..

export files=$(find stan/src/stan/ -type f \( -name "*.hpp" -o -name "*.cpp" \) )

pyspellcode/spell-check.py -std=c++14 --collect --show-file-progress --all-comments --personal-dict=pyspellcode/stan_dictionary --extra-clang-arg="-DSTAN_OPENCL" --extra-clang-arg="-DOPENCL_DEVICE_ID=0" --extra-clang-arg="-DOPENCL_PLATFORM_ID=0" --extra-clang-arg="-DCL_HPP_ENABLE_EXCEPTIONS" --extra-clang-arg="-DCL_HPP_TARGET_OPENCL_VERSION=220" --extra-clang-arg='-D_REENTRANT' --include-dir=stan/lib/stan_math --include-dir=stan/src --include-dir=stan/lib/stan_math/lib/boost_1.72.0 --include-dir=stan/lib/stan_math/lib/opencl_2.2.0 --include-dir=stan/lib/stan_math/lib/eigen_3.3.3 --include-dir=stan/lib/stan_math/lib/gtest_1.8.1/include --include-dir=stan/lib/stan_math/lib/sundials_5.1.0/include --include-dir=stan/lib/stan_math/lib/tbb_2019_U8/include $files
