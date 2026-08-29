# 観察表

| 観測点 | debug | `-d:release` | 判断 |
| --- | --- | --- | --- |
| Nim source | `addOne(value) = value + 1` | 同一source | 入力差ではなくbuild profile差を比較した |
| Nim compile mode | `opt: none` | `opt: speed; -d:release` | releaseは最適化profileを変えた |
| C compiler option | optimization flagなし | `-O3` | generated Cのcompile条件は異なる |
| generated Cの加算 | `nimAddInt` | `nimAddInt` | releaseでもhelperは残った |
| overflow分岐 | `raiseOverflow` | `raiseOverflow` | releaseでもcheckは残った |
| source frame処理 | `nimfr_`、`nimlf_`、`popFrame`あり | なし | releaseでdebug bookkeepingが削除された |
| 通常値`41` | exit 0、stdout `42` | exit 0、stdout `42` | 両buildで同じ結果 |
| `high(int)` | exit 1、`OverflowDefect` | exit 1、`OverflowDefect` | 両buildでoverflowを拒否した |
| 境界値stderr | `addOne` frameあり | `addOne` frameなし | stack/line trace設定差が見えた |

Nim 2.2.10の`nim.cfg`では、release blockに`overflow_checks:off`はない。個別checkを無効にする設定はbuild profileと別に確認する必要がある。
