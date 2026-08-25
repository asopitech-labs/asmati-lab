/* Extracted from Nim 2.2.10 generated C for src/scalar_proc.nim. */
/* Local absolute paths were removed from the excerpt. */

#define NIM_INTBITS 64

/* nimbase.h */
#define N_NIMCALL(rettype, name) rettype name /* no modifier */
typedef NI64 NI;
typedef double NF;

/* @mscalar_proc.nim.c */
N_LIB_PRIVATE N_NIMCALL(NI, noArgs__scalar95proc_u1)(void);
N_LIB_PRIVATE N_NIMCALL(NI, addOne__scalar95proc_u3)(NI x_p0);
N_LIB_PRIVATE N_NIMCALL(NF, half__scalar95proc_u6)(NF x_p0);

N_LIB_PRIVATE N_NIMCALL(NI, noArgs__scalar95proc_u1)(void) {
	NI result;
	result = ((NI)7);
	return result;
}

N_LIB_PRIVATE N_NIMCALL(NI, addOne__scalar95proc_u3)(NI x_p0) {
	NI result;
	NI tmp;
	result = (NI)0;
	if (nimAddInt(x_p0, ((NI)1), &tmp)) {
		raiseOverflow();
		goto BeforeRet_;
	}
	result = (NI)(tmp);
BeforeRet_:
	return result;
}

N_LIB_PRIVATE N_NIMCALL(NF, half__scalar95proc_u6)(NF x_p0) {
	NF result;
	result = ((NF)(x_p0) / (NF)(2.0));
	return result;
}
