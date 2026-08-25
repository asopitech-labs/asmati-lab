# Observation Table

| Case | Nim declaration | Generated C signature | Notes |
| --- | --- | --- | --- |
| no-arg int return | `proc noArgs(): int` | `NI noArgs__scalar95proc_u1(void)` | 引数なしは`void`、戻り値は`NI` |
| int by value | `proc addOne(x: int): int` | `NI addOne__scalar95proc_u3(NI x_p0)` | `x`は値渡しで`NI` 1引数 |
| float arg/return | `proc half(x: float): float` | `NF half__scalar95proc_u6(NF x_p0)` | 引数と戻り値の両方が`NF` |

補足:

- `NIM_INTBITS 64`のため、この環境では`NI = NI64`。
- `NF = double`。
- 非Windows分岐の`N_NIMCALL`なので、呼び出し規約の追加修飾子は付かない。
