# Issue #48: openArray sliceのpointer/length境界を観察する

## 問い

array、seq、seqのsliceを同じ`openArray[int]` procへ渡したとき、C backendは元データの位置と要素数をどう渡すか。範囲外sliceはcalleeへ入る前に止まるか。

この実験はNim内部のprivateな生成C関数を観察する。C ABIとして公開せず、string、seq append、所有権一般論へ範囲を広げない。

## 入力source

`src/openarray_slice.nim`は、`openArray[int]`を受ける`summary`へ次を渡す。

1. 4要素の固定array
2. 同じ4要素を持つseq
3. seqの`toOpenArray(1, 2)`

`sameAddress`はcalleeが見る先頭要素のaddressと、caller側で期待する元要素のaddressを比較する。別の`oob`実行では、長さ4のseqに`toOpenArray(1, 4)`を指定する。

## 再現

macOS、Nim 2.2.10、Apple Clang、Python 3が必要。リポジトリrootから実行する。

```sh
python3 tools/experiment_ci.py validate
python3 -m unittest discover -s tools/tests -p 'test_*.py'
python3 tools/experiment_ci.py run 015-nim-openarray-slice
```

実験directoryからは次で再実行できる。

```sh
python3 tests/run_experiment.py
```

scriptは`nim --version`のmacOS CPUへNim/Clangのarchitectureを揃える。binaryとnimcacheは`observed/bin/`と`observed/nimcache/`へ生成し、gitへ保存しない。通常実行は保存観測を上書きせず、`--record`だけが明示的に保存する。

ローカルで実行した主要commandは次である。

```sh
nim c --forceBuild:on --cc:clang --cpu:amd64 '--passC:-arch x86_64' '--passL:-arch x86_64' --mm:orc --nimcache:observed/nimcache --out:observed/bin/openarray_slice src/openarray_slice.nim
observed/bin/openarray_slice
observed/bin/openarray_slice oob
```

## 実測結果（2026-09-05 UTC）

Nim 2.2.10 / ORC / debug、Apple clang 21.0.0、macOS 26.6.2、x86_64 target。machineはarm64で、x86_64 binaryを実行した。詳細は`observed/environment.txt`へ保存した。

正常caseはexit 0だった。

```text
array len=4 first=10 last=40 total=100 aliases=true
seq len=4 first=10 last=40 total=100 aliases=true
slice len=2 first=20 last=30 total=50 aliases=true
```

範囲外caseはexit 1だった。

```text
Error: unhandled exception: index out of bounds: 1..4 notin 0..3 [IndexDefect]
```

範囲外caseでは`show`の出力がなく、calleeへ入る前に停止した。

## 生成Cの観察

`summary`と`sameAddress`は、どちらも要素pointerとlengthを別々のC引数として受けた。

```c
summarize(...)(NI* values_p0, NI values_p0Len_0);
sameAddress(...)(NI* values_p0, NI values_p0Len_0, NI* expected_p1);
```

caller側のloweringは次のように分かれた。

- array: 固定arrayの先頭pointerとliteral `4`
- seq: payloadの`data` pointerとseqの`len`
- slice: payloadの`data + 1` pointerと`2 - 1 + 1`

実行時の`aliases=true`も、それぞれcalleeの先頭addressが期待した元要素と一致したことを示す。正常sliceの構築箇所には要素copyやallocationが現れない。元seq初期化の`newSeqPayload`は別であり、seq storageの割り当てまで「allocationなし」とは扱わない。

範囲外`1..4`には、`show`より前に両端をseq lengthと比較する分岐と`raiseIndexError4`呼び出しが生成された。Nim 2.2.10の`system/chcks.nim`では、このhelperが`sysFatal(IndexDefect, ...)`へ接続される。

## 成果物

- `observed/call-boundary.md`: array・seq・sliceのpointer/length対応表
- `observed/generated-c-excerpt.c`: 2つのcalleeとcaller lowering、範囲検査の抜粋
- `observed/toolchain-definition-excerpt.nim`: Nim 2.2.10の`toOpenArray`と`raiseIndexError4`定義
- `observed/commands-2026-09-05.txt`: 実際のcompile、実行、環境確認commandとexit status
- `observed/environment.txt`: compiler、OS、machine、生成target
- `observed/run-2026-09-05.txt`: 正常caseと範囲外caseの実行結果
- `tests/run_experiment.py`: fresh build、signature、call lowering、alias、範囲検査、target、実行結果の検証

## 技術判断と未確認範囲

読者が区別する判断は、元storageとnon-owning view、pointerとlength、seq本体のallocationとslice view構築、正常sliceのcallee内bounds checkとslice構築前の範囲検査、private生成C signatureと公開C ABIである。

追跡した識別子は`openArray[int]`、`toOpenArray`、`magic: "Slice"`、`NI* values_p0`、`NI values_p0Len_0`、seq payloadの`data`と`len`、`raiseIndexError2`、`raiseIndexError4`、`sysFatal`、`IndexDefect`である。

未確認は、空slice、negative index、arrayから作る部分slice、view経由の書き換え、元seqのappend・再割り当て・破棄後のview、viewの長期保持、bounds check無効build、release、string、C ABI公開、別OS・target・Nim versionである。
