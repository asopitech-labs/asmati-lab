# Archive inputとlink結果の対応

| 対象 | link前の状態 | link map | 実行binary | 観察から言えること |
| --- | --- | --- | --- | --- |
| `caller.o` | `_main`を定義し、`_used_value`と`_printf`がundefined external | object `[1]`として記録 | `_main`あり | linkの起点で、`_used_value`の定義を要求した |
| `libvalues.a(used.o)` | `_used_value`をdefined externalとして持つarchive member | object `[2]`として記録 | `_used_value`あり | callerの未解決symbolを満たすmemberが取り込まれた |
| `libvalues.a(unused.o)` | `_unused_value`をdefined externalとして持つarchive member | 記録なし | `_unused_value`なし | archive内には存在するが、callerから要求されないmemberは取り込まれなかった |
| `libSystem.B.dylib` | archive外のsystem library | system objectとしてlinkへ参加 | `otool -L`のruntime dependency | static archiveのmember抽出と、実行時shared library依存は別の段階である |

今回の条件では、archive memberの存在、link時に抽出されたobject、実行binaryに残るsymbol、runtime loaderが見るshared libraryを別々に観察できた。
