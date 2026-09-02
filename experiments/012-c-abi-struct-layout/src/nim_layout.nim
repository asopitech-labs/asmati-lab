type
  AsmatiLayout {.importc: "AsmatiLayout", header: "layout.h", bycopy, completeStruct.} = object
    first: int32
    second: int32
    ratio: cfloat

static:
  doAssert sizeof(AsmatiLayout) == 12
  doAssert alignof(AsmatiLayout) == 4
  doAssert offsetOf(AsmatiLayout, first) == 0
  doAssert offsetOf(AsmatiLayout, second) == 4
  doAssert offsetOf(AsmatiLayout, ratio) == 8

echo "nim size=", sizeof(AsmatiLayout),
  " align=", alignof(AsmatiLayout),
  " first=", offsetOf(AsmatiLayout, first),
  " second=", offsetOf(AsmatiLayout, second),
  " ratio=", offsetOf(AsmatiLayout, ratio)
