#!/bin/bash
export build_dir=temp_build_clang_tool
export llvm_repo=https://github.com/llvm/llvm-project
export name_of_tool=extract-comments

echo "Building clang tool to extract comments ..."

echo "Must clone llvm, then build the tool. This might take a while."
mkdir -p $build_dir
export path_to_llvm_project=$build_dir/llvm-project
if [ ! -d "$path_to_llvm_project" ]; then
    echo "Cloning llvm project (depth 1) ..."
    git clone --depth 1 $llvm_repo $path_to_llvm_project
    if [ $? -ne 0 ]; then
        echo "Clone failed."
        exit 1
    fi
fi

echo "Patching llvm project to include tool ..."
mkdir -p $path_to_llvm_project/clang-tools-extra/$name_of_tool
# Preserve modification time to avoid unnecessary recompiling.
cp -p internals/extract-comments_CMakeLists.txt $path_to_llvm_project/clang-tools-extra/$name_of_tool/CMakeLists.txt
cp -p internals/ExtractComments.cpp $path_to_llvm_project/clang-tools-extra/$name_of_tool/$tool_cpp
cd $path_to_llvm_project
if [ ! $(basename `git rev-parse --show-toplevel`) = "llvm-project" ]; then
    echo "Something went wrong; we aren't in the the right repository."
    # This is so I don't reset _my_ repository by mistake when I bug my shell
    # scripts.
    exit 1
fi
export patched_hash=2f4c57eca80c3a70587bfe729d0f9be4fbaa5acd
if [ ! $(git rev-parse HEAD) = $patched_hash ]; then
    git reset --hard master >/dev/null
    git am ../../internals/patch_clang_for_extract_comments_tool >/dev/null
fi
if [ $? -ne 0 ] || [ ! $(git rev-parse HEAD) = $patched_hash ]; then
    echo "Something went wrong with patching Clang?"
    exit 1
fi

echo "Building tool ..."
mkdir -p build
cd build
cmake -G Ninja ../llvm -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" >/dev/null
if [ $? -ne 0 ]; then
    echo "CMake failed."
    exit 1
fi
ninja $name_of_tool
if [ $? -ne 0 ]; then
    echo "Clang build failed."
    exit 1
fi
cd ../../..

cp $path_to_llvm_project/build/bin/$name_of_tool $name_of_tool
echo "Done. Tool is built."
