proc noArgs(): int =
  7

proc addOne(x: int): int =
  x + 1

proc half(x: float): float =
  x / 2.0

when isMainModule:
  echo "noArgs=", noArgs()
  echo "addOne(41)=", addOne(41)
  echo "half(3.5)=", half(3.5)
