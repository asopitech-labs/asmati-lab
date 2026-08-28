# Nim 2.2.10配布sourceからの最小抜粋。
# これは実験が生成したartifactではなく、生成Cの識別子を定義へ追跡する根拠である。

# lib/system.nim
proc `&`*(x, y: string): string {.
  magic: "ConStrStr", noSideEffect.}

# lib/system/strs_v2.nim
type
  NimStringV2 {.core.} = object
    len: int
    p: ptr NimStrPayload

proc appendString(dest: var NimStringV2; src: NimStringV2) {.compilerproc, inline.} =
  if src.len > 0:
    copyMem(unsafeAddr dest.p.data[dest.len], unsafeAddr src.p.data[0], src.len)
    inc dest.len, src.len
    dest.p.data[dest.len] = '\0'

proc rawNewString(space: int): NimStringV2 {.compilerproc.} =
  if space <= 0:
    result = NimStringV2(len: 0, p: nil)
  else:
    var p = allocPayload(space)
    p.cap = space
    p.data[0] = '\0'
    result = NimStringV2(len: 0, p: p)
