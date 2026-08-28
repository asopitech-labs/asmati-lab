# 観察表

| 段階 | 識別子または式 | 保存先 | 観測 |
| --- | --- | --- | --- |
| Nim source | `addSuffix(value: string): string` | `src/proc_runtime.nim` | 受け取ったstringへ`!`を連結して返す |
| Nim定義 | `proc &*(x, y: string)` / `ConStrStr` | Nim 2.2.10 `lib/system.nim` | string同士の`&`はcompiler magicとして宣言される |
| 生成C関数 | `addSuffix__proc95runtime_u1(NimStringV2 value_p0)` | `@mproc_runtime.nim.c` | private関数。`NimStringV2`を値で受け取り、値で返す |
| 結果領域 | `rawNewString(value_p0.len + 1)` | `@mproc_runtime.nim.c` / `@psystem.nim.c` | 入力長+1のcapacityを確保し、長さ0・終端zeroのstringを返す |
| 第1追記 | `appendString(&T1_, value_p0)` | `@mproc_runtime.nim.c` | 入力stringのbytesをcopyする |
| 第2追記 | `appendString(&T1_, <"!" literal>)` | `@mproc_runtime.nim.c` | 1 byteのsuffixをcopyする |
| copy境界 | `copyMem__system_u1755` → `nimCopyMem` → `memcpy` | `@mproc_runtime.nim.c` | bytes copyはC libraryの`memcpy`へ到達する |
| 結果 | `result = T1_; return result;` | `@mproc_runtime.nim.c` | 構築済み`NimStringV2`を返す |
| caller | `NimMainModule` | `@mproc_runtime.nim.c` | `"nim"` literalで生成C関数を呼ぶ |
| 実行 | `nim!` | `observed/run-2026-08-28.txt` | sourceの期待結果と一致する |

`@mproc_runtime.nim.c`と`@psystem.nim.c`は実験で生成された再生成可能なCである。`lib/system.nim`と`lib/system/strs_v2.nim`はNim 2.2.10配布toolchainのsourceであり、生成物とは区別した。
