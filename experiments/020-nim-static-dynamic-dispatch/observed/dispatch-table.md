# 呼び出し先選択表

| Nim呼び出し | 生成Cの入口 | 選択条件 | 呼び出し先 | 実行値 |
| --- | --- | --- | --- | ---: |
| `callStatic(Animal)` | `staticScore__static95dynamic95dispatch_u7` | 静的に確定 | 基底型用proc | 105 |
| `callDynamic(Animal)` | `dynamicScore__static95dynamic95dispatch_u13` | depth 2 / token `1574871296` | Dog用method | 12 |
| dispatcher fallback | `dynamicScore__static95dynamic95dispatch_u13` | depth 1 / token `1148574976` | Animal用base method | 今回は未実行 |

今回の生成単位では`TNimTypeV2`に`vTable`欄があるが、Dog descriptorはその欄を明示初期化せず、生成単位内にslotの設定・参照もない。呼び出し先選択は`isObjDisplayCheck`を並べたdispatcherで行われた。
