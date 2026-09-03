/* Nim 2.2.10: observed/nimcache/@mpair_api.nim.c.
 * Excerpt: struct, APIs, NimMain, constructor; runtime helper bodies omitted.
 * Local source paths normalized to <EXPERIMENT>. */

typedef struct AsmatiPair AsmatiPair;
struct AsmatiPair {
	int left;
	int right;
};

N_LIB_EXPORT N_CDECL(int, asmati_add)(int left_p0, int right_p1) {
	int result;
	NI TM__iF9aDiIi02Ch9bEIcrrUw8Hw_2;
	nimfr_("asmati_add", "<EXPERIMENT>/src/pair_api.nim");
{	result = (int)0;
	nimlf_(7, "<EXPERIMENT>/src/pair_api.nim");	if (nimAddInt(left_p0, right_p1, &TM__iF9aDiIi02Ch9bEIcrrUw8Hw_2)) { raiseOverflow(); goto BeforeRet_;
	};
	if (TM__iF9aDiIi02Ch9bEIcrrUw8Hw_2 < (-2147483647 -1) || TM__iF9aDiIi02Ch9bEIcrrUw8Hw_2 > 2147483647){ raiseOverflow(); goto BeforeRet_;
	}
	result = (NI32)(TM__iF9aDiIi02Ch9bEIcrrUw8Hw_2);
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_EXPORT N_CDECL(int, asmati_sum_pair)(AsmatiPair pair_p0) {
	int result;
	NI TM__iF9aDiIi02Ch9bEIcrrUw8Hw_3;
	nimfr_("asmati_sum_pair", "<EXPERIMENT>/src/pair_api.nim");
{	result = (int)0;
	nimln_(10);	if (nimAddInt(pair_p0.left, pair_p0.right, &TM__iF9aDiIi02Ch9bEIcrrUw8Hw_3)) { raiseOverflow(); goto BeforeRet_;
	};
	if (TM__iF9aDiIi02Ch9bEIcrrUw8Hw_3 < (-2147483647 -1) || TM__iF9aDiIi02Ch9bEIcrrUw8Hw_3 > 2147483647){ raiseOverflow(); goto BeforeRet_;
	}
	result = (NI32)(TM__iF9aDiIi02Ch9bEIcrrUw8Hw_3);
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_EXPORT N_CDECL(void, NimMain)(void) {
#if 0
	void (*volatile inner)(void);
	PreMain();
	inner = NimMainInner;
	(*inner)();
#else
	PreMain();
	NimMainInner();
#endif
}

N_LIB_PRIVATE void NIM_POSIX_INIT NimMainInit(void) {
	NimMain();
}
