# Issue #67: shared libraryの依存とruntime loaderを確認する

## 問い

1つのshared libraryへ依存するcallerに、libraryのinstall nameとloader-relative search pathを記録したとき、runtime loaderはどのpathを解決し、libraryがそのpathにない場合はどう失敗するか。

## 最小source

- `src/answer.c`は`shared_answer`を公開し、42を返す。
- `src/caller.c`は`shared_answer`を呼び、`answer=42`を表示する。

libraryはinstall nameを`@rpath/libanswer.dylib`としてbuildした。callerにはdependencyとして同じ名前を記録し、`LC_RPATH`へ`@loader_path/lib`を設定した。生成配置は`observed/bin/caller`と`observed/bin/lib/libanswer.dylib`である。

## 再現command

macOS上で、このdirectoryをcurrent directoryとして実行する。

```console
$ python3 tests/prepare_outputs.py
shared library output directories prepared
$ clang -arch arm64 -std=c11 -Wall -Wextra -Werror -fPIC -dynamiclib src/answer.c -Wl,-install_name,@rpath/libanswer.dylib -o observed/bin/lib/libanswer.dylib
$ clang -arch arm64 -std=c11 -Wall -Wextra -Werror src/caller.c -Lobserved/bin/lib -lanswer -Wl,-rpath,@loader_path/lib -o observed/bin/caller
$ python3 tests/verify_loader.py
shared library dependency and loader path verified
$ python3 tests/run_cases.py
success: exit=0 stdout=answer=42
trace: loaded=<EXPERIMENT>/observed/bin/lib/libanswer.dylib
missing: exit_nonzero=true
missing: library_not_loaded=@rpath/libanswer.dylib
missing: tried=<EXPERIMENT>/observed/bin/missing/lib/libanswer.dylib
shared library loader success and failure verified
```

libraryとcallerは再生成物なのでcommitしない。CIは同じcommandで生成してから検証する。

## 観察結果

- libraryのinstall nameは`@rpath/libanswer.dylib`だった。
- callerのdependency一覧には`@rpath/libanswer.dylib`と`libSystem.B.dylib`があった。
- callerの`LC_RPATH`は`@loader_path/lib`だった。
- libraryは`_shared_answer`をdefined externalとして持ち、callerでは同symbolがundefined externalだった。
- 元の配置でcallerを実行するとexit 0で`answer=42`を出力した。
- `DYLD_PRINT_LIBRARIES=1`では、実体の`observed/bin/lib/libanswer.dylib`がloadされた行を確認した。
- callerだけを`observed/bin/missing/caller`へcopyすると、loaderは`observed/bin/missing/lib/libanswer.dylib`を試し、`Library not loaded: @rpath/libanswer.dylib`で非zero終了した。

この条件では、link時にcallerへ記録されたdependency名だけでは実行成功は決まらない。runtimeではcallerの`LC_RPATH`にある`@loader_path/lib`とlibrary名が組み合わされ、その位置に実体がある元配置は成功し、callerだけを移した配置は失敗した。

前回のstatic archiveではarchive名がruntime dependencyへ残らなかったが、今回はshared libraryの`@rpath`名がcallerに残り、runtime loaderが実体のpathを解決した。link時の入力とruntime dependencyを区別できる。

## 成果物

- `observed/dependencies-2026-09-01.txt`: library ID、caller dependency、symbol状態
- `observed/load-commands-2026-09-01.txt`: callerの`LC_RPATH`
- `observed/loader-cases-2026-09-01.txt`: 成功、load trace、欠落失敗の正規化ログ
- `tests/verify_loader.py`: Mach-O形式、install name、dependency、RPATH、export symbolの検査
- `tests/run_cases.py`: 成功配置、dyld trace、library欠落配置の実行検査

## 未確認範囲

- `DYLD_LIBRARY_PATH`など環境変数による検索path上書き
- codesign、hardened runtime、SIP、notarization
- `dlopen`を使うplugin形式、weak dependency、optional loading
- 依存が2段以上ある場合のtransitive lookup
- absolute install name、`@executable_path`、複数`LC_RPATH`
- Linux ELF、Windows PE/COFF、x86_64など別形式・別architecture
