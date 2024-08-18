#include <iostream>

#include "pls.h"

// Depend on ths code in this repo. Since it does not have the `CMakeLists.txt` file, one will be created.
PLS_ADD("trivial_cmake_lib_without_cmakelists_txt", "https://github.com/dkorolev/trivial_cmake_lib_without_cmakelists_txt");

// Add the dependency from the above repo. Since its source name is lib_*.cc`, it will yield a library target.
PLS_DEP("lib_trivial_cmake_lib_without_cmakelists_txt")

#include "trivial_cmake_lib_without_cmakelists_txt.h"

int main() {
  std::cout << "2+2=" << trivial_cmake_lib_without_cmakelists_txt_add(2, 2) << std::endl;
}
