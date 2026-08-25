# Nim scalar procの引数と戻り値を生成Cで確認する

対応Issue: [#28](https://github.com/asopitech-labs/asmati-lab/issues/28)

## 問い

int/floatの引数と戻り値に限定し、Nimのprocシグネチャが生成Cでどの型と関数シグネチャに落ちるかを確認する。

## 対象

- 引数なしで`int`を返す`noArgs`
- `int`を値渡しして`int`を返す`addOne`
- `float`を受けて`float`を返す`half`

## 実行環境

- 実行日時: 2026-08-25T09:05:50+0900
- OS: macOS 26.5.2
- CPU: Apple Silicon
- Nim: 2.2.10
- C compiler: Apple clang 21.0.0
- Nim memory manager: ORC
- Nim build mode: debug (`opt: none`)

## 実行コマンド

```bash
nim c --nimcache:observed/nimcache -o:observed/bin/scalar_proc src/scalar_proc.nim
./observed/bin/scalar_proc
```

リポジトリ共通runnerからは、manifestに宣言したcompile、生成C署名検査、実行出力検査を順に実行する。

```bash
python3 tools/experiment_ci.py run 004-nim-scalar-proc-c-signature
```

## 生成物

- `src/scalar_proc.nim`: 最小の入力コード
- `observed/environment.txt`: versionと実行環境
- `observed/run-2026-08-25.txt`: バイナリ実行結果
- `observed/generated_c_excerpt.c`: 生成Cの該当箇所抜粋
- `observed/observation-table.md`: 観察表

## 観察

- 生成Cの先頭で`NIM_INTBITS 64`が定義され、この条件では`nimbase.h`の`NI`は`NI64`に解決される。
- 同じ`nimbase.h`で`NF`は`double`として定義される。
- macOS/clang条件では`N_NIMCALL`は呼び出し規約修飾子なしの通常C関数になる。
- `noArgs`は`NI func(void)`、`addOne`は`NI func(NI x_p0)`、`half`は`NF func(NF x_p0)`として生成された。
- `addOne`の本体は単純な`x + 1`ではなく`nimAddInt(..., &tmp)`と`raiseOverflow()`を通り、debug buildの整数overflow検査が残っていた。
- `half`の本体は`((NF)(x_p0) / (NF)(2.0))`で、浮動小数点演算は直接C式へ落ちていた。
- 実行結果は`noArgs=7`、`addOne(41)=42`、`half(3.5)=1.75`だった。

## 未確認点

- `int`と`float`がNim内部型`NI`と`NF`を通して、ターゲットごとのC基本型へどう定義されるかの一般化は、この1回の環境では未確認。
- `exportc`や`header`生成時に同じシグネチャが外部ABIとしてどう見えるかは、このIssueでは未確認。
- 最適化後のassemblyやABI上のレジスタ割り当ては見ていない。
