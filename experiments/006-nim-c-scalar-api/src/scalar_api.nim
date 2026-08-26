proc asmati_add_ints(left, right: cint): cint {.exportc, dynlib, cdecl.} =
  left + right

proc asmati_half(value: cdouble): cdouble {.exportc, dynlib, cdecl.} =
  value / 2.0
