# Qwen3.8-27Bを24GB M3 Macで再現する

対応Issue: [#17](https://github.com/asopitech-labs/asmati-lab/issues/17)

## 問い

24GB unified memoryのM3 MacBook Airで、Qwen3.8-27Bの8K〜32Kコンテキスト実行と、記事で示された15〜25 tokens/sの意味を確認する。

## 条件

- MacBook Air、Apple M3、24GB unified memory、10-core GPU
- source-built llama.cpp、Metal、arm64
- `unsloth/Qwen3.8-27B-GGUF` / `UD-Q4_K_XL`
- 測定日: 2026-08-22
- 比較対象: [参照記事](https://x.com/zefirium/status/2089719218493149633?s=20)

モデル本体と17GB超のGGUFは公開しない。取得元、量子化名、SHA-256を記録し、再取得したファイルを使う。

## 観察

- 8KのGPU KVは、`--parallel 1 --batch-size 128 --ubatch-size 64`で動作した。
- 16K／32KのGPU KVはMetal OOMになり、CPU管理KVへの切り替えが必要だった。
- prompt処理は17.83〜24.03 tok/sだったが、generationは1.43〜3.97 tok/sだった。
- 15〜25 tok/sという表示は、今回の条件ではgeneration速度ではなくprompt処理速度として整合した。
- 生成コードは構文解析と機能テストに合格した。

## 制約

M3実機の結果であり、記事のM4実機を再現したものではない。CPU KVで32Kを予約できたが、完全な32K入力の処理までは確認していない。RSSはMetal割り当てや共有ページを完全には表さない。

詳細な測定表は [`observed/REPORT.md`](observed/REPORT.md) を参照。
