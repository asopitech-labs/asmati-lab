# generated CからNimのprocとruntime呼び出しを対応づける

対応Issue: [#64](https://github.com/asopitech-labs/asmati-lab/issues/64)

## 問い

1つのNim procと1つの文字列操作に範囲を限定し、sourceのprocが生成Cのどの関数になり、その関数が文字列生成・追記のためにどのruntime関数を呼ぶかを対応づけられるか確認する。

## 対象

```nim
proc addSuffix(value: string): string =
  value & "!"
```

`addSuffix("nim")`を実行するdebug buildをNim 2.2.10のC backendで生成した。optimized assembly、性能、`echo`の出力経路、allocator内部は対象外とした。

## 実行環境

- 実行日時: 2026-08-28T11:36:18+0900
- OS: macOS 26.6.2 (build 25G83)
- CPU: arm64 / Apple Silicon
- Nim: 2.2.10 (`nim` executableはMach-O x86_64、compiler表示は`MacOSX: amd64`)
- C compiler: Apple clang 21.0.0
- 生成実行ファイル: Mach-O arm64
- Nim memory manager: ORC
- Nim build mode: debug (`opt: none`)

## 再現コマンド

```bash
python3 tests/prepare_outputs.py
nim c --nimcache:observed/nimcache --out:observed/bin/proc_runtime src/proc_runtime.nim
python3 tests/verify_generated_c.py
./observed/bin/proc_runtime
```

リポジトリ共通runnerからはmanifestのargvを同じ順序で実行する。

```bash
python3 tools/experiment_ci.py run 007-nim-proc-runtime-call
```

## 対応結果

| Nim source | 生成C | 次に呼ぶ処理 | 確認した作用 |
| --- | --- | --- | --- |
| `proc addSuffix(value: string): string` | `addSuffix__proc95runtime_u1(NimStringV2 value_p0)` | `rawNewString(value_p0.len + 1)` | 入力長と`!` 1 byte分のcapacityを持つ空の結果文字列を作る |
| `value & "!"` | 同じ生成C関数内 | `appendString(&T1_, value_p0)` | 入力文字列を結果へcopyし、長さと終端zeroを更新する |
| `value & "!"` | 同じ生成C関数内 | `appendString(&T1_, <文字列literal>)` | `!`を結果へcopyし、長さと終端zeroを更新する |
| `return`相当 | `result = T1_; return result;` | なし | `NimStringV2`を値として返す |

生成Cの`appendString`は`copyMem__system_u1755`、`nimCopyMem`を経てC libraryの`memcpy`を呼んだ。`rawNewString`本体は生成された`@psystem.nim.c`側にあり、capacity、先頭の終端zero、長さ0を設定した。

配布toolchain sourceでは、`system.nim`のstring同士の`&`は`ConStrStr` magicとして宣言されていた。`system/strs_v2.nim`には`NimStringV2`、`appendString`、`rawNewString`の定義があり、生成Cで観測した処理と対応した。この配布sourceは実験で生成されたartifactではなく、生成結果の定義を追跡する根拠として抜粋した。

生成された`NimMainModule`が`addSuffix__proc95runtime_u1`を呼ぶことも確認した。`echoBinSafe`以降はsource procからruntime呼び出しを対応づける今回の範囲に含めていない。

## 実行結果

```text
nim!
```

## 生成物

- `src/proc_runtime.nim`: 1 proc・1文字列操作のsource
- `tests/verify_generated_c.py`: source declaration、生成C、配布runtime定義の対応を検査するscript
- `observed/generated-c-excerpt.c`: 生成Cから保存した関係箇所の抜粋
- `observed/runtime-definition-excerpt.nim`: Nim 2.2.10配布sourceから保存した定義抜粋
- `observed/observation-table.md`: source、生成C、runtime callの対応表
- `observed/unmapped-lines.md`: 今回対応づけない生成行と理由
- `observed/compile-2026-08-28.txt`: compile commandと結果
- `observed/run-2026-08-28.txt`: 検証と実行結果
- `observed/environment.txt`: compiler、runtime、実行環境

`observed/bin/`と`observed/nimcache/`は再生成可能なためGit管理対象外である。

## 確認したこと

- Nim sourceの`addSuffix`は、`NimStringV2`を受けて返すprivateな生成C関数`addSuffix__proc95runtime_u1`になった。
- string同士の`&`は、この生成条件では結果用の`rawNewString` 1回と`appendString` 2回に展開された。
- 生成Cの`appendString`はbyte copy、長さ更新、終端zero設定を行った。
- 生成programは`nim!`を出力した。
- 生成CとNim 2.2.10配布sourceの両方を検査することで、観測したruntime識別子の定義まで追跡できた。

## 未確認点

- `addSuffix__proc95runtime_u1`というsuffixの命名規則
- release build、別memory manager、別backend、別Nim versionでの呼び出し構造
- allocator内部とallocation failure時の処理
- `echoBinSafe`からOS出力までの経路
- optimized assemblyと性能
