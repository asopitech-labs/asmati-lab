# Nim 2.2.10 lib/system/seqs_v2.nim, strs_v2.nim, and memalloc.nim.
# Selected definitions only; source paths are repository-independent.

type
  NimSeqPayloadBase = object
    cap: int

  NimSeqPayload[T] = object
    cap: int
    data: UncheckedArray[T]

  NimSeqV2*[T] = object # \
    # if you change this implementation, also change seqs_v2_reimpl.nim!
    len: int
    p: ptr NimSeqPayload[T]

  NimRawSeq = object
    len: int
    p: pointer

proc newSeqPayloadUninit(cap, elemSize, elemAlign: int): pointer {.compilerRtl, raises: [].} =
  # Used in `newSeqOfCap()`.
  if cap > 0:
    var p = cast[ptr NimSeqPayloadBase](alignedAlloc(align(sizeof(NimSeqPayloadBase), elemAlign) + cap * elemSize, elemAlign))
    p.cap = cap
    result = p
  else:
    result = nil

proc prepareSeqAddUninit(len: int; p: pointer; addlen, elemSize, elemAlign: int): pointer {.
    noSideEffect, tags: [], raises: [], compilerRtl.} =
  {.noSideEffect.}:
    let headerSize = align(sizeof(NimSeqPayloadBase), elemAlign)
    if addlen <= 0:
      result = p
    elif p == nil:
      result = newSeqPayloadUninit(len+addlen, elemSize, elemAlign)
    else:
      # Note: this means we cannot support things that have internal pointers as
      # they get reallocated here. This needs to be documented clearly.
      var p = cast[ptr NimSeqPayloadBase](p)
      let oldCap = p.cap and not strlitFlag
      let newCap = max(resize(oldCap), len+addlen)
      if (p.cap and strlitFlag) == strlitFlag:
        var q = cast[ptr NimSeqPayloadBase](alignedAlloc(headerSize + elemSize * newCap, elemAlign))
        copyMem(q +! headerSize, p +! headerSize, len * elemSize)
        q.cap = newCap
        result = q

proc add*[T](x: var seq[T]; y: sink T) {.magic: "AppendSeqElem", noSideEffect, nodestroy.} =
  ## Generic proc for adding a data item `y` to a container `x`.
  ##
  ## For containers that have an order, `add` means *append*. New generic
  ## containers should also call their adding proc `add` for consistency.
  ## Generic code becomes much easier to write if the Nim naming scheme is
  ## respected.
  {.cast(noSideEffect).}:
    let oldLen = x.len
    var xu = cast[ptr NimSeqV2[T]](addr x)
    if xu.p == nil or (xu.p.cap and not strlitFlag) < oldLen+1:
      xu.p = cast[typeof(xu.p)](prepareSeqAddUninit(oldLen, xu.p, 1, sizeof(T), alignof(T)))
    xu.len = oldLen+1
    # .nodestroy means `xu.p.data[oldLen] = value` is compiled into a
    # copyMem(). This is fine as know by construction that
    # in `xu.p.data[oldLen]` there is nothing to destroy.
    # We also save the `wasMoved + destroy` pair for the sink parameter.
    xu.p.data[oldLen] = y

func capacity*[T](self: seq[T]): int {.inline.} =
  ## Returns the current capacity of the seq.
  # See https://github.com/nim-lang/RFCs/issues/460
  runnableExamples:
    var lst = newSeqOfCap[string](cap = 42)
    lst.add "Nim"
    assert lst.capacity == 42

  let sek = cast[ptr NimSeqV2[T]](unsafeAddr self)
  result = if sek.p != nil: sek.p.cap and not strlitFlag else: 0

proc resize(old: int): int {.inline.} =
  if old <= 0: result = 4
  elif old <= high(int16): result = old * 2
  else: result = old div 2 + old # for large arrays * 3/2 is better

proc alignedRealloc(p: pointer, oldSize, newSize, align: Natural): pointer =
    if align <= MemAlign:
      when compileOption("threads"):
        result = reallocShared(p, newSize)
      else:
        result = realloc(p, newSize)
    else:
      result = alignedAlloc(newSize, align)
      copyMem(result, p, oldSize)
      alignedDealloc(p, align)
