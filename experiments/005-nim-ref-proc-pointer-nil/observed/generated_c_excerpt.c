/* Extracted from Nim 2.2.10 generated C for src/ref_proc.nim. */
/* Local absolute paths and unrelated runtime code were removed. */

typedef struct tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ;

struct tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ {
	NI value;
};

N_LIB_PRIVATE N_NOINLINE(NI, readValue__ref95proc_u4)(tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ* reading_p0);
N_LIB_PRIVATE N_NOINLINE(tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ*, keepReading__ref95proc_u10)(tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ* reading_p0);

N_LIB_PRIVATE N_NOINLINE(NI, readValue__ref95proc_u4)(tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ* reading_p0) {
	NI result;
	if (!(reading_p0 == 0)) goto LA4_;
	result = ((NI)-1);
	goto LA2_;
LA4_: ;
	result = (*reading_p0).value;
LA2_: ;
	return result;
}

N_LIB_PRIVATE N_NOINLINE(tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ*, keepReading__ref95proc_u10)(tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ* reading_p0) {
	tyObject_ReadingcolonObjectType___8EkEo4jsvRYTKsMVQRmgZQ* result;
	result = NIM_NIL;
	eqcopy___ref95proc_u19(&result, reading_p0);
	return result;
}
