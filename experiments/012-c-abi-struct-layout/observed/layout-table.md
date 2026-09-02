# Size・alignment・offset比較

| 言語 | size | alignment | `first` | `second` | `ratio` | 観察 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| C | 12 | 4 | 0 | 4 | 8 | C headerを直接includeし、`sizeof`、`_Alignof`、`offsetof`で取得 |
| Nim | 12 | 4 | 0 | 4 | 8 | C headerのtypeを`importc`/`completeStruct`し、`sizeof`、`alignof`、`offsetOf`で取得 |
| Rust | 12 | 4 | 0 | 4 | 8 | 独立した`repr(C)` mirrorを`size_of`、`align_of`、`offset_of`で取得 |

全fieldは4 byte境界に連続配置された。`first`の前、field間、`ratio`の後に追加paddingは観察されず、最大alignment 4と最終field末尾12がstruct size 12に一致した。

値は各sourceのcompile-time assertionと、3 binaryの実行結果の両方で検査した。
