#include <stdio.h>

static int internal_double(int value) {
  return value * 2;
}

int call_internal(int value) {
  return internal_double(value);
}

int call_external(const char *message) {
  return puts(message);
}
