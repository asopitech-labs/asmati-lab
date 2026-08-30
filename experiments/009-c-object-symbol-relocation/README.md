# Issue #65: object fileのsymbolとrelocationを最小関数で読む

## 問い

同じC sourceに、同じobject内の`static`関数を呼ぶ関数と、object外で定義される関数を呼ぶ関数を置いたとき、Mach-O objectのsymbol tableとrelocation tableには何が残るか。

## 最小source

`src/symbol_relocation.c`は次の2経路だけを持つ。

- `call_internal`は、同じsource内の`static`関数`internal_double`を呼ぶ。
- `call_external`は、標準C libraryで実装される`puts`を呼ぶ。

`-O0 -fno-inline -fno-builtin-puts`を指定し、比較対象のcall instructionがobjectに残る条件でARM64 Mach-O objectを作った。

## 再現command

macOS上で、このdirectoryをcurrent directoryとして実行する。

```console
$ python3 tests/prepare_outputs.py
object output directory prepared
$ clang -arch arm64 -std=c11 -Wall -Wextra -Werror -O0 -fno-inline -fno-builtin-puts -c src/symbol_relocation.c -o observed/obj/symbol_relocation.o
$ python3 tests/verify_object.py
Mach-O symbols and ARM64 branch relocations verified
```

手動観察に用いたcommandは次のとおり。

```console
$ file observed/obj/symbol_relocation.o
$ nm -m observed/obj/symbol_relocation.o
$ nm -u observed/obj/symbol_relocation.o
$ otool -hv observed/obj/symbol_relocation.o
$ size observed/obj/symbol_relocation.o
$ otool -rv observed/obj/symbol_relocation.o
$ otool -tvV observed/obj/symbol_relocation.o
```

object fileは再生成物なのでcommitしない。CIも同じcommandで生成してから検証する。

## 観察結果

- `call_internal`と`call_external`は、いずれもdefined external symbolだった。
- `internal_double`は同じobject内のdefined non-external symbolだった。
- `puts`だけがundefined external symbolであり、`nm -u`の出力も`_puts`だけだった。
- `__TEXT,__text`には2件のARM64 `BR26` relocationがあり、対象は`_internal_double`と`_puts`だった。
- disassemblyでは`call_internal`と`call_external`の双方に`bl` instructionが残った。

このobjectでは、内部callにも外部callにもbranch relocationがある。したがって、relocationの存在だけではobject外の依存を判定できない。relocationの対象symbolが、同じobject内のdefined non-externalなのか、undefined externalなのかをsymbol tableと組み合わせて読む必要がある。

`__LD,__compact_unwind`には別途3件のlocal section relocationがあった。これは関数callの2経路を比較する今回の主対象ではないため、存在だけを記録し、個別の意味までは追跡していない。

## 成果物

- `observed/symbols-2026-08-30.txt`: symbol tableとundefined symbol
- `observed/relocations-2026-08-30.txt`: relocation table
- `observed/disassembly-excerpt.txt`: 3関数のdisassembly
- `observed/observation-table.md`: source上の識別子とobject上の観察の対応
- `tests/verify_object.py`: object形式、symbol状態、text relocation、call instructionの検査

## 未確認範囲

- x86_64、ELF、COFFなど、ARM64 Mach-O以外のobject形式
- optimization levelを変えた場合のinlining、call消去、relocation変化
- `__compact_unwind` relocationの詳細な意味
- debug information、assembly性能、link後の実行file
