# Evaluation method

- pass@1として、同一条件で1つ生成し、説明文ではなくPythonファイルを実行する。
- 公開テストと、仕様から導いた追加テストを別プロセスで実行する。
- 修正を促した生成物は `repair_used` として記録し、初回成功とは分ける。
- 速度とメモリは副指標であり、テスト不合格の生成物を合格にしない。
- モデル出力を信頼せず、`python -I`相当の隔離、タイムアウト、固定条件で検証する。

実行例:

```bash
python3 -m unittest discover -s tests -v
```

このディレクトリの `expected/generated_ttl_cache.py` は、3回の生成で同一ハッシュになった代表成果物である。
