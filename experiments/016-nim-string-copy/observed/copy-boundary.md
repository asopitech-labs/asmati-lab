# string copy境界

| 操作 | source | 観測したaddress | 生成C/runtime | 結果 |
| --- | --- | --- | --- | --- |
| 値引数 | `passAliases(original, originalAddress)` | callee内のpayload先頭 | `NimStringV2 value_p0`、callee内に`eqcopy`なし | 元と同じ |
| 戻り値 | `returned = identity(original)` | 戻り値のpayload先頭 | `identity`が`eqcopy(&result, value_p0)`、その先で`nimAsgnStrV2` | 元と異なる |
| 通常代入 | `assigned = original` | 代入先のpayload先頭 | callerが`eqcopy(&assigned, original)`、その先で`nimAsgnStrV2` | 元と異なる |
| 書き換え | `assigned[0] = 'Z'` | 書き換え前後の代入先 | `nimPrepareStrMutationV2`の後にpayloadへ書く | addressは元と異なるまま、元の値は不変 |
| 終了時 | `original`、`returned`、`assigned` | 各payload | non-nilかつnon-literalなら`deallocShared` | 3変数それぞれにcleanup生成 |

今回のsourceは`newString(4)`で作ったnon-literal stringである。`nimAsgnStrV2`のliteral shallow-copy分岐は保存したが、実行対象にはしていない。
