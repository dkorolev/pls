#include <iostream>

#include "pls.h"

PLS_ADD("trivial_transitive_dependency_bare_lib", "https://github.com/dkorolev/trivial_transitive_dependency_bare_lib");
PLS_DEP("lib_trivial_transitive_bare_lib");

PLS_DEP("trivial_cmake_lib");

#include "trivial_transitive_bare_lib.h"
#include "trivial_cmake_lib.h"

int main() {
  std::cout << "7*2=" << trivial_transitive_bare_lib_duplicate(7) << "; " << std::flush;
  std::cout << "8+8=" << trivial_cmake_lib_add(8, 8) << std::endl;
}
