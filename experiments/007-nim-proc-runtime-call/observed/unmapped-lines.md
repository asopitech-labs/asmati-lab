# 今回対応づけない生成行

| 生成行・識別子 | 扱い | 理由 |
| --- | --- | --- |
| `nimfr_`、`nimlf_`、`popFrame` | 範囲外 | debug stack frameとsource位置のbookkeepingであり、1 proc・1文字列操作のruntime対応ではない |
| `nimErrorFlag`、`nimTestErrorFlag` | 範囲外 | program全体のerror propagationであり、今回の文字列連結の定義追跡には含めない |
| `deallocShared` | 範囲外 | `NimMainModule`終了時のlifetime cleanupであり、`addSuffix`の生成関数本体外にある |
| `echoBinSafe` | 範囲外 | 観測値を出力するための経路であり、source procから文字列runtimeへの対応ではない |
| `allocSharedImpl`以下 | 未確認 | `rawNewString`がallocatorへ到達することだけを確認し、allocator内部は追跡していない |
| `addSuffix__proc95runtime_u1`のsuffix | 未確認 | このbuildでのsymbolを記録したが、命名規則は調査していない |

「未確認」は結果を推測で埋めず、今回の最小実験で検証していない境界として残した。
