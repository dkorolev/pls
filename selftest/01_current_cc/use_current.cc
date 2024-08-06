#include "pls.h"

PLS_USE_CURRENT();

#include <vector>

#include "typesystem/serialization/json.h"

int main() {
  std::cout << JSON(std::vector<uint64_t>{1,2,3}) << std::endl;
}
