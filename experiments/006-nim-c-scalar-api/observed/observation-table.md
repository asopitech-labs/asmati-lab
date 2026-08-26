# 観察表

| Nim source / build | 生成header・library・caller | この実験で確認したこと |
| --- | --- | --- |
| `cint`引数・戻り値と`cdecl` | `int asmati_add_ints(int, int)` | Cの`int`を使う公開宣言になった |
| `cdouble`引数・戻り値と`cdecl` | `double asmati_half(double)` | Cの`double`を使う公開宣言になった |
| `exportc, dynlib` | `N_LIB_EXPORT`定義と`_asmati_add_ints` / `_asmati_half` | 生成C内だけのprivate関数ではなく、dynamic libraryの公開symbolになった |
| `--header:scalar_api.h` | `scalar_api.h`が`nimbase.h`をinclude | 生成headerの利用にはNim macro定義のinclude pathが必要だった |
| `--app:lib` on macOS/POSIX | `NIM_POSIX_INIT NimMainInit`が`NimMain()`を呼ぶ | C callerの`main`から明示的に`NimMain`を呼ばず、library constructorで初期化された |
| `caller.c` | libraryへの未定義symbolはscalar 2関数、`NimMain`参照なし | C callerは生成headerと公開symbolだけを直接利用した |
| `asmati_add_ints(19, 23)` | `add(19,23)=42` | integer APIをC callerから実行できた |
| `asmati_half(3.5)` | `half(3.5)=1.75` | floating-point APIをC callerから実行できた |

この表はmacOS arm64、Nim 2.2.10、Clang 21.0.0、ORC、debug dynamic libraryの1条件だけを記録する。string、ownership、error handlingは扱っていない。
