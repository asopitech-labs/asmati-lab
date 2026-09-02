# DeclarationとC ABI型の対応

| 契約要素 | C header | Nim declaration | Rust declaration |
| --- | --- | --- | --- |
| layout指定 | C structの正本 | `importc: "AsmatiLayout"`、`header: "layout.h"`、`bycopy`、`completeStruct` | `#[repr(C)]` |
| field 1 | `int32_t first` | `first: int32` | `first: i32` |
| field 2 | `int32_t second` | `second: int32` | `second: i32` |
| field 3 | `float ratio` | `ratio: cfloat` | `ratio: f32` |

Nim declarationはC headerのtypeを参照する。Rust declarationはheaderをincludeせず、C ABIを選択したmirrorなので、fieldの型と順序を別途一致させる必要がある。`tests/verify_layouts.py`はこのsource対応と実行時の数値を同時に検査する。
