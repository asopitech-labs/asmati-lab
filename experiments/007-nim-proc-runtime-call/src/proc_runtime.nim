proc addSuffix(value: string): string =
  value & "!"

when isMainModule:
  echo addSuffix("nim")
