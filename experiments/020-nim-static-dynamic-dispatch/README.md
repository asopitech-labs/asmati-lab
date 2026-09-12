# Issue #45: static dispatchとdynamic dispatchの呼び出しを比較する

## 問い

基底型`Animal`として保持した`Dog`に同じ計算を`proc`と`method`で適用すると、Nim 2.2.10の生成Cで呼び出し先選択はどう異なるか。methodのfunction table相当は、今回の条件で実際にどの生成物として現れるか。

この実験はNim内部のprivateな生成Cを観察する。大規模class設計、性能、公開C ABIへ範囲を広げない。

## 入力sourceと実行経路

`src/static_dynamic_dispatch.nim`は`RootObj → Animal → Dog`の2段階のobject型を定義する。`staticScore(Animal)`は通常proc、`dynamicScore(Animal)`はbase method、`dynamicScore(Dog)`は1つのoverrideである。

実体が`Dog`、静的な参照型が`Animal`である同じ値を、`callStatic`と`callDynamic`へ渡す。基底型側は`id + 100`、派生型側は`id + bonus`を返すため、呼び出し先を実行値でも区別できる。

## 再現

macOS、Nim 2.2.10、Apple Clang、Python 3が必要。リポジトリrootから実行する。

```sh
python3 tools/experiment_ci.py validate
python3 -m unittest discover -s tools/tests -p 'test_*.py'
python3 tools/experiment_ci.py run 020-nim-static-dynamic-dispatch
```

実験directoryからは次で再実行できる。

```sh
python3 tests/run_experiment.py
```

scriptはbinaryをfresh buildし、procの直接呼び出し、method dispatcher、実型metadataによる分岐、callee、実行結果を検証する。binaryとnimcacheは`observed/bin/`と`observed/nimcache/`へ生成し、gitへ保存しない。通常実行は保存観測を上書きせず、`--record`だけが明示的に保存する。

## 実測結果（2026-09-12 UTC）

Nim 2.2.10 / ORC / debug / threads on / method既定設定、Apple Clang、macOSの64-bit targetで実行した。

```text
static=105
dynamic=12
```

`callStatic(Animal)`は`staticScore(Animal)`を直接呼び、基底型procの`id + 100`を実行した。`callDynamic(Animal)`はmethod dispatcherを呼び、実体Dogのtype descriptorを検査して`dynamicScore(Dog)`へ進み、`id + bonus`を実行した。

## 生成Cの観察

static側のcall wrapperからcalleeへの辺は1本で、呼び出し先選択の分岐はない。

dynamic側のcall wrapperは、base methodやoverrideを直接呼ばず、同じ`Animal*`をmethod dispatcherへ渡す。dispatcherはnil checkの後に`animal.Sup.m_type`を読み、まずDogのdepth 2 / class tokenを`isObjDisplayCheck`で検査してDog用methodを呼ぶ。続いてAnimalのdepth 1 / class tokenを検査し、base methodをfallbackとして呼ぶ。

生成された`TNimTypeV2`には`vTable`欄がある。一方、今回のDog descriptor initializerは`.vTable`を明示初期化せず、この生成単位に`vTable` slotの設定または参照はなかった。したがって、この条件で観察できたfunction table相当の呼び出し先対応は、vTable lookupではなく、type descriptorのdepth/display tokenと直接calleeを対応づける分岐dispatcherである。

## 成果物

- `observed/dispatch-table.md`: Nim呼び出し、生成C入口、type条件、callee、実行値
- `observed/generated-c-excerpt.c`: object型、descriptor、static call、method dispatcher、各callee
- `observed/toolchain-definition-excerpt.nim`: `TNimTypeV2`と`isObjDisplayCheck`のNim 2.2.10定義
- `observed/commands-2026-09-12.txt`: build、実行、環境確認command
- `observed/environment.txt`: compiler、OS、machine、生成target、memory manager、build mode
- `observed/run-2026-09-12.txt`: binary targetと実行結果
- `tests/run_experiment.py`: fresh buildと全証拠の検証

## 技術判断と未確認範囲

読者が区別する判断は、静的な参照型と実体型、procの直接callとmethod dispatcherへのcall、type descriptorとcallee、型metadata内の`vTable`欄と実際のvTable使用、dispatcherの派生型分岐とbase fallbackである。

追跡した識別子は`Animal`、`Dog`、`staticScore`、`dynamicScore`、`callStatic`、`callDynamic`、`RootObj.m_type`、`TNimTypeV2`、`depth`、`display`、class token、`isObjDisplayCheck`、`chckNilDisp`、`vTable`である。

未確認は、base実体のfallback実行、nil receiver、複数override、複数引数method、`--multimethods`、release、ARC・refc・tracing GC、C++ backend、別OS・target・compiler・Nim version、公開C ABI、性能である。
