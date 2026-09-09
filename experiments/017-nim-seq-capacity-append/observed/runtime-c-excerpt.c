/* Nim 2.2.10 observed/nimcache/@psystem.nim.c.
 * Selected seq append, allocation, growth, and reallocation helpers only. */

N_LIB_PRIVATE N_NIMCALL(void, add__seq95capacity_u210)(tySequence__qwqHTkRvwhrRyENtudHQ7g* x_p0, NI y_p1) {
	NI oldLen_1;
	NI T1_;
	tyObject_NimSeqV2__iBLQBZISDVbzop0Kpde9bgw* xu_1;
	NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_138;
{	T1_ = (*x_p0).len;
	oldLen_1 = T1_;
	xu_1 = ((tyObject_NimSeqV2__iBLQBZISDVbzop0Kpde9bgw*) (x_p0));
	{
		NIM_BOOL T4_;
		NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_137;
		void* T8_;
		T4_ = (NIM_BOOL)0;
		T4_ = ((*xu_1).p == ((tyObject_NimSeqPayload__derV431WzYFLuE9bQM0SCfg*) NIM_NIL));
		if (T4_) goto LA5_;
		if (nimAddInt(oldLen_1, ((NI)1), &TM__Q5wkpxktOdTGvlSRo9bzt9aw_137)) { raiseOverflow(); goto BeforeRet_;
		};
		T4_ = ((NI)((*(*xu_1).p).cap & ((NI)IL64(-4611686018427387905))) < (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_137));
LA5_: ;
		if (!T4_) goto LA6_;
		T8_ = (void*)0;
		T8_ = prepareSeqAddUninit(oldLen_1, ((void*) ((*xu_1).p)), ((NI)1), ((NI)8), ((NI)8));
		(*xu_1).p = ((tyObject_NimSeqPayload__derV431WzYFLuE9bQM0SCfg*) (T8_));
	}
LA6_: ;
	if (nimAddInt(oldLen_1, ((NI)1), &TM__Q5wkpxktOdTGvlSRo9bzt9aw_138)) { raiseOverflow(); goto BeforeRet_;
	};
	(*xu_1).len = (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_138);
	(*(*xu_1).p).data[oldLen_1] = y_p1;
	}BeforeRet_: ;
}

N_LIB_PRIVATE N_NIMCALL(void*, newSeqPayloadUninit)(NI cap_p0, NI elemSize_p1, NI elemAlign_p2) {
	void* result;
{	result = (void*)0;
	{
		tyObject_NimSeqPayloadBase__PzjcziHuiUFb0I9cLrjAqww* p_1;
		NI T5_;
		NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_11;
		NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_12;
		void* T6_;
		if (!(((NI)0) < cap_p0)) goto LA3_;
		T5_ = (NI)0;
		T5_ = align__system_u1648(((NI)8), elemAlign_p2);
		if (nimMulInt(cap_p0, elemSize_p1, &TM__Q5wkpxktOdTGvlSRo9bzt9aw_11)) { raiseOverflow(); goto BeforeRet_;
		};
		if (nimAddInt(T5_, (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_11), &TM__Q5wkpxktOdTGvlSRo9bzt9aw_12)) { raiseOverflow(); goto BeforeRet_;
		};
		if (((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_12)) < ((NI)0) || ((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_12)) > ((NI)IL64(9223372036854775807))){ raiseRangeErrorI((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_12), ((NI)0), ((NI)IL64(9223372036854775807))); goto BeforeRet_;
		}
		if ((elemAlign_p2) < ((NI)0) || (elemAlign_p2) > ((NI)IL64(9223372036854775807))){ raiseRangeErrorI(elemAlign_p2, ((NI)0), ((NI)IL64(9223372036854775807))); goto BeforeRet_;
		}
		T6_ = (void*)0;
		T6_ = alignedAlloc__system_u1928(((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_12)), (elemAlign_p2));
		p_1 = ((tyObject_NimSeqPayloadBase__PzjcziHuiUFb0I9cLrjAqww*) (T6_));
		(*p_1).cap = cap_p0;
		result = ((void*) (p_1));
	}
	goto LA1_;
LA3_: ;
	{
		result = NIM_NIL;
	}
LA1_: ;
	}BeforeRet_: ;
	return result;
}

