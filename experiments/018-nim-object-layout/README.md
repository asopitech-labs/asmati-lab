# Issue #43: object fieldのlayoutとsizeofを生成Cで確認する

## 問い

`int`、`bool`、`float`をこの順に持つNim objectは、Nim 2.2.10の生成Cでどのfield順とC型になるか。64-bit macOS targetで、objectのsize、alignment、各field offset、paddingはどう観測できるか。

この実験はNim内部のprivateな生成C structを観察する。継承、dynamic dispatch、公開C ABIの互換性保証へ範囲を広げない。

## 入力source

`src/object_layout.nim`は`Sample` objectを次の順で定義する。

1. `count: int`
2. `enabled: bool`
3. `ratio: float`

sourceにはsize、alignment、offsetのcompile-time assertionを置く。実行時に同じ値と各field型のsizeを出力し、値渡しされた`Sample`の3 fieldを読む`score`も実行する。

## 再現

macOS、Nim 2.2.10、Apple Clang、Python 3が必要。リポジトリrootから実行する。

```sh
python3 tools/experiment_ci.py validate
python3 -m unittest discover -s tools/tests -p 'test_*.py'
python3 tools/experiment_ci.py run 018-nim-object-layout
```

実験directoryからは次で再実行できる。

```sh
python3 tests/run_experiment.py
```

scriptはfresh buildを行い、保存済みのNim 2.2.10型定義、生成C structとfield access、実行結果、binary targetを検証する。binaryとnimcacheは`observed/bin/`と`observed/nimcache/`へ生成し、gitへ保存しない。通常実行は保存観測を上書きせず、`--record`だけが明示的に保存する。

## 実測結果（2026-09-10 UTC）

Nim 2.2.10 / ORC / debug、Apple Clang、macOSの64-bit targetで実行した。compiler、OS、machine、生成targetは`observed/environment.txt`へ保存する。

```text
size=24 align=8
fieldSizes int=8 bool=1 float=8
count=0 enabled=8 ratio=16
score=9.0
```

`Sample`はsize 24、alignment 8だった。field offsetは宣言順に0、8、16となった。`enabled`は1 byteで終端がoffset 9、次の`ratio`はoffset 16なので、その間に7 byteのpaddingがある。生成C structにはpadding用の明示fieldはない。

## 生成Cと型定義の観察

生成Cの`Sample` structは`NI count`、`NIM_BOOL enabled`、`NF ratio`の順だった。`score`も`sample_p0.enabled`、`sample_p0.count`、`sample_p0.ratio`として同じfieldを読む。

生成Cは`NIM_INTBITS 64`を定義する。Nim 2.2.10の`nimbase.h`では、この条件の`NI`は`NI64`、C99以降の`NIM_BOOL`は`_Bool`、`NF`は`double`となる。実行時のfield size 8、1、8と対応した。

field順とC型は生成Cの記述、sizeとoffsetはcompile-time assertionおよび実行結果、paddingはfield sizeとoffset差で確認する。C compilerが挿入するpaddingを、生成Cに明示fieldがあるかのようには扱わない。

## 成果物

- `observed/layout-table.md`: fieldごとのC型、size、offset、padding
- `observed/generated-c-excerpt.c`: `NIM_INTBITS`、生成struct、field accessの抜粋
- `observed/nimbase-definition-excerpt.h`: `NI`、`NIM_BOOL`、`NF`の定義鎖
- `observed/commands-2026-09-10.txt`: compile、実行、環境確認commandとexit status
- `observed/environment.txt`: compiler、OS、machine、生成target、memory manager、build mode
- `observed/run-2026-09-10.txt`: binary形式と実行結果
- `tests/run_experiment.py`: fresh buildと全証拠の検証

## 技術判断と未確認範囲

読者が区別する判断は、Nim sourceのfield順と生成C structのfield順、明示fieldとC compilerのpadding、field型のsizeとobject全体のsize、private生成structの観察と公開C ABI契約である。

追跡した識別子は`Sample`、`count`、`enabled`、`ratio`、`sizeof`、`alignof`、`offsetOf`、`NIM_INTBITS`、`NI`、`NI64`、`NIM_BOOL`、`NF`、`score`である。

未確認は、field順の変更、明示alignment、packed object、継承、variant object、ref object、dynamic dispatch、公開C ABI、release、別memory manager、32-bit、Windows、Linux、別compiler・target・Nim versionである。
