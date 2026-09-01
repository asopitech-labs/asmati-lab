# Link記録とruntime解決の対応

| 観察対象 | 保存された値 | 成功配置 | library欠落配置 | 判断できること |
| --- | --- | --- | --- | --- |
| library install name | `@rpath/libanswer.dylib` | callerのdependency名と一致 | 同じ名前を解決できない | libraryがlink先へ渡す識別名 |
| caller dependency | `@rpath/libanswer.dylib` | dyld traceに実体pathあり | `Library not loaded`に同名あり | binaryへ名前が記録されても実体の発見はruntimeに残る |
| caller `LC_RPATH` | `@loader_path/lib` | `observed/bin/lib/libanswer.dylib`がloadされた | `observed/bin/missing/lib/libanswer.dylib`を試した | callerの位置変更に伴って試行pathも変化した |
| `_shared_answer` | libraryでdefined external、callerでundefined external | `answer=42` | main開始前にloader failure | symbol呼び出しより前にdependencyのload成立が必要 |

`otool`による静的なload command観察、`DYLD_PRINT_LIBRARIES`による成功時の実体path、library欠落時のdyld errorを分けて保存した。
