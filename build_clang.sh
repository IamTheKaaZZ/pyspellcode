#!/bin/bash

export path_to_llvm_project=../llvm-project

cd ../llvm-project/clang/tools
mkdir -p $path_to_llvm_project/clang/tools/commentparser
echo 'add_subdirectory(commentparser)' >> $path_to_llvm_project/clang/tools/CMakeLists.txt
cp commentparser_CMakeLists.txt $path_to_llvm_project/clang/tools/commentparser/CMakeLists.txt

mkdir -p $path_to_llvm_project/build
cmake -G Ninja $path_to_llvm_project/llvm -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" -DLLVM_BUILD_TESTS=ON
ninja
ninja check       # Test LLVM only.
ninja clang-test  # Test Clang only.
