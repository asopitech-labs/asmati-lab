/*
 * Nim 2.2.10が同じsourceから生成した対象関数の抜粋。
 * debug内のabsolute source pathだけをsrc/overflow_compare.nimへ正規化した。
 */

/* debug: opt none */
N_LIB_PRIVATE N_NOINLINE(NI, addOne__overflow95compare_u3)(NI value_p0) {
	NI result;
	NI TM__xElOhXHrKGBgXfy2Ox0w7A_4;
	nimfr_("addOne", "src/overflow_compare.nim");
{	result = (NI)0;
	nimlf_(4, "src/overflow_compare.nim");	if (nimAddInt(value_p0, ((NI)1), &TM__xElOhXHrKGBgXfy2Ox0w7A_4)) { raiseOverflow(); goto BeforeRet_;
	};
	result = (NI)(TM__xElOhXHrKGBgXfy2Ox0w7A_4);
	}BeforeRet_: ;
	popFrame();
	return result;
}

/* release: -d:release / opt speed / Clang -O3 */
N_LIB_PRIVATE N_NOINLINE(NI, addOne__overflow95compare_u3)(NI value_p0) {
	NI result;
	NI TM__xElOhXHrKGBgXfy2Ox0w7A_4;
{	result = (NI)0;
	if (nimAddInt(value_p0, ((NI)1), &TM__xElOhXHrKGBgXfy2Ox0w7A_4)) { raiseOverflow(); goto BeforeRet_;
	};
	result = (NI)(TM__xElOhXHrKGBgXfy2Ox0w7A_4);
	}BeforeRet_: ;
	return result;
}

/* debug @psystem.nim.c */
N_LIB_PRIVATE N_NOINLINE(void, raiseOverflow)(void) {
	sysFatal__system_u5089(TM__Q5wkpxktOdTGvlSRo9bzt9aw_31);
}

/* release @psystem.nim.c */
N_LIB_PRIVATE N_NOINLINE(void, raiseOverflow)(void) {
	sysFatal__system_u5003(TM__Q5wkpxktOdTGvlSRo9bzt9aw_24);
}
