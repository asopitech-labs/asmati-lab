# Issue #55: Nim libraryのbufferとlengthをCから扱う

## 問い

caller所有の固定pointerとlength/capacityをNimの公開C ABIへ渡したとき、入力の読み取り、出力の書き込み、必要長の返却、cleanup責任をどこまで明示できるか。

Nim `string`や`seq`は公開しない。`ptr UncheckedArray[uint8]`と`csize_t`だけを使い、入力用と出力用のAPIを分けた。

## 入力sourceと公開API

`src/buffer_api.nim`は次の2関数を定義する。

- `asmati_trimmed_length(input, length)`: 入力bufferの末尾0 byteを除いた長さを返す。length 0ではpointerを読まない。
- `asmati_write_label(output, capacity)`: callerのbufferへ`ASMATI`をcapacityまで書き、書けた長さではなく必要長6を返す。capacity 0ではpointerへ書かない。

生成header `observed/buffer_api.h`では、どちらも`NU8*`と`size_t`を受け、`size_t`を返した。Nim 2.2.10配布`nimbase.h`を今回のC11条件でpreprocessすると`NU8`は`unsigned char`である。入力pointerも`const`ではない。実装が読み取りだけを行ったという観察と、headerがread-onlyを型で保証することは同じではない。

完全なprecondition、write範囲、戻り値、ownershipは`observed/buffer-contract.md`に固定した。

## 再現

macOS、Nim 2.2.10、Apple Clang、Python 3が必要。リポジトリrootから実行する。

```sh
python3 tools/experiment_ci.py validate
python3 -m unittest discover -s tools/tests -p 'test_*.py'
python3 tools/experiment_ci.py run 014-nim-c-buffer
```

実験directoryからは次で再実行できる。

```sh
python3 tests/run_experiment.py
```

scriptは`nim --version`のmacOS CPUへNim/Clangのarchitectureを揃える。ローカルではNim compilerのx86_64 targetを使用し、arm64 machine上でx86_64 Mach-Oを実行した。CIではrunnerのNim targetを別に検証する。binaryとnimcacheは`observed/bin/`と`observed/nimcache/`へ生成し、gitへ保存しない。通常実行は保存観測を上書きせず、`--record`だけが明示的に保存する。

主要commandのローカル条件は次のとおり。`NIM_LIB`は`nim dump`のsearch pathからscriptが検出する。

```sh
nim c --forceBuild:on --cc:clang --cpu:amd64 '--passC:-arch x86_64' '--passL:-arch x86_64' --mm:orc --app:lib --header:buffer_api.h --nimcache:observed/nimcache --out:observed/bin/libbuffer_api.dylib --passL:-Wl,-install_name,@rpath/libbuffer_api.dylib src/buffer_api.nim
clang -arch x86_64 -std=c11 -Iobserved/nimcache -I"$NIM_LIB" -Wall -Wextra -Werror src/caller.c -Lobserved/bin -lbuffer_api -Wl,-rpath,@loader_path -o observed/bin/caller
observed/bin/caller
```

## 実測結果（2026-09-04 UTC）

Nim 2.2.10 / ORC / debug、Apple clang 21.0.0、macOS 26.6.2、x86_64 target。詳細は`observed/environment.txt`へ保存した。

```text
input empty=0 padded=2 full=6
output query=6 full_required=6 short_required=6
output full=ASMATI short=ASM tails=CC,CC
```

C callerは次を実行してexit 0となった。

1. `NULL, 0`の入力、末尾0を持つ4 byte入力、6 byte入力を比較した。
2. `NULL, 0`で必要長だけを照会した。
3. capacity 8とcapacity 3の出力bufferを0xCCで初期化し、write範囲外のcanaryが変化しないことを確認した。

このcanary結果は今回の3呼び出しで境界外書き込みを観測しなかった証拠であり、任意pointer/lengthに対するmemory safetyの証明ではない。

## 生成物、symbol、初期化

- `observed/buffer_api.h`: Nim compilerが生成したheaderの未加工保存コピー。
- `observed/generated-c-excerpt.c`: 2つの公開関数、capacityを制限する`min` helper、POSIX constructorの抜粋。runtime helper本体は省略し、ローカルpathだけを正規化した。
- `observed/c-macro-expansion.txt`: `NU8`定義、今回有効なmacro、展開済みAPI宣言。
- `observed/symbols-linkage.txt`: `_asmati_trimmed_length`、`_asmati_write_label`、`_NimMain`とcallerのdependency/import。
- `observed/commands-2026-09-04.txt`: 実際のcompile/link/inspection command、出力、exit status。
- `observed/run-2026-09-04.txt`: library/caller形式と実行結果。
- `tests/run_experiment.py`: fresh build、header、generated C、macro、symbol、target、実行値、canaryを検証する。

libraryは3つのsymbolを公開した。C callerは2つのAPIを未定義symbolとして参照するが、`NimMain`を直接参照しない。生成Cの`NIM_POSIX_INIT NimMainInit`が`NimMain()`を呼ぶ。今回の2つの公開関数には、検査対象のallocation helperは現れなかった。

## 技術判断と未確認範囲

読者が区別する判断は、pointerと領域長、capacityと必要長、実装上のread-onlyと型の`const`保証、今回allocationを観測しないことと一般的なlifetime保証である。追跡した識別子は`ptr UncheckedArray[uint8]`、`csize_t`、`NU8`、`size_t`、`asmati_trimmed_length`、`asmati_write_label`、`min` helper、`NIM_EXTERNC`、`N_CDECL`、`N_LIB_IMPORT`、`N_LIB_EXPORT`、`NIM_POSIX_INIT`、`NimMainInit`、`NimMain`。

公式参照（Nim manual 2.2.10、閲覧2026-09-04）:

- [Unchecked arrays](https://nim-lang.org/docs/manual.html#types-unchecked-arrays)
- [Pointer types](https://nim-lang.org/docs/manual.html#types-reference-and-pointer-types)
- [exportc pragma](https://nim-lang.org/docs/manual.html#foreign-function-interface-exportc-pragma)
- [cdecl pragma](https://nim-lang.org/docs/manual.html#foreign-function-interface-cdecl-pragma)

未確認は、不正pointer、実領域を超えるlength/capacity、overlap、concurrent call、NUL終端文字列としての利用、Nim string/seq、library側allocation、callerへ返すowned pointer、error code/exception、別OS/target/version、release/static libraryである。
