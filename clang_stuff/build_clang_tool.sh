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
fi
mkdir -p $path_to_llvm_project/clang-tools-extra/$name_of_tool
echo "Patching llvm project to include tool ..."
# Preserve modification time to avoid unnecessary recompiling.
cp -p clang_stuff/CMakeLists_patched $path_to_llvm_project/clang-tools-extra/CMakeLists.txt
cp -p clang_stuff/extract-comments_CMakeLists.txt $path_to_llvm_project/clang-tools-extra/$name_of_tool/CMakeLists.txt
cp -p clang_stuff/ExtractComments.cpp $path_to_llvm_project/clang-tools-extra/$name_of_tool/$tool_cpp
cp -p clang_stuff/ASTContext.h_patched $path_to_llvm_project/clang/include/clang/AST/ASTContext.h
cd $path_to_llvm_project
echo "Building tool ..."
mkdir -p build
cd build
cmake -G Ninja ../llvm -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" >/dev/null
ninja $name_of_tool
cd ../../..
mv $path_to_llvm_project/build/bin/$name_of_tool $name_of_tool
echo "Done. Tool is built."
