type
  Reading = ref object
    value: int

proc readValue(reading: Reading): int {.noinline.} =
  if reading.isNil:
    -1
  else:
    reading.value

proc keepReading(reading: Reading): Reading {.noinline.} =
  reading

let present = Reading(value: 42)
let missing: Reading = nil

echo "present=", readValue(present)
echo "missing=", readValue(missing)
echo "keptIsNil=", keepReading(missing).isNil
