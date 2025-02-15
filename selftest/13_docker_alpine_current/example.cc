#include "pls.h"

PLS_INCLUDE_HEADER_ONLY_CURRENT();

#include "typesystem/serialization/json.h"

int main() {
  std::vector<uint64_t> v123{1,2,3};
  std::cout << JSON(v123) << std::endl;
}
