# debug/releaseで整数overflow処理を比較する

対応Issue: [#78](https://github.com/asopitech-labs/asmati-lab/issues/78)

## 問い

同一の整数加算procをdebug buildと`-d:release` buildで生成したとき、generated Cのoverflow helper・検査分岐と、通常値・overflow境界値の実行結果がどう変わるかを確認する。

## 対象

```nim
proc addOne(value: int): int {.noinline.} =
  value + 1
```

command lineから整数を読み、`addOne`へ渡す。`noinline`はrelease buildでも対象関数を独立したgenerated C関数として残すために指定した。通常値は`41`、overflow境界値は64-bit `int`の上限`9223372036854775807`とした。

浮動小数点、range/bounds check、別target/compiler/Nim version、assembly、性能は対象外とした。

## 実行環境

- 実行日時: 2026-08-29T19:04:55+0900
- OS: macOS 26.6.2 (build 25G83)
- CPU: arm64 / Apple Silicon
- Nim: 2.2.10 (`nim` executableはMach-O x86_64、compiler表示は`MacOSX: amd64`)
- C compiler: Apple clang 21.0.0
- 生成実行ファイル: debug/releaseともMach-O arm64
- backend: C
- memory manager: ORC
- debug: `opt: none`
- release: `opt: speed; options: -d:release`、generated CのClang commandは`-O3`

## 再現コマンド

```bash
python3 tests/prepare_outputs.py
nim c --nimcache:observed/nimcache/debug --out:observed/bin/debug/overflow_compare src/overflow_compare.nim
nim c -d:release --nimcache:observed/nimcache/release --out:observed/bin/release/overflow_compare src/overflow_compare.nim
python3 tests/verify_generated_c.py
python3 tests/run_cases.py
```

リポジトリ共通runnerからはmanifestのargvを同じ順序で実行する。

```bash
python3 tools/experiment_ci.py run 008-nim-debug-release-overflow
```

## 観察

debugとreleaseの`addOne`は、どちらも次のoverflow検査を生成した。

```c
if (nimAddInt(value_p0, ((NI)1), &temporary)) {
  raiseOverflow();
  goto BeforeRet_;
}
```

Nim 2.2.10の`nim.cfg`で`release or danger`に共通する設定はstack/line traceの無効化、`opt:speed`、`define:release`であり、`overflow_checks:off`は含まれていなかった。`overflow_checks:off`は別の`danger or quick` blockにあった。したがって、このtoolchainでは`-d:release`とoverflow check無効化は同じ設定ではない。

64-bit条件の`nimAddInt`は、Nim 2.2.10の`nimbase.h`でClang/GCC builtinの`__builtin_saddll_overflow`へ定義されていた。overflow時の`raiseOverflow`はgenerated `@psystem.nim.c`で`sysFatal`へ接続され、`OverflowDefect`を報告した。

releaseで変わった対象関数内の観測点は、加算処理そのものではなくdebug frame bookkeepingだった。debugには`nimfr_`、`nimlf_`、`popFrame`があり、releaseでは削除された。その結果、境界値のdebug stderrには`addOne`のsource frameがあり、release stderrにはなかった。

## 実行結果

```text
debug normal: exit=0 stdout=42
release normal: exit=0 stdout=42
debug boundary: exit=1 overflow_defect=true add_one_frame=true
release boundary: exit=1 overflow_defect=true add_one_frame=false
```

## 生成物

- `src/overflow_compare.nim`: 同一の整数加算procとruntime入力
- `tests/verify_generated_c.py`: 両buildのgenerated C、Nim config、helper定義を検証
- `tests/run_cases.py`: 通常値・境界値のexit status、出力、frame差を検証
- `observed/generated-c-excerpt.c`: 両buildの対象関数抜粋
- `observed/generated-c-diff.txt`: 対象関数とC compiler optionの差
- `observed/nim-config-excerpt.txt`: release/danger設定のNim 2.2.10抜粋
- `observed/nimbase-overflow-excerpt.h`: `nimAddInt`定義のNim 2.2.10抜粋
- `observed/observation-table.md`: build、generated C、実行結果の対応
- `observed/compile-2026-08-29.txt`: compile commandと結果
- `observed/run-2026-08-29.txt`: 検証済み4ケース
- `observed/environment.txt`: compiler、runtime、実行環境

`observed/bin/`と`observed/nimcache/`は再生成可能なためGit管理対象外である。

## 確認したこと

- Nim 2.2.10のこの条件では、`-d:release`でも整数加算のoverflow checkは残った。
- debug/releaseの両方が`nimAddInt`と`raiseOverflow`を生成した。
- debug/releaseの両方が通常値`41`へ`42`を返した。
- debug/releaseの両方が`high(int) + 1`を`OverflowDefect`としてexit 1で終了した。
- releaseは`-O3`を使い、対象関数からdebug frame bookkeepingを除いたが、overflow分岐は除かなかった。
- build profileと個別runtime check optionは分けて確認する必要がある。

## 未確認点

- `-d:danger`または明示的`--overflowChecks:off`のgenerated Cと実行結果
- 減算・乗算・underflowの経路
- 別target、別C compiler、別Nim versionでのhelper定義
- 最適化後assemblyと性能
