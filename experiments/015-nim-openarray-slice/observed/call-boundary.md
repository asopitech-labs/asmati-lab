# openArray call boundary

Nim 2.2.10 / ORC / debug / C backendで観察した。`openArray[int]`を受ける`summary`と`sameAddress`はprivateな生成C関数であり、C ABIとして公開していない。

| Nim caller | 生成Cで渡したpointer | 生成Cで渡したlength | 実行結果 | 境界の観察 |
| --- | --- | ---: | --- | --- |
| `[10, 20, 30, 40]`のarray | 固定arrayの先頭 | literal `4` | `len=4 first=10 last=40 total=100 aliases=true` | array storageの先頭addressとcallee先頭要素が一致 |
| `@[10, 20, 30, 40]`のseq | seq payloadの`data`。payloadがなければ`NIM_NIL` | seqの`len` | `len=4 first=10 last=40 total=100 aliases=true` | seq payload先頭とcallee先頭要素が一致 |
| seqの`toOpenArray(1, 2)` | seq payloadの`data + 1` | `2 - 1 + 1`、実値2 | `len=2 first=20 last=30 total=50 aliases=true` | 元seqのindex 1とcallee先頭要素が一致 |

calleeの生成C signatureは`NI* values_p0, NI values_p0Len_0`である。要素参照とloop上限は同じlength引数を使った。Nim配布sourceは`toOpenArray(seq, first, last)`を`magic: "Slice"`とし、copyしないnon-owning viewと説明する。生成Cでも、正常sliceは元seq payloadへのoffset pointerとlengthだけを`show`へ渡し、slice構築用の要素copyやallocationは現れなかった。元seq自体の初期化には`newSeqPayload`があるため、seqの割り当てとslice viewの構築は別に扱う。

`toOpenArray(1, 4)`では、元seqの長さ4に対する範囲検査が`show`呼び出しより前に生成された。実行時は`raiseIndexError4(1, 4, 4)`へ進み、`IndexDefect`でexit 1となった。`oob len=`は出力されず、calleeは実行されなかった。

この結果は、今回の有効なarray・seq・sliceと範囲外sliceに限定する。viewを元データの再割り当て・破棄後まで保持する条件や、bounds checkを無効にしたbuildは確認していない。
