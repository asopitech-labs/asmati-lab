# Nim ref procのポインタとnil条件を生成Cで確認する

対応Issue: [#29](https://github.com/asopitech-labs/asmati-lab/issues/29)

## 問い

`ref object`をprocの引数・戻り値にしたとき、objectのfield、参照のpointer、nil判定、fieldアクセスが生成Cでどう表現されるかを確認する。

## 対象

- `Reading = ref object`と`value: int` field
- `Reading`を受け取り、nilなら`-1`、非nilならfield値を返す`readValue`
- `Reading`を受け取り、同じ`Reading`を返す`keepReading`
- 値を持つ参照とnil参照の実行結果

## 実行環境

- 実行日時: 2026-08-26T09:03:06+0900
- OS: macOS 26.5.2 (build 25F84)
- CPU: arm64 / Apple Silicon
- Nim: 2.2.10 (`nim` executableはMach-O x86_64)
- C compiler: Apple clang 21.0.0
- 生成binary: Mach-O 64-bit executable arm64
- Nim memory manager: ORC
- Nim build mode: debug (`opt: none`)

`nim --version`はcompiler targetを`MacOSX: amd64`と表示し、`nim` executable自体もx86_64だった。一方、`uname -m`と生成binaryはarm64だった。この実験はRosetta上のNim compilerがarm64 nativeのclangを起動した条件として、両方をenvironmentへ記録した。

## 実行コマンド

```bash
nim c --nimcache:observed/nimcache -o:observed/bin/ref_proc src/ref_proc.nim
./observed/bin/ref_proc
```

リポジトリ共通runnerからは、manifestに宣言したcompile、生成C検査、実行出力検査を順に実行する。

```bash
python3 tools/experiment_ci.py run 005-nim-ref-proc-pointer-nil
```

## 生成物

- `src/ref_proc.nim`: 最小の入力コード
- `tests/verify_generated_c.py`: 生成Cの型、シグネチャ、nil分岐、field access、ref returnを検査する
- `observed/environment.txt`: version、実行環境、command
- `observed/compile-2026-08-26.txt`: compile結果
- `observed/run-2026-08-26.txt`: バイナリ実行結果
- `observed/generated_c_excerpt.c`: 生成Cの該当箇所抜粋
- `observed/observation-table.md`: sourceと生成Cの対応表

## 観察

- `Reading`のfield本体は`NI value`を持つC structになり、Nimの`ref`はそのstructへのpointerとしてprocへ渡された。
- `readValue`は`NI`を返し、`Reading* reading_p0`を受ける関数になった。
- `reading.isNil`は`reading_p0 == 0`というnull比較になり、field accessは非nil側の`(*reading_p0).value`に置かれた。
- `keepReading`の引数と戻り値はどちらも`Reading*`になった。
- `keepReading`は戻り値を`NIM_NIL`で初期化し、ORCの`eqcopy`補助を呼んでからpointerを返した。
- 実行結果は、値を持つ参照で`present=42`、nil参照で`missing=-1`、nilを返した結果で`keptIsNil=true`だった。

## 未確認点

- ARC、refc、mark-and-sweepなど別のmemory managerで生成Cがどう変わるかは確認していない。
- `exportc`、header生成、外部C callerは対象外であり、この生成Cシグネチャを安定したFFI契約としては確認していない。
- release最適化後のC、assembly、ABI上のレジスタ割り当ては確認していない。
- x86_64のNim compiler executableとarm64の生成binaryというtoolchain構成が、別環境の生成Cへ影響するかは未確認。
