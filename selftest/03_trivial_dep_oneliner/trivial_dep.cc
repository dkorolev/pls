#include <iostream>

#include "pls.h"

PLS_ADD_DEP("trivial_cmake_lib", "https://github.com/dkorolev/trivial_cmake_lib");

#include "trivial_cmake_lib.h"

int main() {
  std::cout << "3+3=" << trivial_cmake_lib_add(3, 3) << std::endl;
}
