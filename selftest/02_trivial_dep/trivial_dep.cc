#include <iostream>

#include "pls.h"

PLS_ADD("trivial_cmake_lib", "https://github.com/dkorolev/trivial_cmake_lib");
PLS_DEP("trivial_cmake_lib");

#include "trivial_cmake_lib.h"

int main() {
  std::cout << "2+2=" << trivial_cmake_lib_add(2, 2) << std::endl;
}