static N_INLINE(NI, resize__system_u2291)(NI old_p0) {
	NI result;
	result = (NI)0;
	{
		if (!(old_p0 <= ((NI)0))) goto LA3_;
		result = ((NI)4);
	}
	goto LA1_;
LA3_: ;
	{
		if (!(old_p0 <= ((NI)32767))) goto LA6_;
		result = (NI)(old_p0 * ((NI)2));
	}
	goto LA1_;
LA6_: ;
	{
		result = (NI)((NI)(old_p0 / ((NI)2)) + old_p0);
	}
LA1_: ;
	return result;
}

N_LIB_PRIVATE N_NIMCALL(void*, prepareSeqAddUninit)(NI len_p0, void* p_p1, NI addlen_p2, NI elemSize_p3, NI elemAlign_p4) {
	void* result;
	NI headerSize_1;
{	result = (void*)0;
	headerSize_1 = align__system_u1648(((NI)8), elemAlign_p4);
	{
		if (!(addlen_p2 <= ((NI)0))) goto LA3_;
		result = p_p1;
	}
	goto LA1_;
LA3_: ;
	{
		NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_13;
		if (!(p_p1 == NIM_NIL)) goto LA6_;
		if (nimAddInt(len_p0, addlen_p2, &TM__Q5wkpxktOdTGvlSRo9bzt9aw_13)) { raiseOverflow(); goto BeforeRet_;
		};
		result = newSeqPayloadUninit((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_13), elemSize_p3, elemAlign_p4);
	}
	goto LA1_;
LA6_: ;
	{
		tyObject_NimSeqPayloadBase__PzjcziHuiUFb0I9cLrjAqww* p_2;
		NI oldCap_1;
		NI newCap_1;
		NI T9_;
		NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_14;
		p_2 = ((tyObject_NimSeqPayloadBase__PzjcziHuiUFb0I9cLrjAqww*) (p_p1));
		oldCap_1 = (NI)((*p_2).cap & ((NI)IL64(-4611686018427387905)));
		T9_ = (NI)0;
		T9_ = resize__system_u2291(oldCap_1);
		if (nimAddInt(len_p0, addlen_p2, &TM__Q5wkpxktOdTGvlSRo9bzt9aw_14)) { raiseOverflow(); goto BeforeRet_;
		};
		newCap_1 = ((T9_ >= (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_14)) ? T9_ : (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_14));
		{
			tyObject_NimSeqPayloadBase__PzjcziHuiUFb0I9cLrjAqww* q_1;
			NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_15;
			NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_16;
			void* T14_;
			NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_17;
			if (!((NI)((*p_2).cap & ((NI)IL64(4611686018427387904))) == ((NI)IL64(4611686018427387904)))) goto LA12_;
			if (nimMulInt(elemSize_p3, newCap_1, &TM__Q5wkpxktOdTGvlSRo9bzt9aw_15)) { raiseOverflow(); goto BeforeRet_;
			};
			if (nimAddInt(headerSize_1, (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_15), &TM__Q5wkpxktOdTGvlSRo9bzt9aw_16)) { raiseOverflow(); goto BeforeRet_;
			};
			if (((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_16)) < ((NI)0) || ((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_16)) > ((NI)IL64(9223372036854775807))){ raiseRangeErrorI((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_16), ((NI)0), ((NI)IL64(9223372036854775807))); goto BeforeRet_;
			}
			if ((elemAlign_p4) < ((NI)0) || (elemAlign_p4) > ((NI)IL64(9223372036854775807))){ raiseRangeErrorI(elemAlign_p4, ((NI)0), ((NI)IL64(9223372036854775807))); goto BeforeRet_;
			}
			T14_ = (void*)0;
			T14_ = alignedAlloc__system_u1928(((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_16)), (elemAlign_p4));
			q_1 = ((tyObject_NimSeqPayloadBase__PzjcziHuiUFb0I9cLrjAqww*) (T14_));
			if (nimMulInt(len_p0, elemSize_p3, &TM__Q5wkpxktOdTGvlSRo9bzt9aw_17)) { raiseOverflow(); goto BeforeRet_;
			};
			if (((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_17)) < ((NI)0) || ((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_17)) > ((NI)IL64(9223372036854775807))){ raiseRangeErrorI((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_17), ((NI)0), ((NI)IL64(9223372036854775807))); goto BeforeRet_;
			}
			copyMem__system_u1755(((void*) ((NU)((NU64)(((NU) (ptrdiff_t) (q_1))) + (NU64)(((NU) (headerSize_1)))))), ((void*) ((NU)((NU64)(((NU) (ptrdiff_t) (p_2))) + (NU64)(((NU) (headerSize_1)))))), ((NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_17)));
			(*q_1).cap = newCap_1;
			result = ((void*) (q_1));
		}
		goto LA10_;
LA12_: ;
		{
			NI oldSize_1;
			NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_18;
			NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_19;
			NI newSize_1;
			NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_20;
			NI TM__Q5wkpxktOdTGvlSRo9bzt9aw_21;
			tyObject_NimSeqPayloadBase__PzjcziHuiUFb0I9cLrjAqww* q_2;
			void* T16_;
			if (nimMulInt(elemSize_p3, oldCap_1, &TM__Q5wkpxktOdTGvlSRo9bzt9aw_18)) { raiseOverflow(); goto BeforeRet_;
			};
			if (nimAddInt(headerSize_1, (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_18), &TM__Q5wkpxktOdTGvlSRo9bzt9aw_19)) { raiseOverflow(); goto BeforeRet_;
			};
			oldSize_1 = (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_19);
			if (nimMulInt(elemSize_p3, newCap_1, &TM__Q5wkpxktOdTGvlSRo9bzt9aw_20)) { raiseOverflow(); goto BeforeRet_;
			};
			if (nimAddInt(headerSize_1, (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_20), &TM__Q5wkpxktOdTGvlSRo9bzt9aw_21)) { raiseOverflow(); goto BeforeRet_;
			};
			newSize_1 = (NI)(TM__Q5wkpxktOdTGvlSRo9bzt9aw_21);
			if ((oldSize_1) < ((NI)0) || (oldSize_1) > ((NI)IL64(9223372036854775807))){ raiseRangeErrorI(oldSize_1, ((NI)0), ((NI)IL64(9223372036854775807))); goto BeforeRet_;
			}
			if ((newSize_1) < ((NI)0) || (newSize_1) > ((NI)IL64(9223372036854775807))){ raiseRangeErrorI(newSize_1, ((NI)0), ((NI)IL64(9223372036854775807))); goto BeforeRet_;
			}
			if ((elemAlign_p4) < ((NI)0) || (elemAlign_p4) > ((NI)IL64(9223372036854775807))){ raiseRangeErrorI(elemAlign_p4, ((NI)0), ((NI)IL64(9223372036854775807))); goto BeforeRet_;
			}
			T16_ = (void*)0;
			T16_ = alignedRealloc__system_u1984(((void*) (p_2)), (oldSize_1), (newSize_1), (elemAlign_p4));
			q_2 = ((tyObject_NimSeqPayloadBase__PzjcziHuiUFb0I9cLrjAqww*) (T16_));
			(*q_2).cap = newCap_1;
			result = ((void*) (q_2));
		}
LA10_: ;
	}
LA1_: ;
	}BeforeRet_: ;
	return result;
}

N_LIB_PRIVATE N_NIMCALL(void*, alignedRealloc__system_u1984)(void* p_p0, NI oldSize_p1, NI newSize_p2, NI align_p3) {
	void* result;
	{
		if (!(align_p3 <= ((NI)16))) goto LA3_;
		result = reallocSharedImpl__system_u1790(p_p0, newSize_p2);
	}
	goto LA1_;
LA3_: ;
	{
		result = alignedAlloc__system_u1928(newSize_p2, align_p3);
		copyMem__system_u1755(result, p_p0, oldSize_p1);
		alignedDealloc(p_p0, align_p3);
	}
LA1_: ;
	return result;
}
