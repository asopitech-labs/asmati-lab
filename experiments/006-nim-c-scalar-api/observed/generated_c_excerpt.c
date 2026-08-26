/* Nim Compiler 2.2.10 generated Cから、公開APIと初期化に関係する箇所だけを抜粋した。 */

N_LIB_EXPORT N_CDECL(int, asmati_add_ints)(int left_p0, int right_p1);
N_LIB_EXPORT N_CDECL(double, asmati_half)(double value_p0);

N_LIB_EXPORT N_CDECL(int, asmati_add_ints)(int left_p0, int right_p1) {
  int result;
  NI temporary;
  result = (int)0;
  if (nimAddInt(left_p0, right_p1, &temporary)) {
    raiseOverflow();
    goto BeforeRet_;
  }
  result = (int)(temporary);
BeforeRet_:
  return result;
}

N_LIB_EXPORT N_CDECL(double, asmati_half)(double value_p0) {
  double result;
  result = ((NF)(value_p0) / (NF)(2.0));
  return result;
}

N_LIB_EXPORT N_CDECL(void, NimMain)(void) {
  PreMain();
  NimMainInner();
}

N_LIB_PRIVATE void NIM_POSIX_INIT NimMainInit(void) {
  NimMain();
}

/* ローカル絶対path、line/frame bookkeeping、無関係なruntime定義は抜粋から除外した。 */
