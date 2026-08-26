#include <stdio.h>

#include "scalar_api.h"

int main(void) {
  const int sum = asmati_add_ints(19, 23);
  const double half = asmati_half(3.5);

  printf("add(19,23)=%d\n", sum);
  printf("half(3.5)=%.2f\n", half);

  if (sum != 42 || half != 1.75) {
    return 1;
  }
  return 0;
}
