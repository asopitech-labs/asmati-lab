# asmati-lab

アスマティ・辰巳の言語実装・コンパイラ・ABI・FFI実験場です。

完成した解説だけでなく、調べ始めた問い、途中の観察、比較できなかった条件、次に試すことを公開で蓄積します。GitHub Issueを研究ノートとして使い、必要になった実験コードだけを `experiments/` に置きます。

## 使い方

1. まず [Experiment Issue](https://github.com/asopitech-labs/asmati-lab/issues/new?template=experiment.md) を作る。
2. 問いと仮説を一つに絞り、最小のコード・コマンド・観察結果を記録する。
3. 生成物（C、object、library、assemblyなど）が重要なら、再確認できる形で残す。
4. 結論を急がず、観察できたこと・推測・未確認を分ける。
5. 再現、反証、別方式との比較を次のIssueやcommitへつなぐ。

Issueは完成原稿でなくて構いません。途中で止まった実験、仮説が外れた実験、まだ比較条件が揃っていない実験も歓迎します。

## 主な研究軸

- Nimの高水準概念と生成C
- compiler、runtime、object、library
- ABIとFFI
- Nimで生成したmodule/libraryの他言語利用
- Rust、C、C++、Zigとの概念・生成物比較
- 高水準言語が低水準の実行モデルへ落ちる過程

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

実験コードは小さく保ちます。ライブラリとしての完成度や本番利用を、このリポジトリの目的にはしません。

## 記録の原則

- compiler version、OS、compile option、依存バージョンを可能な範囲で記録する。
- 生成Cを見ただけで性能、安全性、lifetime、ABI互換性を断定しない。
- secret、個人情報、未公開の顧客情報を置かない。
- 既存プロジェクトのコードを持ち込む場合は、ライセンスと公開範囲を確認する。
- Issue、commit、コードの粒度は荒くてよい。ただし、後から問いと観察を追えるようにする。

## 研究から教材へ

このリポジトリのIssueと実験コードは、将来の技術記事・教材の原料です。公開記事へ昇格するときは、別途「予想 → 生成 → diff → 解説 → 演習」の形に編集し、この記事だけで確認できる証拠と制約を整理します。
