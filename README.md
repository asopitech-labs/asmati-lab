# asmati-lab

アスマティ・辰巳が、実際に触って確かめた技術を公開で蓄積する研究・実験ラボです。

対象は一つの技術領域に限定しません。完成した解説だけでなく、調べ始めた問い、途中の観察、比較できなかった条件、仮説が外れた結果、次に試すことを残します。GitHub Issueを研究ノートとして使い、必要になった実験コードだけを `experiments/` に置きます。

## 使い方

1. まず [Experiment Issue](https://github.com/asopitech-labs/asmati-lab/issues/new?template=experiment.md) または [Question Issue](https://github.com/asopitech-labs/asmati-lab/issues/new?template=question.md) を作る。
2. 問い、試したいこと、仮説または確認したい条件を記録する。
3. 最小のコード・コマンド・設定・実行結果を残す。コードが不要ならIssueだけでよい。
4. 観察できたこと、解釈、未確認のことを分ける。
5. 再現、反証、比較、記事化などの次の一手をIssueやcommitにつなぐ。

Issueは完成原稿でなくて構いません。途中で止まった実験、仮説が外れた実験、まだ比較条件が揃っていない実験も歓迎します。

## 主な対象領域

分類は固定しません。たとえば次のような技術を扱います。

- Nim、Rust、C、C++、Zigなどのプログラミング言語と基本概念
- compiler、runtime、ABI、FFI、生成コード、object、library、package
- Web、desktop、WebView、OS API、GPU、入力、描画、テキスト処理
- CLI、TUI、editor、開発ツール、build system、package manager、toolchain
- framework、library、OSS、database、network、distributed systems
- AI agent、MCP、parser、データ形式、protocol、interoperability
- architecture、debugging、benchmark、再現実験、技術選定、開発方法
- 上記の境界をまたぐ小さな統合や比較

Nim→生成C→ABI/FFIは重要な研究軸の一つですが、このリポジトリ全体をそれだけに限定しません。

## ディレクトリ

```text
experiments/
  <experiment-id>-<topic>/
    README.md
    src/
    expected/
    observed/

.github/ISSUE_TEMPLATE/
```

実験コードは小さく保ちます。ライブラリとしての完成度や本番利用の保証を、このリポジトリの目的にはしません。共通ルールは [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## 記録の原則

- 対象のversion、OS、実行環境、compile option、依存バージョンを可能な範囲で記録する。
- 一回の観察や一つのbenchmarkだけから、性能、安全性、互換性、一般的優位性を断定しない。
- 比較するときは、workload、入力、baseline、測定方法、条件差を残す。
- secret、個人情報、未公開の顧客情報、許可のない外部サービスへの検証を持ち込まない。
- 既存プロジェクトのコードを持ち込む場合は、ライセンスと公開範囲を確認する。
- Issue、commit、コードの粒度は荒くてよい。ただし、後から問いと観察を追えるようにする。

## 研究から教材へ

このリポジトリのIssueと実験コードは、将来の技術記事・教材の原料です。公開記事へ昇格するときは、必要な証拠と制約を整理し、「予想 → 実験 → 観察 → 比較 → 制約 → 演習」の形へ編集します。