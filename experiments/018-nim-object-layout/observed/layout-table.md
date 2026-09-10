# object layout表

| 要素 | C型（生成C） | size | offset | 次のoffsetまでのpadding |
| --- | --- | ---: | ---: | ---: |
| `count` | `NI`（今回の`NIM_INTBITS 64`では`NI64`） | 8 | 0 | 0 |
| `enabled` | `NIM_BOOL`（今回のC99以降では`_Bool`） | 1 | 8 | 7 |
| `ratio` | `NF`（`double`） | 8 | 16 | 0 |

object全体はsize 24、alignment 8だった。生成Cのstructには明示的なpadding fieldはなく、`enabled`の終端offset 9と`ratio`のoffset 16の差から7 byteの内部paddingを確認した。末尾fieldはoffset 16から8 byteなのでobject終端の24と一致し、今回の配置に末尾paddingはない。

この表はNim 2.2.10、macOS、64-bit target、Apple Clangの保存観測であり、公開C ABIの保証ではない。
