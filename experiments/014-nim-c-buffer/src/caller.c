#include "buffer_api.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int expect_bytes(const uint8_t *actual, const uint8_t *expected, size_t length) {
  return memcmp(actual, expected, length) == 0;
}

int main(void) {
  const uint8_t padded[] = {'A', 'B', 0, 0};
  const uint8_t full[] = {'A', 'S', 'M', 'A', 'T', 'I'};
  uint8_t output[8];
  uint8_t short_output[5];

  size_t empty_length = asmati_trimmed_length(NULL, 0);
  size_t padded_length = asmati_trimmed_length(padded, sizeof padded);
  size_t full_length = asmati_trimmed_length(full, sizeof full);
  printf("input empty=%zu padded=%zu full=%zu\n", empty_length, padded_length,
         full_length);
  if (empty_length != 0 || padded_length != 2 || full_length != 6) return 1;

  size_t query_required = asmati_write_label(NULL, 0);
  memset(output, 0xCC, sizeof output);
  size_t full_required = asmati_write_label(output, sizeof output);
  memset(short_output, 0xCC, sizeof short_output);
  size_t short_required = asmati_write_label(short_output, 3);
  printf("output query=%zu full_required=%zu short_required=%zu\n",
         query_required, full_required, short_required);
  printf("output full=%.*s short=%.*s tails=%02X,%02X\n", 6,
         (const char *)output, 3, (const char *)short_output,
         (unsigned int)output[6], (unsigned int)short_output[3]);

  if (query_required != 6 || full_required != 6 || short_required != 6) return 2;
  if (!expect_bytes(output, full, sizeof full) || output[6] != 0xCC ||
      output[7] != 0xCC) return 3;
  if (!expect_bytes(short_output, full, 3) || short_output[3] != 0xCC ||
      short_output[4] != 0xCC) return 4;
  return 0;
}
