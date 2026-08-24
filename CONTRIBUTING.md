# asmati-lab 使用ルール

このリポジトリは、アスマティ・辰巳が技術を実際に調べ、試し、失敗し、考え直す過程を公開で蓄積するためのラボです。完成品だけを置く場所ではありません。

## 1. 扱うテーマ

言語実装、コンパイラ、ABI、FFIに限定しません。プログラミング言語、runtime、framework、library、OSS、toolchain、build、CLI/TUI、editor、Web・desktop・OS API、GPU、database、network、distributed systems、AI agent、parser、protocol、debugging、benchmark、architecture、技術選定など、アスマティの技術探究に関係するものを扱えます。

テーマが広くても、一つのIssueでは問い・観察・比較対象を絞ります。

## 2. Issueを先に作る

原則として、コードを書く前にIssueを作ります。

- 実験は [Experiment Issue](https://github.com/asopitech-labs/asmati-lab/issues/new?template=experiment.md) から始める。
- 実験前の疑問や、結果への質問は [Question Issue](https://github.com/asopitech-labs/asmati-lab/issues/new?template=question.md) に残す。
- Issueの本文は粗くてよい。空欄や「未確認」を残して開始してよい。
- 実験が失敗しても、Issueを消さず、何を試してどこで止まったかを追記する。
- 一つのIssueに複数の大きな問いを詰め込まず、必要なら関連Issueへ分ける。

Issueは公開物です。公開できない内容をIssueに書かないでください。

## 3. 最低限残す記録

小さなメモではすべてを埋めなくても構いませんが、可能な範囲で次を残します。

- 問い、目的、仮説または確認したい条件
- 対象version、OS、実行環境、依存、設定
- 実行したコマンド、入力、コード、参照したcommitや資料
- 観察結果、生成物、ログ、スクリーンショット
- 観察から言えること
- 未確認、制約、再現できなかった条件
- 次に試すこと

「観察した事実」「そこからの解釈」「まだ分からないこと」を同じ文章で混ぜないようにします。

## 4. 実験コードの置き方

再実行しやすいコードは、次の形式で置きます。

```text
experiments/<experiment-id>-<topic>/
  README.md
  src/
  expected/
  observed/
```

- `README.md`に問い、環境、実行方法、結果を記録する。
- コードは最小限にする。製品コードや完成ライブラリへ育てる必要はない。
- 生成C、object、library、assembly、ログなどは、何を確認するためのファイルかREADMEに書く。
- 大きなバイナリや再生成できるcacheはcommitしない。必要なら生成手順と保存先を記録する。
- 実験同士の共通化は、複数回必要になってから行う。

## 5. 主張と証拠

アスマティの技術記録では、条件を外した断定を避けます。

- 一回の実行結果を一般的な性能・安全性・互換性の証明にしない。
- benchmarkにはworkload、入力、version、baseline、測定方法、回数、機械差を残す。
- 外部OSSやframeworkを扱うときは、確認したversion・commit・Issue・ドキュメントを示す。
- 生成物から読み取った事実と、実行していない推測を分ける。
- 不明な値は推測で埋めず、「未確認」と書く。
- 不利な結果、未実装、向かない条件、別方式の優位性を隠さない。

## 6. commit、Issue、Pull Request

このリポジトリはスクラッチに近い運用です。

- 小さな実験のcommitは、Issueに紐づけて直接mainへ積んでよい。
- 複数の実験へ影響するルール変更や大きな整理はPull Requestを使う。
- 失敗した実験の記録を、きれいに見せるために書き換えたり削除したりしない。訂正は追記commitまたは後続Issueで行う。
- Issueは未完了のまま開いておいてよい。問いが解決、保留、別Issueへ移管されたときに状態を更新する。
- commit messageは短く具体的にする。例: `experiment: Nim closureの生成Cを比較`、`docs: runtimeの未確認点を追記`。

## 7. 公開・安全・ライセンス

- secret、token、credential、個人情報、未公開の顧客情報をcommit・Issueへ置かない。
- 外部サービス、OSS、benchmark対象へ負荷をかける実験は、許可された範囲で行う。
- 既存コード、画像、ログ、データを持ち込むときは、ライセンスと公開範囲を確認する。
- 実験結果を製品仕様、性能保証、セキュリティ保証、顧客事例として扱わない。
- このリポジトリは教材、講座、製品、営業導線、収益化計画を定義する場所ではない。
- 研究ログを別の公開物や内部計画で利用するときは、元Issue・commit・実行条件を参照し、目的・受け手・責任範囲・評価を独立して定義する。

## 8. このラボの完成条件

すべての実験が結論に到達する必要はありません。次のどれかが残れば一つの実験は成立します。

- 再現できる観察
- 仮説が外れた理由
- 条件付きの比較
- 未確認点と次の実験
- 別の技術判断につながる問い

短く言えば、**完成度より、問い・条件・観察・未確認点が後から追えることを優先します。**