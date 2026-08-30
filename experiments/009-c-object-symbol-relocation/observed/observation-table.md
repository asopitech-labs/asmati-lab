# Sourceとobject観察の対応

| source上の識別子 | sourceでの条件 | symbol table | `__TEXT,__text` relocation | 観察から言えること |
| --- | --- | --- | --- | --- |
| `call_internal` | 非`static`関数 | defined external `_call_internal` | call site `0x14`から`_internal_double`への`BR26` | objectから参照可能な定義であり、内部関数へのcallを持つ |
| `internal_double` | 同じtranslation unitの`static`関数 | defined non-external `_internal_double` | relocationのtarget | targetは同じobject内で定義済みで、外部link先ではない |
| `call_external` | 非`static`関数 | defined external `_call_external` | call site `0x50`から`_puts`への`BR26` | objectから参照可能な定義であり、外部関数へのcallを持つ |
| `puts` | headerで宣言され、source内に定義なし | undefined external `_puts` | relocationのtarget | このobjectだけではaddressが確定せず、link時に外部定義が必要 |

`_internal_double`と`_puts`には、どちらにも`BR26` relocationがある。外部依存かどうかはrelocationの存在ではなく、symbolがdefined non-externalかundefined externalかを併読して区別する。
