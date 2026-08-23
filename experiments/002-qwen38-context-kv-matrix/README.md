# Qwen3.8-27Bのコンテキスト長とKV配置の境界

対応Issue: [#18](https://github.com/asopitech-labs/asmati-lab/issues/18)

## 問い

24GB M3 MacでQ4_K_M量子化モデルを使い、入力長、生成長、KV cacheの配置が実行可能性と速度にどう影響するかを測る。

## 条件

- MacBook Air、Apple M3、24GB unified memory、10-core GPU
- `bartowski/Qwen3.8-27B-GGUF` / `Qwen3.8-27B-Q4_K_M.gguf`
- source-built llama.cpp `llama-bench`、Metal、flash attention
- build commit: `1719747`
- 測定日: 2026-08-22

モデル本体は公開せず、取得元、ファイル名、SHA-256だけを記録する。

## 結果

- 入力128／2048では全層Metal＋GPU F16 KVが成功した。
- 入力8192ではGPU F16 KV、GPU Q8 KVとも確保に失敗した。
- 入力8192は、全層MetalのままCPU F16 KV（`--no-kv-offload`）にすると生成64／256／1024の全ケースが成功した。
- 実生成ではprompt 22.0〜24.3 tok/s、generation 4.8〜4.9 tok/sだった。
- 8192入力・1024生成は約895秒を要し、動作可能と実用的な速度は別である。

詳細な境界とメモリ計測は [`observed/REPORT.md`](observed/REPORT.md) を参照。
