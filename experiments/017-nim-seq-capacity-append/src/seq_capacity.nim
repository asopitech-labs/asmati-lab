proc total(values: seq[int]): int {.noinline.} =
  for value in values:
    result += value

proc show(step: int, values: seq[int]) {.noinline.} =
  echo "step=", step, " len=", values.len, " cap=", values.capacity,
    " total=", total(values)

var values: seq[int]
show(0, values)
for value in 1 .. 10:
  values.add(value)
  show(value, values)
