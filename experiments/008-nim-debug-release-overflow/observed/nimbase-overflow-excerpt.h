/*
 * Nim 2.2.10 lib/nimbase.hからの抜粋。
 * これはgenerated artifactではなく、nimAddIntを定義へ追跡する配布headerである。
 */
#if (!defined(_MSC_VER) || defined(__clang__)) && !defined(NIM_EmulateOverflowChecks)
  #define nimAddInt64(a, b, res) __builtin_saddll_overflow(a, b, (long long int*)res)

  #if NIM_INTBITS == 32
    #if (defined(__arm__) || defined(__riscv)) && defined(__GNUC__)
      #define nimAddInt(a, b, res) __builtin_saddl_overflow(a, b, res)
    #else
      #define nimAddInt(a, b, res) __builtin_sadd_overflow(a, b, res)
    #endif
  #else
    #define nimAddInt(a, b, res) __builtin_saddll_overflow(a, b, (long long int*)res)
  #endif
#endif
