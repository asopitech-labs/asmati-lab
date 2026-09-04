const Label = [65'u8, 83'u8, 77'u8, 65'u8, 84'u8, 73'u8]

proc asmati_trimmed_length*(input: ptr UncheckedArray[uint8],
                            length: csize_t): csize_t
    {.exportc, dynlib, cdecl.} =
  result = length
  while result > 0 and input[result - 1] == 0'u8:
    dec result

proc asmati_write_label*(output: ptr UncheckedArray[uint8],
                         capacity: csize_t): csize_t
    {.exportc, dynlib, cdecl.} =
  result = csize_t(Label.len)
  let writable = min(capacity, result)
  var index = csize_t(0)
  while index < writable:
    output[index] = Label[int(index)]
    inc index
