/* Nim 2.2.10 observed/nimcache/@psystem.nim.c.
 * Selected string assignment and literal-mutation helpers only. */

N_LIB_PRIVATE N_NIMCALL(void, nimAsgnStrV2)(NimStringV2* a_p0, NimStringV2 b_p1) {
{	{
		NIM_BOOL T3_;
		T3_ = (NIM_BOOL)0;
		T3_ = ((*a_p0).p == b_p1.p);
		if (!(T3_)) goto LA4_;
		T3_ = ((*a_p0).len == b_p1.len);
LA4_: ;
		if (!T3_) goto LA5_;
		goto BeforeRet_;
	}
LA5_: ;
	{
		NIM_BOOL T9_;
		T9_ = (NIM_BOOL)0;
		T9_ = (b_p1.p == ((NimStrPayload*) NIM_NIL));
		if (T9_) goto LA10_;
		T9_ = ((NI)((*b_p1.p).cap & ((NI)IL64(4611686018427387904))) == ((NI)IL64(4611686018427387904)));
LA10_: ;
		if (!T9_) goto LA11_;
		{
			NIM_BOOL T15_;
			T15_ = (NIM_BOOL)0;
			T15_ = ((*a_p0).p == ((NimStrPayload*) NIM_NIL));
			if (T15_) goto LA16_;
			T15_ = ((NI)((*(*a_p0).p).cap & ((NI)IL64(4611686018427387904))) == ((NI)IL64(4611686018427387904)));
LA16_: ;
			if (!!(T15_)) goto LA17_;
			deallocShared(((void*) ((*a_p0).p)));
		}
LA17_: ;
		(*a_p0).len = b_p1.len;
		(*a_p0).p = b_p1.p;
	}
	goto LA7_;
LA11_: ;
	{
		{
			NIM_BOOL T22_;
			NIM_BOOL T23_;
			void* T34_;
			T22_ = (NIM_BOOL)0;
			T23_ = (NIM_BOOL)0;
			T23_ = ((*a_p0).p == ((NimStrPayload*) NIM_NIL));
			if (T23_) goto LA24_;
			T23_ = ((NI)((*(*a_p0).p).cap & ((NI)IL64(4611686018427387904))) == ((NI)IL64(4611686018427387904)));
LA24_: ;
			T22_ = T23_;
			if (T22_) goto LA25_;
			T22_ = ((NI)((*(*a_p0).p).cap & ((NI)IL64(-4611686018427387905))) < b_p1.len);
LA25_: ;
			if (!T22_) goto LA26_;
			{
				NIM_BOOL T30_;
				T30_ = (NIM_BOOL)0;
				T30_ = ((*a_p0).p == ((NimStrPayload*) NIM_NIL));
				if (T30_) goto LA31_;
				T30_ = ((NI)((*(*a_p0).p).cap & ((NI)IL64(4611686018427387904))) == ((NI)IL64(4611686018427387904)));
LA31_: ;
				if (!!(T30_)) goto LA32_;
				deallocShared(((void*) ((*a_p0).p)));
			}
LA32_: ;
			T34_ = (void*)0;
			T34_ = allocSharedImpl(((NI)((NI)(b_p1.len + ((NI)1)) + ((NI)8))));
			(*a_p0).p = ((NimStrPayload*) (T34_));
			(*(*a_p0).p).cap = b_p1.len;
		}
LA26_: ;
		(*a_p0).len = b_p1.len;
		copyMem__system_u1755(((void*) ((&(*(*a_p0).p).data[((NI)0)]))), ((void*) ((&(*b_p1.p).data[((NI)0)]))), ((NI)(b_p1.len + ((NI)1))));
	}
LA7_: ;
	}BeforeRet_: ;
}

N_LIB_PRIVATE N_NIMCALL(void, eqcopy___system_u2754)(NimStringV2* dest_p0, NimStringV2 src_p1) {
	nimAsgnStrV2(((NimStringV2*) (dest_p0)), src_p1);
}

N_LIB_PRIVATE N_NIMCALL(void, nimPrepareStrMutationImpl__system_u2493)(NimStringV2* s_p0) {
	NimStrPayload* oldP_1;
	void* T1_;
	oldP_1 = (*s_p0).p;
	T1_ = (void*)0;
	T1_ = allocSharedImpl(((NI)((NI)((*s_p0).len + ((NI)1)) + ((NI)8))));
	(*s_p0).p = ((NimStrPayload*) (T1_));
	(*(*s_p0).p).cap = (*s_p0).len;
	copyMem__system_u1755(((void*) ((&(*(*s_p0).p).data[((NI)0)]))), ((void*) ((&(*oldP_1).data[((NI)0)]))), ((NI)((*s_p0).len + ((NI)1))));
}
