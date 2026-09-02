# Issue #68: C ABI structのlayout契約を最小例で固定する

## 問い

2つの32-bit整数と1つのC `float`を持つstructをC header、NimのC import declaration、Rust `repr(C)`で表したとき、size、alignment、field orderを示すoffsetは一致するか。

## 最小struct

C headerを契約の正本とした。

```c
typedef struct AsmatiLayout {
  int32_t first;
  int32_t second;
  float ratio;
} AsmatiLayout;
```

- C probeはこのheaderを直接includeする。
- Nimは`importc`、`header`、`bycopy`、`completeStruct`を付け、`int32`、`int32`、`cfloat`の順で宣言する。
- Rustは`#[repr(C)]`を付け、`i32`、`i32`、`f32`の順で独立に宣言する。

各言語にsize、alignment、3 field offsetのcompile-time assertionを置き、実行時にも同じ値を出力した。

## targetの揃え方

`tests/build_layouts.py`は`rustc -vV`のnative host targetを読み、Cの`-arch`とNimの`--cpu`・Clang/linker `-arch`を同じarchitectureへ揃える。ローカル観察ではRust hostが`x86_64-apple-darwin`だったため、3 binaryともx86_64 Mach-Oとして作成した。実行machineはarm64 macOSである。

この選択は、ローカルのRust toolchainにARM64標準libraryがなかったため、言語ごとに異なるtargetを比較しないために行った。CIでもそのrunnerのRust native hostへ3言語を揃える。

## 再現command

macOS上で、このdirectoryをcurrent directoryとして実行する。

```console
$ python3 tests/prepare_outputs.py
layout output directory prepared
$ python3 tests/build_layouts.py
layout target prepared: x86_64-apple-darwin
$ python3 tests/verify_layouts.py
C, Nim, and Rust C-ABI struct layouts verified
```

ローカルで`build_layouts.py`が実行した主要commandは次のとおり。

```console
$ clang -arch x86_64 -std=c11 -Wall -Wextra -Werror -Isrc src/c_layout.c -o observed/bin/c_layout
$ nim c --cc:clang --cpu:amd64 '--passC:-arch x86_64' --passC:-Isrc '--passL:-arch x86_64' --out:observed/bin/nim_layout src/nim_layout.nim
$ rustc --edition=2024 -o observed/bin/rust_layout src/rust_layout.rs
```

binaryとNim cacheは再生成物なのでcommitしない。

## 観察結果

| 言語 | size | alignment | `first` offset | `second` offset | `ratio` offset |
| --- | ---: | ---: | ---: | ---: | ---: |
| C | 12 | 4 | 0 | 4 | 8 |
| Nim | 12 | 4 | 0 | 4 | 8 |
| Rust | 12 | 4 | 0 | 4 | 8 |

このx86_64 Mach-O条件では3つの観察値がすべて一致した。fieldは宣言順に4 byte間隔で配置され、最後の`ratio`がoffset 8、struct全体がsize 12、alignment 4だった。

ただし、3言語の宣言の意味は同一ではない。NimはC headerの`AsmatiLayout`を`importc`で参照し、Rustは`repr(C)`でC layout規則を選ぶ独立したmirror declarationである。数値が一致したことに加え、型とfield順をsource検査で固定している。

## 成果物

- `src/layout.h`: C ABI headerの正本
- `src/c_layout.c`: C11 `_Alignof`・`offsetof` probe
- `src/nim_layout.nim`: `importc`/`bycopy`/`completeStruct` declarationと`sizeof`/`alignof`/`offsetOf`
- `src/rust_layout.rs`: `repr(C)` declarationと`size_of`/`align_of`/`offset_of`
- `observed/layout-results-2026-09-02.txt`: 3 binaryの形式と実行結果
- `observed/layout-table.md`: 数値比較とpadding観察
- `observed/declaration-table.md`: 各言語の型・ABI指定の対応
- `tests/verify_layouts.py`: source契約、同一target、数値一致の検証

## 未確認範囲

- ARM64、Windows x64、32-bit targetなど、ローカルx86_64 Mach-O以外の保存済み観察値
- structを実際に言語間で渡すfunction callとcalling convention
- endianness、値のbyte表現、serialization互換性
- `packed`、明示alignment、field reorder、64-bit型、pointer、enum、bool
- nested/anonymous/variable-length struct、union、継承
- compiler optionやcompiler versionを変えた場合のlayout保証
