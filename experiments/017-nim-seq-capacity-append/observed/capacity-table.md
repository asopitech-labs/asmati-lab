# seq capacity表

| step | append後のlen | capacity | capacity変化 | total |
| ---: | ---: | ---: | --- | ---: |
| 0 | 0 | 0 | 初期状態 | 0 |
| 1 | 1 | 1 | 初回payload確保 | 1 |
| 2 | 2 | 2 | 拡張 | 3 |
| 3 | 3 | 4 | 拡張 | 6 |
| 4 | 4 | 4 | なし | 10 |
| 5 | 5 | 8 | 拡張 | 15 |
| 6 | 6 | 8 | なし | 21 |
| 7 | 7 | 8 | なし | 28 |
| 8 | 8 | 8 | なし | 36 |
| 9 | 9 | 16 | 拡張 | 45 |
| 10 | 10 | 16 | なし | 55 |

生成された`add`はpayloadがnil、または`capacity < oldLen + 1`のときだけ`prepareSeqAddUninit`を呼ぶ。したがってstep 1はnil用の初回確保、step 2、3、5、9は既存payloadの拡張条件に対応する。allocatorが同じaddressを返す可能性があるため、capacity拡張と物理address移動は同じ意味として扱わない。
