type
  AsmatiPair* {.exportc, bycopy.} = object
    left*: cint
    right*: cint

proc asmati_add*(left, right: cint): cint {.exportc, dynlib, cdecl.} =
  left + right

proc asmati_sum_pair*(pair: AsmatiPair): cint {.exportc, dynlib, cdecl.} =
  pair.left + pair.right
