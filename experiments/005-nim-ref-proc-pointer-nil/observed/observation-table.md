# 観察表

| Nim source | Nim 2.2.10生成C | この実験で確認したこと |
| --- | --- | --- |
| `Reading = ref object` | `struct ... { NI value; };`と、そのstructへのpointer | ref objectのfield本体とrefのpointerが分離された |
| `readValue(reading: Reading): int` | `NI readValue(...Reading* reading_p0)` | ref object引数は生成Cでpointer引数になった |
| `reading.isNil` | `reading_p0 == 0` | nil分岐はfieldアクセス前のnull比較になった |
| `reading.value` | `(*reading_p0).value` | 非nil側だけでpointerをdereferenceしてfieldを読んだ |
| `keepReading(reading: Reading): Reading` | `Reading* keepReading(Reading* reading_p0)` | ref objectの戻り値も同じobject型へのpointerになった |
| `reading`を返す | `result = NIM_NIL; eqcopy(..., reading_p0)` | ORC debug buildでは戻り値へ単純代入せずref copy補助を呼んだ |

この表はmacOS arm64、Nim 2.2.10、ORC、debug buildの1条件だけを記録する。C ABIとしての公開契約やmemory manager間の差は確認していない。
