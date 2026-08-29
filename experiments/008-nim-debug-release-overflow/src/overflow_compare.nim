import std/[os, strutils]

proc addOne(value: int): int {.noinline.} =
  value + 1

when isMainModule:
  if paramCount() != 1:
    quit "usage: overflow_compare <integer>", QuitFailure
  let value = parseInt(paramStr(1))
  echo addOne(value)
