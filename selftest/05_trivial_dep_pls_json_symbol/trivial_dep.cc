#include <iostream>

// NOTE(dkorolev): Do not `#include "pls.h"` here, since `pls.json` is used.

#include "trivial_cmake_lib.h"

int main() {
  std::cout << "2+2=" << trivial_cmake_lib_add(2, 2) << std::endl;
}
