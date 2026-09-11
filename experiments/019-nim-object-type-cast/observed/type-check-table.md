# type identification・cast条件表

| 入力の実型 | 判定・操作 | 結果 | 生成Cの条件 |
| --- | --- | --- | --- |
| `Dog` | `dog of Dog` | `true` | 実体の`m_type`にあるdepth 2のdisplay tokenがDog tokenと一致 |
| `Cat` | `cat of Dog` | `false` | 実体の`m_type`にあるdepth 2のdisplay tokenがDog tokenと不一致 |
| `Dog` | `Dog(animal).barkVolume` | `7` | 同じDog token検査後にDog pointerへcastしてfield参照 |
| `Cat` | `Cat(animal).lives` | `9`（実験出力は符号を反転して`-9`） | 同じCat token検査後にCat pointerへcastしてfield参照 |
| `Cat` | 未判定の`Dog(animal)` | 非zero終了、`ObjectConversionDefect` | Dog token検査不一致から`raiseObjectConversionError`へ分岐 |

DogとCatの型descriptorはいずれもdepth 2で、display配列の0・1番要素は共通、2番要素は異なった。`isObjDisplayCheck`は`targetDepth <= source.depth`と`source.display[targetDepth] == token`を同時に検査する。

今回、`of`とobject conversionは同じmetadataと`isObjDisplayCheck`を使った。ただし、`of`の不一致は`false`となり、object conversionの不一致は`raiseObjectConversionError`へ進む。判定の結果とcast失敗時の制御フローを区別する。
