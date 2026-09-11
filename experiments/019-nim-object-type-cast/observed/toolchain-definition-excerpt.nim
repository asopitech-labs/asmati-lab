# Nim 2.2.10 lib/system.nim, system/arc.nim, system/chcks.nim,
# and system/exceptions.nim. Selected definitions only.

when not defined(js) and defined(nimV2):
  type
    DestructorProc = proc (p: pointer) {.nimcall, gcsafe, raises: [].}
    TNimTypeV2 {.compilerproc.} = object
      destructor: pointer
      size: int
      align: int16
      depth: int16
      display: ptr UncheckedArray[uint32] # classToken
      when defined(nimTypeNames) or defined(nimArcIds) or defined(nimOrcLeakDetector):
        name: cstring
      traceImpl: pointer
      typeInfoV1: pointer # for backwards compat, usually nil
      flags: int
      when defined(gcDestructors):
        when defined(cpp):
          vTable: ptr UncheckedArray[pointer] # vtable for types
        else:
          vTable: UncheckedArray[pointer] # vtable for types
    PNimTypeV2 = ptr TNimTypeV2

proc isObjDisplayCheck(source: PNimTypeV2, targetDepth: int16, token: uint32): bool {.compilerRtl, inl.} =
  result = targetDepth <= source.depth and source.display[targetDepth] == token

proc raiseObjectConversionError() {.compilerproc, noinline.} =
  sysFatal(ObjectConversionDefect, "invalid object conversion")

  ObjectConversionDefect* = object of Defect ## \
    ## Raised if an object is converted to an incompatible object type.
    ## You can use `of` operator to check if conversion will succeed.
