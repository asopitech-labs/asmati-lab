#include <stdio.h>

int shared_answer(void);

int main(void) {
  printf("answer=%d\n", shared_answer());
  return 0;
}
