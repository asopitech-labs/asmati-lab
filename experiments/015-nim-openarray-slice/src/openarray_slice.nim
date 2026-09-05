import std/os

type Summary = tuple[length, first, last, total: int]

proc summarize(values: openArray[int]): Summary {.noinline.} =
  result.length = values.len
  if values.len > 0:
    result.first = values[0]
    result.last = values[^1]
    for value in values:
      result.total += value

proc sameAddress(values: openArray[int], expected: ptr int): bool {.noinline.} =
  values.len > 0 and unsafeAddr(values[0]) == expected

proc show(label: string, values: openArray[int], expected: ptr int) =
  let summary = summarize(values)
  echo label, " len=", summary.length, " first=", summary.first,
    " last=", summary.last, " total=", summary.total,
    " aliases=", sameAddress(values, expected)

var fixedValues = [10, 20, 30, 40]
var dynamicValues = @[10, 20, 30, 40]

if paramCount() == 1 and paramStr(1) == "oob":
  show("oob", dynamicValues.toOpenArray(1, 4), addr dynamicValues[1])
else:
  show("array", fixedValues, addr fixedValues[0])
  show("seq", dynamicValues, addr dynamicValues[0])
  show("slice", dynamicValues.toOpenArray(1, 2), addr dynamicValues[1])
