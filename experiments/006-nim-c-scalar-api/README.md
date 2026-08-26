# Nim libraryをCのscalar APIとして呼び出す

対応Issue: [#54](https://github.com/asopitech-labs/asmati-lab/issues/54)

## 問い

整数と浮動小数点だけに範囲を限定し、Nimのprocを公開C headerとdynamic libraryのsymbolにして、独立したC callerからcompile・link・実行できるかを確認する。

## 対象

- `cint`を2つ受けて`cint`を返す`asmati_add_ints`
- `cdouble`を受けて`cdouble`を返す`asmati_half`
- Nimが生成する`scalar_api.h`
- 公開symbolを含む`libscalar_api.dylib`
- 生成headerだけを通してAPIを呼ぶ`caller.c`

string、ownership、error handlingは対象外とした。

## 実行環境

- 実行日時: 2026-08-26T18:07:53+0900
- OS: macOS 26.5.2 (build 25F84)
- CPU: arm64 / Apple Silicon
- Nim: 2.2.10 (`nim` executableはMach-O x86_64、compiler表示は`MacOSX: amd64`)
- C compiler: Apple clang 21.0.0
- 生成library / C caller: Mach-O arm64
- Nim memory manager: ORC
- Nim build mode: debug (`opt: none`)

## 再現コマンド

```bash
python3 tests/prepare_outputs.py
nim c --app:lib '--passL:-install_name @rpath/libscalar_api.dylib' --header:scalar_api.h --nimcache:observed/nimcache --out:observed/bin/libscalar_api.dylib src/scalar_api.nim
python3 tests/collect_header.py
python3 tests/verify_library.py
python3 tests/build_c_caller.py
python3 tests/verify_caller.py
./observed/bin/c_caller
```

リポジトリ共通runnerからは、manifestのargvを同じ順序で実行する。

```bash
python3 tools/experiment_ci.py run 006-nim-c-scalar-api
```

## C callerの初期化

このmacOS/POSIXの`--app:lib`生成物では、C callerは`NimMain`を明示的に呼ばなかった。生成Cは`NIM_POSIX_INIT`を付けた`NimMainInit`を定義し、その関数内で`NimMain()`を呼んでいた。Nim 2.2.10の`nimbase.h`は、この条件の`NIM_POSIX_INIT`をClang/GCCの`constructor` attributeへ定義していた。

したがって、この実験条件での呼び出し位置はCの`main`内ではなく、dynamic loaderが実行するlibrary constructorである。`nm -u`でC callerが`NimMain`を未定義symbolとして参照していないことも検査した。Windows、static library、別のNim backendへこの判断を一般化していない。

## 生成headerの依存

生成された`scalar_api.h`は`nimbase.h`をincludeする。Nim library directoryをinclude pathへ加えずにC callerをcompileすると、`'nimbase.h' file not found`で失敗した。修正版は`nim dump`から`nimbase.h`のあるdirectoryを見つけ、`clang`へ`-I/usr/local/Cellar/nim/2.2.10/nim/lib`相当を渡した。ローカル絶対pathは再現scriptが実行時に解決するため、manifestには固定していない。

## 実行結果

```text
add(19,23)=42
half(3.5)=1.75
```

`nm -gU`では`_asmati_add_ints`、`_asmati_half`、`_NimMain`を公開symbolとして確認した。C callerは`@rpath/libscalar_api.dylib`へlinkされ、`@loader_path`のruntime search pathで隣接libraryを読み込んだ。

## 生成物

- `src/scalar_api.nim`: exportする最小scalar API
- `src/caller.c`: 生成headerを使う独立C caller
- `tests/`: header保存、toolchain探索、library/caller検証、C caller build
- `observed/scalar_api.h`: Nim 2.2.10が生成した公開header
- `observed/generated_c_excerpt.c`: 公開定義とPOSIX初期化の生成C抜粋
- `observed/nimbase-definition-excerpt.h`: 使用したmacro定義の抜粋
- `observed/symbols-2026-08-26.txt`: dynamic libraryの公開symbol
- `observed/linkage-2026-08-26.txt`: install nameとcaller依存関係
- `observed/compile-link-2026-08-26.txt`: compile/link commandと観測した失敗・成功
- `observed/run-2026-08-26.txt`: C callerの実行結果
- `observed/observation-table.md`: source、header、symbol、callerの対応

`observed/bin/`と`observed/nimcache/`は再生成可能なためGit管理対象外である。

## 確認したこと

- `.exportc, dynlib, cdecl.`を付けた`cint`/`cdouble` procから、`int`/`double`を使うheader宣言とdefault-visibleなdynamic library symbolが生成された。
- 独立したC callerは、そのheaderとlibraryを通して整数関数と浮動小数点関数を呼び出し、期待値を得た。
- 生成header単体では完結せず、macro定義のためNim 2.2.10の`nimbase.h`がcompile時に必要だった。
- このmacOS/POSIX dynamic libraryでは生成されたconstructorが`NimMain`を呼ぶため、C caller内の明示的初期化呼び出しは不要だった。

## 未確認点

- Windows DLLやstatic libraryでの初期化位置とcaller側の必要処理
- release build、別memory manager、別Nim versionでのheader・symbol・初期化差分
- libraryと`nimbase.h`を第三者へ配布するときのversioning・packaging契約
- integer overflow、NaN/Infinityなどscalar APIのfailure semantics
- string、ownership、error handling
