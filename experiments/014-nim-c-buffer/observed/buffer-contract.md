# 観測したbuffer contract

| API | callerの入力 | libraryの動作 | 戻り値 |
| --- | --- | --- | --- |
| `asmati_trimmed_length` | `input`とbyte単位の`length` | 末尾の0 byteだけを読み飛ばす。書き込まず保持しない | 末尾0を除いた長さ |
| `asmati_write_label` | `output`と書き込み可能な`capacity` | `min(capacity, 6)` byteだけ`ASMATI`を書く。NUL終端しない。保持しない | 常に必要長6 |

## 有効な呼び出し

- `length == 0`の入力照会は`input == NULL`を許す。生成Cはlengthを先に判定し、0ならpointerをdereferenceしない。
- `length > 0`では、callerが少なくとも`length` byte読めるpointerを渡す。
- `capacity == 0`の出力照会は`output == NULL`を許す。生成Cの書き込み回数は0になる。
- `capacity > 0`では、callerが少なくとも`capacity` byte書けるpointerを渡す。
- callerは入力・出力bufferの所有権と寿命を保持する。今回の生成された2関数にはallocation helperやpointerの保存処理がない。

## 観測した境界条件

- 入力`AB\0\0`、length 4は2を返した。`ASMATI`、length 6は6を返した。
- 出力capacity 8は6 byteを書き、後続2 byteのcanaryを保持した。
- 出力capacity 3は`ASM`だけを書き、後続canaryを保持しながら必要長6を返した。
- `NULL, 0`の入力は0、`NULL, 0`の出力照会は6を返した。

このAPIは不正pointerや、実領域を超えるlength/capacityを検出しない。生成headerの入力型も`NU8*`であり、read-only制約をC型へ表していない。今回の実装が入力へ書かなかったという観察を、外部が依存できる型保証に広げない。
