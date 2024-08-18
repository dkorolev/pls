#include <iostream>

#include "pls.h"

// Import the transitive repo and add the dependency on a lib from it.
PLS_ADD("trivial_transitive_cmake_lib", "https://github.com/dkorolev/trivial_transitive_cmake_lib");
PLS_DEP("lib_trivial_transitive_cmake_lib");

// Add a dependency on the trivial lib as well. No need to `ADD` it, since it is already added transitively.
PLS_DEP("trivial_cmake_lib");

// Inside `trivial_transitive_cmake_lib`, the header is under `include/`.'
// It can be `#include`-d directly, since library targets exposes by `pls` automatically
// add their directories to the includes path upon the desired target depending on that library.
// In other words, the first `PLS_DEP` above makes this line correct.
#include "include/trivial_transitive_cmake_lib.h"

// Similarly, the second `PLS_DEP` above makes this line correct.
// Because `trivial_cmake_lib` has its own `CMakeLists.txt`, and adds its own source dir to include-s search path.
#include "trivial_cmake_lib.h"

int main() {
  std::cout << "6*2=" << trivial_transitive_cmake_lib_duplicate(6) << "; " << std::flush;
  std::cout << "7+7=" << trivial_cmake_lib_add(7, 7) << std::endl;
}
