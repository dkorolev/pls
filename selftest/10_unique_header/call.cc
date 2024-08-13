#include <iostream>

#include "pls.h"

PLS_ADD_DEP("trivial_header_repo", "https://github.com/dkorolev/trivial_header_repo");

#include "unique_header_dir/unique_header.h"

int main() {
  std::cout << "UNIQUE=" << unique_function() << std::endl;
}
