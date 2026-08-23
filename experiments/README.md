# Experiments

ここには、Issueで始めた実験のうち、再実行しやすい最小コードを置きます。

## 命名

`<experiment-id>-<topic>/` の形式にします。例:

```text
001-nim-closure-c-lowering/
```

各実験には、可能なら次を置きます。

- `README.md`: 問い、環境、実行方法、観察結果
- `src/`: 入力となる最小コード
- `expected/`: 実験前の予想や比較用の入力
- `observed/`: 生成C、diff、ログなどの再確認に必要な成果物

生成物を置くこと自体を目的にせず、何を確認するためのファイルかをREADMEに書きます。
