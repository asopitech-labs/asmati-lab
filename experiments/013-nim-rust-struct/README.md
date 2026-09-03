# Issue #56: Nim libraryをRust repr(C) structで呼び出す

## 問いと範囲

2つの整数を持つstructをNimの公開C ABIへ値渡しし、Rust callerでscalarの結果を受け取れるか。Issue #68のlayout比較だけでは未確認だった実際の関数呼び出しを、Issue #54の公開scalar APIに接続する。今回は2つの`cint`を持つ`AsmatiPair`と、加算結果を`cint`で返すAPIに限定する。

## sourceと契約

- `src/pair_api.nim`は実験の入力。`AsmatiPair`へ`exportc`と`bycopy`、fieldへ公開指定を付ける。scalar版`asmati_add`とstruct版`asmati_sum_pair`へ`exportc`、`dynlib`、`cdecl`を指定する。
- `observed/nimcache/pair_api.h`はNimが生成するheader。保存コピーは`observed/pair_api.h`であり、手書きheaderではない。`AsmatiPair`は`int left; int right;`の順で、struct版の引数は`AsmatiPair pair_p0`、戻り値は`int`となった。
- `src/c_caller.c`は生成headerを直接includeし、Cのsize/alignment/offsetと実呼び出しを検証する。
- `src/rust_caller.rs`は`#[repr(C)]`の独立したmirror宣言。fieldとscalar関数は`std::ffi::c_int`、外部関数は`unsafe extern "C"`で宣言する。RustはこのC headerを自動的には読まない。

`repr(C)`が指定するデータ配置と、`extern "C"`が指定する関数呼び出しのABIは別の役割である。今回のRust unsafe blockの前提は、生成headerと一致する宣言、全fieldの初期化、結果がC intへ収まる入力、同一target、ロード済み・初期化済みlibraryである。pointerを渡さず、Rustの所有権やNim管理objectの移転は行わない。

## 再現

macOS、Nim 2.2.10、Clang、Rust 2024 edition対応toolchain、Python 3が必要。リポジトリrootから共通runnerを使う。

```sh
python3 tools/experiment_ci.py validate
python3 -m unittest discover -s tools/tests -p 'test_*.py'
python3 tools/experiment_ci.py run 013-nim-rust-struct
```

実験directoryから単独実行する場合:

```sh
python3 tests/run_experiment.py
```

scriptは`rustc -vV`のnative hostへNim/Clangのarchitectureを揃える。対応はx86_64またはaarch64のmacOSのみ。ローカルではarm64 machine上でx86_64 Mach-O library/C caller/Rust callerを生成して実行した。CIもrunnerのRust native hostを使用し、保存済みローカル観測とは区別する。

主要build/link commandのローカル条件は次のとおり。`NIM_LIB`は`nim dump --verbosity:0 src/pair_api.nim`のsearch pathから`nimbase.h`があるdirectoryを選ぶ。scriptは自動検出する。

```sh
nim c --forceBuild:on --cc:clang --cpu:amd64 '--passC:-arch x86_64' '--passL:-arch x86_64' --mm:orc --app:lib --header:pair_api.h --nimcache:observed/nimcache --out:observed/bin/libpair_api.dylib --passL:-Wl,-install_name,@rpath/libpair_api.dylib src/pair_api.nim
clang -arch x86_64 -std=c11 -Iobserved/nimcache -I"$NIM_LIB" -Wall -Wextra -Werror src/c_caller.c -Lobserved/bin -lpair_api -Wl,-rpath,@loader_path -o observed/bin/c_caller
rustc --edition=2024 -Dwarnings -Dimproper_ctypes --target x86_64-apple-darwin src/rust_caller.rs -L native=observed/bin -l dylib=pair_api -C link-arg=-Wl,-rpath,@loader_path -o observed/bin/rust_caller
```

生成C・header・objectは`observed/nimcache/`、libraryとcallerは`observed/bin/`へ生成される。この2 directoryはgit対象外。通常の再実行は保存済み観測を上書きしない。`--record`は新しい実測値を保存する明示的な操作であり、使用時は日付付きlog名も今回の実行日に合わせる。

## 実測値（2026-09-03 UTC）

Nim 2.2.10 / ORC / debug、Apple clang 21.0.0、Rust 1.97.1 Homebrew、macOS 26.6.2、x86_64 target。完全な環境と時刻は`observed/environment.txt`に保存した。

両callerの出力は同一で、exit statusは0だった。

```text
size=8 align=4 left=0 right=4
case=0 scalar=42 pair=42
case=1 scalar=-93 pair=-93
case=2 scalar=32768 pair=32768
```

