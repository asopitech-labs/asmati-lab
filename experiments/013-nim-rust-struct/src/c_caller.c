#include "pair_api.h"
#include <stddef.h>
#include <stdio.h>

_Static_assert(sizeof(int) == 4, "this experiment requires 32-bit C int");
_Static_assert(sizeof(AsmatiPair) == 8, "pair size");
_Static_assert(_Alignof(AsmatiPair) == 4, "pair alignment");
_Static_assert(offsetof(AsmatiPair, left) == 0, "left offset");
_Static_assert(offsetof(AsmatiPair, right) == 4, "right offset");

int main(void) {
  const AsmatiPair pairs[] = {{19, 23}, {-100, 7}, {32767, 1}};
  const int expected[] = {42, -93, 32768};
  printf("size=%zu align=%zu left=%zu right=%zu\n", sizeof(AsmatiPair),
         _Alignof(AsmatiPair), offsetof(AsmatiPair, left), offsetof(AsmatiPair, right));
  for (size_t i = 0; i < 3; ++i) {
    int scalar = asmati_add(pairs[i].left, pairs[i].right);
    int aggregate = asmati_sum_pair(pairs[i]);
    printf("case=%zu scalar=%d pair=%d\n", i, scalar, aggregate);
    if (scalar != expected[i] || aggregate != expected[i]) return 1;
  }
  return 0;
}
