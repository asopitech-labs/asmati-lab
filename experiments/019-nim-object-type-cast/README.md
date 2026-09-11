# Issue #44: objectのtype identificationとcast条件を観察する

## 問い

基底型`Animal`として受け取った`Dog`と`Cat`の実型判定は、Nim 2.2.10の生成Cでどのmetadataと分岐になるか。判定に一致するobject conversionと、一致しないconversionの実行結果はどう異なるか。

この実験はNim内部のprivateな生成Cとruntime helperを観察する。安全性の一般化、dynamic dispatch、公開C ABIへ範囲を広げない。

## 入力sourceと実行経路

`src/object_type_cast.nim`は`RootObj → Animal → Dog/Cat`の継承関係を定義する。正常buildでは次を実行する。

- `Dog`実体を持つ`Animal`に対する`of Dog`
- `Cat`実体を持つ`Animal`に対する`of Dog`
- `of`で実型を分けた後の`Dog(animal)`と`Cat(animal)`
- `Dog`実体に対する直接の`Dog(animal)`

同じsourceを`-d:forceFailedCast`でもbuildし、`Cat`実体へ直接`Dog(animal)`を実行する。正常・失敗を別binaryと別nimcacheへ保存する。

## 再現

macOS、Nim 2.2.10、Apple Clang、Python 3が必要。リポジトリrootから実行する。

```sh
python3 tools/experiment_ci.py validate
python3 -m unittest discover -s tools/tests -p 'test_*.py'
python3 tools/experiment_ci.py run 019-nim-object-type-cast
```

実験directoryからは次で再実行できる。

```sh
python3 tests/run_experiment.py
```

scriptは2 binaryをfresh buildし、型descriptor、objectの`m_type`設定、display token、`isObjDisplayCheck`、正常castのfield access、失敗分岐、実行結果を検証する。binaryとnimcacheは`observed/bin/`と`observed/nimcache/`へ生成し、gitへ保存しない。通常実行は保存観測を上書きせず、`--record`だけが明示的に保存する。

## 実測結果（2026-09-11 UTC）

Nim 2.2.10 / ORC / debug / object checks既定値、Apple Clang、macOSの64-bit targetで実行した。

正常build:

```text
dogOfDog=true
catOfDog=false
dogResult=7
catResult=-9
forcedDog=7
```

失敗buildは、有効な判定後castで`checkedDog=7`を出力した後、`Cat`実体に`Dog(animal)`を適用し、`invalid object conversion [ObjectConversionDefect]`で非zero終了した。

## 生成Cとruntimeの観察

生成Cでは`RootObj`が`TNimTypeV2* m_type`を持つ。`Animal`は`RootObj Sup`、`Dog`と`Cat`はそれぞれ`Animal Sup`を先頭に持つ。Dog/Cat実体の生成時には、各型descriptorのaddressが`Sup.Sup.m_type`へ設定された。

DogとCatの`TNimTypeV2` descriptorはいずれもdepth 2と3要素のdisplay配列を持った。配列の0・1番要素は共通、2番要素のclass tokenは型ごとに異なった。

`isObjDisplayCheck`は、要求depthが実型descriptorのdepth以下であることと、要求depthのdisplay tokenが対象tokenと一致することを検査した。`of`の不一致はfalse分岐となる。object conversionにも同じ検査が入り、不一致時には`raiseObjectConversionError`から`ObjectConversionDefect`へ進んだ。一致時だけDog/Cat pointerへC castして各fieldを読んだ。

## 成果物

- `observed/type-check-table.md`: 実型、判定・cast、結果、生成C条件
- `observed/generated-c-excerpt.c`: 継承struct、型descriptor、`m_type`設定、型判定・正常cast
- `observed/failed-cast-c-excerpt.c`: 不正cast検査と失敗helper
- `observed/toolchain-definition-excerpt.nim`: `TNimTypeV2`、display検査、conversion error、defect定義
- `observed/commands-2026-09-11.txt`: 2 build、正常・失敗実行、環境確認command
- `observed/environment.txt`: compiler、OS、machine、生成target、memory manager、build mode
- `observed/run-2026-09-11.txt`: 正常・失敗実行結果
- `tests/run_experiment.py`: fresh buildと全証拠の検証

## 技術判断と未確認範囲

読者が区別する判断は、静的な基底参照型と実体の型descriptor、`of`のfalseとobject conversionのdefect、型判定と判定後のC pointer cast、継承用`Sup`と`m_type`、private runtime metadataと公開C ABIである。

追跡した識別子は`RootObj`、`Animal`、`Dog`、`Cat`、`Sup`、`m_type`、`TNimTypeV2`、`depth`、`display`、class token、`isObjDisplayCheck`、`raiseObjectConversionError`、`ObjectConversionDefect`、`identify`、`forceDog`である。

未確認は、nil参照、3段以上の継承、sibling以外のcast、object checks無効、release、ARC・refc・tracing GC、dynamic dispatch・vTable、型名metadata、別backend・OS・target・compiler・Nim version、公開C ABIである。
