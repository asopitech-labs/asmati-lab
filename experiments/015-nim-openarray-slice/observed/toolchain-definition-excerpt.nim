# Nim 2.2.10 lib/system.nim and lib/system/chcks.nim.
# Selected definitions only; source paths are repository-independent.

proc toOpenArray*[T](x: seq[T]; first, last: int): openArray[T] {.
  magic: "Slice".}
  ## Returns a non-owning slice (a `view`:idx:) of `x` from the element at
  ## index `first` to `last` inclusive. Allows passing slices without copying,

proc toOpenArray*[I, T](x: array[I, T]; first, last: I): openArray[T] {.
  magic: "Slice".}

proc raiseIndexError4(l1, h1, h2: int) {.compilerproc, noinline.} =
  sysFatal(IndexDefect, "index out of bounds: " & $l1 & ".." & $h1 & " notin 0.." & $(h2 - 1))
