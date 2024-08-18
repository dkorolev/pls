#include "typesystem/serialization/json.h"

int main() {
  std::vector<uint64_t> v123{4,5,6};
  std::cout << JSON(v123) << std::endl;
}
