# Nim 2.2.10 lib/system/strs_v2.nim and lib/system.nim.
# Selected definitions only; source paths are repository-independent.

type
  NimStrPayloadBase = object
    cap: int

  NimStrPayload {.core.} = object
    cap: int
    data: UncheckedArray[char]

  NimStringV2 {.core.} = object
    len: int
    p: ptr NimStrPayload ## can be nil if len == 0.

template frees(s) =
  if not isLiteral(s):
    when compileOption("threads"):
      deallocShared(s.p)
    else:
      dealloc(s.p)

proc nimAsgnStrV2(a: var NimStringV2, b: NimStringV2) {.compilerRtl.} =
  if a.p == b.p and a.len == b.len: return
  if isLiteral(b):
    # we can shallow copy literals:
    frees(a)
    a.len = b.len
    a.p = b.p
  else:
    if isLiteral(a) or (a.p.cap and not strlitFlag) < b.len:
      # we have to allocate the 'cap' here, consider
      # 'let y = newStringOfCap(); var x = y'
      # on the other hand... These get turned into moves now.
      frees(a)
      a.p = allocPayload(b.len)
      a.p.cap = b.len
    a.len = b.len
    copyMem(unsafeAddr a.p.data[0], unsafeAddr b.p.data[0], b.len+1)

proc nimPrepareStrMutationImpl(s: var NimStringV2) =
  let oldP = s.p
  # can't mutate a literal, so we need a fresh copy here:
  s.p = allocPayload(s.len)
  s.p.cap = s.len
  copyMem(unsafeAddr s.p.data[0], unsafeAddr oldP.data[0], s.len+1)

proc nimPrepareStrMutationV2(s: var NimStringV2) {.compilerRtl, inl.} =
  if s.p != nil and (s.p.cap and strlitFlag) == strlitFlag:
    nimPrepareStrMutationImpl(s)

proc `=`*[T](dest: var T; src: T) {.noSideEffect, magic: "Asgn".}
proc `=copy`*[T](dest: var T; src: T) {.noSideEffect, magic: "Asgn".}
