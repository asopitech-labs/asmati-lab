#include <stddef.h>
#include <stdio.h>

#include "layout.h"

_Static_assert(sizeof(AsmatiLayout) == 12, "unexpected AsmatiLayout size");
_Static_assert(_Alignof(AsmatiLayout) == 4, "unexpected AsmatiLayout alignment");
_Static_assert(offsetof(AsmatiLayout, first) == 0, "unexpected first offset");
_Static_assert(offsetof(AsmatiLayout, second) == 4, "unexpected second offset");
_Static_assert(offsetof(AsmatiLayout, ratio) == 8, "unexpected ratio offset");

int main(void) {
  printf(
      "c size=%zu align=%zu first=%zu second=%zu ratio=%zu\n",
      sizeof(AsmatiLayout),
      _Alignof(AsmatiLayout),
      offsetof(AsmatiLayout, first),
      offsetof(AsmatiLayout, second),
      offsetof(AsmatiLayout, ratio));
  return 0;
}
