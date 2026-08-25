# Experiments

ここには、Issueで始めた実験のうち、再実行しやすい最小コードを置きます。

## 命名

`<experiment-id>-<topic>/` の形式にします。例:

```text
001-nim-closure-c-lowering/
```

各実験には、可能なら次を置きます。

- `experiment.json`: CI実行可否、toolchain、再現step、確認するartifact
- `README.md`: 問い、環境、実行方法、観察結果
- `src/`: 入力となる最小コード
- `expected/`: 実験前の予想や比較用の入力
- `observed/`: 生成C、diff、ログなどの再確認に必要な成果物

生成物を置くこと自体を目的にせず、何を確認するためのファイルかをREADMEに書きます。

## 共通CI契約

すべての実験ディレクトリに`experiment.json`を置きます。CIはmanifestの構造とartifactの存在を常に検証し、`ci.mode`が`automated`の実験だけを実行します。外部機器、ローカルモデル、特定GPUなどGitHub-hosted runnerで再現できない実験は`manual`とし、実行できない理由を必須で残します。

```bash
python3 tools/experiment_ci.py validate
python3 tools/experiment_ci.py run 003-q4-local-codegen-ttl-cache
```

Pull Requestでは変更された実験だけを選びます。manifest schema、共通runner、workflow、そのテストが変わった場合は、すべての`automated`実験を再実行します。各stepはshell文字列ではなくargv配列として実行されるため、pipeやリダイレクトが必要な検証は専用scriptへ切り出します。
