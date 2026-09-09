# Issue #50: seqのcapacity拡張とappendを観察する

## 問い

空の`seq[int]`へ要素を一つずつappendしたとき、lengthとcapacityはどう変わるか。生成Cのappend条件は、Nim 2.2.10 runtimeの初回payload確保と既存payload再確保へどう接続されるか。

この実験はNim内部のprivateな生成C関数とruntime helperを観察する。要素型は`int`だけとし、benchmark、allocatorの優劣、公開C ABI、複合要素のcopy/destructorへ範囲を広げない。

## 入力source

`src/seq_capacity.nim`は空の`seq[int]`へ1から10までを一つずつ`add`する。初期状態と各append後に`len`、公開`capacity`、全要素の合計を出力する。

## 再現

macOS、Nim 2.2.10、Apple Clang、Python 3が必要。リポジトリrootから実行する。

```sh
python3 tools/experiment_ci.py validate
python3 -m unittest discover -s tools/tests -p 'test_*.py'
python3 tools/experiment_ci.py run 017-nim-seq-capacity-append
```

実験directoryからは次で再実行できる。

```sh
python3 tests/run_experiment.py
```

scriptはfresh buildを行い、保存済みのNim定義、生成C、runtime helper、capacity列、binary targetを検証する。binaryとnimcacheは`observed/bin/`と`observed/nimcache/`へ生成し、gitへ保存しない。通常実行は保存観測を上書きせず、`--record`だけが明示的に保存する。

## 実測結果（2026-09-09 UTC）

Nim 2.2.10 / ORC / debug、Apple Clang、macOSで実行した。compiler、OS、machine、生成targetは`observed/environment.txt`へ保存する。

```text
step=0 len=0 cap=0 total=0
step=1 len=1 cap=1 total=1
step=2 len=2 cap=2 total=3
step=3 len=3 cap=4 total=6
step=4 len=4 cap=4 total=10
step=5 len=5 cap=8 total=15
step=6 len=6 cap=8 total=21
step=7 len=7 cap=8 total=28
step=8 len=8 cap=8 total=36
step=9 len=9 cap=16 total=45
step=10 len=10 cap=16 total=55
```

空seqのcapacityは0だった。初回appendではcapacity 1のpayloadが作られた。以降は不足時に1→2→4→8→16と拡張し、空きがあるstep 4、6、7、8、10ではcapacityが変わらなかった。

## 生成Cとruntimeの観察

生成Cのseqは`len`とpayload pointerを持ち、payloadは`cap`と`data`を持つ。公開`capacity`はpayloadがnilなら0を返し、非nilならliteral flagを除いた`p.cap`を返す。

今回具体化された`add(seq[int], int)`は、append前の`oldLen`を読み、payloadがnilまたは`cap < oldLen + 1`のときだけ`prepareSeqAddUninit(oldLen, p, 1, 8, 8)`を呼ぶ。その後で`len = oldLen + 1`とし、`data[oldLen]`へ要素を書く。

`prepareSeqAddUninit`はpayloadがnilなら要求長`len + addlen`で`newSeqPayloadUninit`を呼ぶ。既存payloadでは`newCap = max(resize(oldCap), len + addlen)`を計算する。今回のnon-literal payloadは`alignedRealloc`へ進み、`cap`を`newCap`へ更新した。`resize`はこの範囲の正capacityを2倍にするため、実行時の2、4、8、16と一致した。

`alignedRealloc`は今回の`int` alignment 8が`MemAlign`以下で、threads有効条件の`reallocShared`へ接続された。ただしreallocが同じaddressを返すか別addressを返すかは測定していない。capacity拡張と物理address移動を区別する。

終了経路には、non-literal seq payloadを`alignedDealloc`する処理が生成された。

## 成果物

- `observed/capacity-table.md`: appendごとのlength、capacity、合計
- `observed/generated-c-excerpt.c`: seq/payload表現、capacity、caller、cleanupの抜粋
- `observed/runtime-c-excerpt.c`: 具体化されたappend、初回確保、再確保helperの抜粋
- `observed/toolchain-definition-excerpt.nim`: Nim 2.2.10のseq型、capacity、add、resize、確保定義
- `observed/commands-2026-09-09.txt`: compile、実行、環境確認commandとexit status
- `observed/environment.txt`: compiler、OS、machine、生成target、memory manager、build mode
- `observed/run-2026-09-09.txt`: 実行結果
- `tests/run_experiment.py`: fresh buildと全証拠の検証

## 技術判断と未確認範囲

読者が区別する判断は、lengthとcapacity、初回payload確保と既存payload再確保、capacity拡張と物理address移動、append条件とallocator処理、公開`capacity`の値とprivate生成C/runtime実装である。

追跡した識別子は`NimSeqV2`、`NimSeqPayload`、`len`、`cap`、`data`、`capacity`、`AppendSeqElem`、`prepareSeqAddUninit`、`newSeqPayloadUninit`、`resize`、`alignedRealloc`、`reallocShared`、`alignedDealloc`である。

未確認は、literal seq、`newSeqOfCap`、複数要素append、shrink/setLen、empty append、物理address移動、allocator内部、複合要素とdestructor、別memory manager、release、threads無効、32-bit、別OS・target・Nim version、公開C ABI、benchmarkである。
