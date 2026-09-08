# Issue #49: stringのpointer/length表現とcopy条件を観察する

## 問い

heap上へ作った同一のNim `string`をprocへ渡す、procから返す、別変数へ代入する場合に、Nim 2.2.10のC backendは`len`とpayload pointerをどう扱うか。代入後の書き換えと終了時の解放は、どの生成C/runtime helperへ接続されるか。

この実験はNim内部のprivateな生成C関数を観察する。string literal、公開C ABI、Unicode、性能、別memory managerへ範囲を広げない。

## 入力source

`src/string_copy.nim`は`newString(4)`で`ABCD`を作る。payload先頭addressを基準に、次を実行する。

1. `passAliases`へ値引数として渡す
2. `identity`から戻して`returned`へ保存する
3. `original`を`assigned`へ代入する
4. `assigned[0]`を`Z`へ変更する

address値そのものは保存せず、基準addressとの一致だけを`true`/`false`で記録する。

## 再現

macOS、Nim 2.2.10、Apple Clang、Python 3が必要。リポジトリrootから実行する。

```sh
python3 tools/experiment_ci.py validate
python3 -m unittest discover -s tools/tests -p 'test_*.py'
python3 tools/experiment_ci.py run 016-nim-string-copy
```

実験directoryからは次で再実行できる。

```sh
python3 tests/run_experiment.py
```

scriptはfresh buildを行い、保存済みのNim定義、生成C、runtime helper、実行結果、binary targetを検証する。binaryとnimcacheは`observed/bin/`と`observed/nimcache/`へ生成し、gitへ保存しない。通常実行は保存観測を上書きせず、`--record`だけが明示的に保存する。

## 実測結果（2026-09-08 UTC）

Nim 2.2.10 / ORC / debug、Apple Clang、macOSで実行した。compiler、OS、machine、生成targetは`observed/environment.txt`へ保存する。

```text
pass len=4 same=true value=ABCD
return len=4 same=false value=ABCD
assign before_same=false original=ABCD assigned=ABCD
assign after_same=false original=ABCD assigned=ZBCD
```

値引数ではcalleeが元payloadを観察した。`identity`の戻り値と通常代入は、どちらも元と異なるpayloadを持った。代入直後からaddressが異なり、`assigned`の変更後も`original`は`ABCD`のままだった。

## 生成Cとruntimeの観察

`NimStringV2`は`NI len`と`NimStrPayload* p`の組である。`passAliases`と`identity`は、この構造体を値引数として受ける。`passAliases`内には`eqcopy`または`nimAsgnStrV2`がなく、実行結果もpayload先頭の一致を示した。

`identity`の戻り値構築と`assigned = original`は`eqcopy`を呼ぶ。`eqcopy`は`nimAsgnStrV2`へ接続される。今回の`newString`由来のsourceはliteralではないため、`nimAsgnStrV2`のnon-literal分岐がdestination payloadを確保し、終端NULを含む`len + 1` byteを`copyMem`した。

`assigned[0] = 'Z'`の直前には`nimPrepareStrMutationV2`がある。このhelperはliteral flag付きpayloadだけを別payloadへ移す。今回の`assigned`はすでにnon-literalの別payloadなので、この時点の書き換えがcopyを発生させたとは扱わない。

終了経路には`original`、`returned`、`assigned`それぞれについて、nilでなくliteral flagもないpayloadを`deallocShared`する処理が生成された。

## 成果物

- `observed/copy-boundary.md`: pass・return・assignment・mutation・cleanupの対応表
- `observed/generated-c-excerpt.c`: string表現、callee、caller、mutation、cleanupの抜粋
- `observed/runtime-c-excerpt.c`: `eqcopy`、`nimAsgnStrV2`、literal mutation helperの抜粋
- `observed/toolchain-definition-excerpt.nim`: Nim 2.2.10の型、copy、mutation、free定義
- `observed/commands-2026-09-08.txt`: compile、実行、環境確認commandとexit status
- `observed/environment.txt`: compiler、OS、machine、生成target、memory manager、build mode
- `observed/run-2026-09-08.txt`: 実行結果
- `tests/run_experiment.py`: fresh buildと全証拠の検証

## 技術判断と未確認範囲

読者が区別する判断は、string値を構成する`len`とpayload pointer、値引数の構造体copyとpayload copy、戻り値/代入時のnon-literal payload copy、代入時のcopyと後続mutation guard、literalとheap string、3つの独立payloadと3つのcleanupである。

追跡した識別子は`NimStringV2`、`NimStrPayload`、`len`、`p`、`magic: "Asgn"`、`eqcopy`、`nimAsgnStrV2`、`strlitFlag`、`nimPrepareStrMutationV2`、`nimPrepareStrMutationImpl`、`copyMem`、`deallocShared`である。

未確認は、string literal、空string、再代入時のdestination buffer再利用、sink/move、closure/iterator、別memory manager、release、threads無効、C ABI公開、別OS・target・Nim version、allocation回数、性能、Unicodeである。