入力は順に`(19, 23)`、`(-100, 7)`、`(32767, 1)`。両callerは数値をassertまたは条件分岐で検証する。CとRustのcompile-time assertionでC int幅、struct size/alignment、field offsetを固定した。検証scriptは生成headerのfield型と順序、値渡しsignature、Rust mirror宣言、3 binaryのarchitecture、公開symbol、実行値を新規buildごとに確認する。

初回PR CI（run `33698430035`）はARM64生成headerと保存済みx86_64 headerの全文一致検査で失敗した。ローカルのARM64追加生成では`#define NIM_EmulateOverflowChecks`の1行だけが差分となった（`observed/arm64-header-diff.txt`）。検証scriptはこのmacroの有無をtarget別に検査し、その1行以外のheader全文一致を確認するよう修正した。この追加調査ではローカルARM64 Rust callerは実行していない。macroのoverflow実装は本実験のABI命題には含めない。

## 公開symbolと初期化

`nm -gU`でlibraryの`_asmati_add`、`_asmati_sum_pair`、`_NimMain`を定義済み公開symbolとして確認した。Rust callerの未定義symbolには前2つがあり、`_NimMain`はない。callerには`@rpath/libpair_api.dylib`の依存が記録され、link commandの`@loader_path`を使って同じdirectoryのlibraryを参照する。

生成Cには`NIM_POSIX_INIT NimMainInit(void)`と、その中の`NimMain()`呼び出しがある。Nim 2.2.10配布`lib/nimbase.h`を今回のClang C11条件でpreprocessすると、`NIM_POSIX_INIT`は`__attribute__((constructor))`、`NIM_EXTERNC`は空、`N_CDECL(rettype,name)`は`rettype name`、`N_LIB_IMPORT`は`extern`となった。結果としてheaderのstruct版は`extern int asmati_sum_pair(AsmatiPair pair_p0);`へ展開された。これらを`observed/c-macro-expansion.txt`へ保存した。

今回はPOSIX constructorによる初期化を利用し、callerで明示的な`NimMain()`呼び出しを行わない。`NimMain`内部が呼ぶ全runtimeのlifecycle、終了・再初期化、thread初期化までは検証していない。

## 主要artifactと読み方

- `observed/pair_api.h`: 未加工の生成header保存コピー。
- `observed/generated-c-excerpt.c`: `@mpair_api.nim.c`からstruct、2つのAPI、NimMain、constructorを抜粋。runtime helper本体を省略し、ローカルsource pathをplaceholderへ正規化した。
- `observed/c-macro-expansion.txt`: 配布headerの今回の有効macroと展開済みAPI宣言。別platformの条件分岐全体ではない。
- `observed/symbols-linkage.txt`: libraryの公開symbolとRustの対象import、runtime dependency。
- `observed/commands-2026-09-03.txt`: 実行したargv、compile/link出力、exit status。ローカル絶対pathのみplaceholder化。
- `observed/run-2026-09-03.txt`: binary architectureとC/Rustの実測値。

## 定義追跡と未確認範囲

記事で区別する判断は「layout一致」と「実呼び出し成立」、「Rust mirror宣言」と「生成header」、「machine architecture」と「生成target」。追跡した識別子は`AsmatiPair`、`cint`→`int`、`c_int`、`bycopy`、`exportc`、`dynlib`、`cdecl`、`repr(C)`、`extern "C"`、`NIM_EXTERNC`、`N_CDECL`、`N_LIB_IMPORT`、`N_LIB_EXPORT`、`NIM_POSIX_INIT`、`NimMainInit`、`NimMain`。

公式の定義参照（閲覧2026-09-03。実測versionは上記へ固定）:

- [Nim manual: bycopy](https://nim-lang.org/docs/manual.html#foreign-function-interface-bycopy-pragma)
- [Rust Reference: C representation](https://doc.rust-lang.org/reference/type-layout.html#the-c-representation)
- [Rust Reference: external blocks](https://doc.rust-lang.org/reference/items/external-blocks.html)
- [Rust std::ffi::c_int](https://doc.rust-lang.org/std/ffi/type.c_int.html)

未確認はstruct戻り値、pointer/ownership/cleanup変換、複雑なobject、overflowや例外が境界を越える場合、別target・OS・compiler・Rust/Nim version、release/static library、register/stackのassembly上の受け渡しである。生成関数にはoverflow helperが残るが、その失敗時のFFI契約は今回扱わない。Rust宣言の誤りを`unsafe extern`やlink成功だけで自動検出できる、とは結論しない。
