proc address(value: string): pointer {.noinline.} =
  if value.len == 0:
    nil
  else:
    unsafeAddr value[0]

proc passAliases(value: string, expected: pointer): bool {.noinline.} =
  address(value) == expected

proc identity(value: string): string {.noinline.} =
  value

var original = newString(4)
original[0] = 'A'
original[1] = 'B'
original[2] = 'C'
original[3] = 'D'

let originalAddress = address(original)
echo "pass len=", original.len, " same=", passAliases(original, originalAddress),
  " value=", original

var returned = identity(original)
echo "return len=", returned.len, " same=", address(returned) == originalAddress,
  " value=", returned

var assigned = original
echo "assign before_same=", address(assigned) == originalAddress,
  " original=", original, " assigned=", assigned

assigned[0] = 'Z'
echo "assign after_same=", address(assigned) == originalAddress,
  " original=", original, " assigned=", assigned
