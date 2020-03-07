/// Same output format as the Clang tool, but does not require building Clang.
/// For testing.

#include <iostream>

int main() {
  std::cout << "// typo1 apple good typo2-typo3" << std::endl;
  std::cout << "/* typo4 apple good(tree) typo5-typo6\napple*/" << std::endl;
}
