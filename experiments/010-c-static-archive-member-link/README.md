# Issue #66: static archiveのmemberとlink結果を比較する

## 問い

2つのobjectを含むstatic archiveから、callerが片方のsymbolだけを参照したとき、archiveのmemberと実行binaryへ取り込まれるsymbolはどう対応するか。

## 最小source

- `src/used.c`は`used_value`を定義し、42を返す。
- `src/unused.c`は`unused_value`を定義し、99を返す。
- `src/caller.c`は`used_value`だけを宣言・呼び出し、結果を表示する。

3つのsourceを別々のARM64 Mach-O objectへcompileし、`used.o`と`unused.o`だけを`libvalues.a`へ入れた。caller objectをこのarchiveとlinkし、link map、binary symbol、実行結果を観察した。

## 再現command

macOS上で、このdirectoryをcurrent directoryとして実行する。

```console
$ python3 tests/prepare_outputs.py
archive output directories prepared
$ clang -arch arm64 -std=c11 -Wall -Wextra -Werror -O0 -c src/used.c -o observed/obj/used.o
$ clang -arch arm64 -std=c11 -Wall -Wextra -Werror -O0 -c src/unused.c -o observed/obj/unused.o
$ clang -arch arm64 -std=c11 -Wall -Wextra -Werror -O0 -c src/caller.c -o observed/obj/caller.o
$ ar rcs observed/lib/libvalues.a observed/obj/used.o observed/obj/unused.o
$ clang -arch arm64 observed/obj/caller.o observed/lib/libvalues.a -Wl,-map,observed/bin/link-map.txt -o observed/bin/caller
$ python3 tests/verify_archive.py
static archive member extraction and linked symbols verified
```

object、archive、binary、full link mapは再生成物なのでcommitしない。CIは同じcommandで生成してから検証する。

## 観察結果

- `ar -t`ではsymbol index `__.SYMDEF SORTED`に続き、`used.o`と`unused.o`の2 object memberがarchive内にあった。
- archiveのsymbol tableでは、`used.o`が`_used_value`、`unused.o`が`_unused_value`をそれぞれdefined externalとして持った。
- link前の`caller.o`では、`_used_value`と`_printf`がundefined externalだった。`_unused_value`への参照はなかった。
- link mapのObject filesには`caller.o`と`libvalues.a(used.o)`があり、`libvalues.a(unused.o)`はなかった。
- 実行binaryには`_used_value`があり、`_unused_value`はなかった。
- callerの実行結果は`used=42`だった。

この条件では、static archive全体が実行binaryへそのまま入るのではなく、callerの未解決symbol`_used_value`を定義する`used.o`がmember単位で取り込まれた。archiveが2つのobjectを含むことと、link結果が両objectのsymbolを含むことは同じではない。

`otool -L`で実行binaryの実行時依存を確認すると`libSystem.B.dylib`だけが表示され、`libvalues.a`は表示されなかった。static archiveはlink時の入力であり、この実験ではruntime loaderが解決するlibrary名として残っていない。

## 成果物

- `observed/archive-members-2026-08-31.txt`: archiveのindexと2 object member
- `observed/archive-symbols-2026-08-31.txt`: memberごとのdefined symbol
- `observed/caller-object-symbols-2026-08-31.txt`: link前callerのdefined/undefined symbol
- `observed/link-map-excerpt.txt`: linkへ入ったobject memberとsymbolの対応
- `observed/linked-symbols-2026-08-31.txt`: 実行binaryのsymbolとruntime dependency
- `tests/verify_archive.py`: member、symbol、link map、実行結果の自動検証

## 未確認範囲

- `-all_load`、`-force_load`など、archive抽出を変更するlink option
- object内に複数symbolがある場合のdead stripping
- LTO、linker性能、symbol visibility変更
- ELF、COFF、x86_64などARM64 Mach-O以外の形式
- static archiveの入れ子、member間の循環依存、member順序の影響
