/* Nim 2.2.10 lib/nimbase.hの非Windows/GNU-compatible条件から使用した定義を抜粋した。 */

#ifdef __cplusplus
#  define NIM_EXTERNC extern "C"
#else
#  define NIM_EXTERNC
#endif

#define N_CDECL(rettype, name) rettype name
#define N_LIB_EXPORT NIM_EXTERNC __attribute__((visibility("default")))
#define N_LIB_IMPORT extern
#define NIM_POSIX_INIT __attribute__((constructor))

/* 別platform・別compiler分岐はこの実験の対象外として省略した。 */
