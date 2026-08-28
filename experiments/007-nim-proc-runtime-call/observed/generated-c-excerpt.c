/*
 * Nim 2.2.10がsrc/proc_runtime.nimから生成したCの関係箇所を抜粋した。
 * source pathを含むdebug line、stack frame bookkeepingは除外した。
 * 残した行の式と制御構造は生成Cのままである。
 */
struct NimStringV2 {
  NI len;
  NimStrPayload* p;
};

static N_INLINE(void, nimCopyMem)(void* dest_p0, void* source_p1, NI size_p2) {
	void* T1_;
	T1_ = (void*)0;
	T1_ = memcpy(dest_p0, source_p1, ((size_t) (size_p2)));
}
static N_INLINE(void, copyMem__system_u1755)(void* dest_p0, void* source_p1, NI size_p2) {
	nimCopyMem(dest_p0, source_p1, size_p2);
}
static N_INLINE(void, appendString)(NimStringV2* dest_p0, NimStringV2 src_p1) {
	{
		if (!(((NI)0) < src_p1.len)) goto LA3_;
		copyMem__system_u1755(((void*) ((&(*(*dest_p0).p).data[(*dest_p0).len]))), ((void*) ((&(*src_p1.p).data[((NI)0)]))), (src_p1.len));
		(*dest_p0).len += src_p1.len;
		(*(*dest_p0).p).data[(*dest_p0).len] = 0;
	}
LA3_: ;
}

N_LIB_PRIVATE N_NIMCALL(NimStringV2, addSuffix__proc95runtime_u1)(NimStringV2 value_p0) {
	NimStringV2 result;
	NimStringV2 T1_;
	/* debug location bookkeeping omitted */
	T1_.len = 0; T1_.p = NIM_NIL;
	T1_ = rawNewString(value_p0.len + 1);
appendString((&T1_), value_p0);
appendString((&T1_), TM__gDfDQgHjebac2MQAzYgKng_3); /* "!" */
	result = T1_;
	/* popFrame omitted */
	return result;
}

/* @psystem.nim.c */
N_LIB_PRIVATE N_NIMCALL(NimStringV2, rawNewString)(NI space_p0) {
	NimStringV2 result;
	nimZeroMem((void*)(&result), sizeof(NimStringV2));
	{
		if (!(space_p0 <= ((NI)0))) goto LA3_;
		result.len = ((NI)0);
		result.p = ((NimStrPayload*) NIM_NIL);
	}
	goto LA1_;
LA3_: ;
	{
		NimStrPayload* p_1;
		void* T6_;
		T6_ = (void*)0;
		T6_ = allocSharedImpl(((NI)((NI)(space_p0 + ((NI)1)) + ((NI)8))));
		p_1 = ((NimStrPayload*) (T6_));
		(*p_1).cap = space_p0;
		(*p_1).data[((NI)0)] = 0;
		result.len = ((NI)0);
		result.p = p_1;
	}
LA1_: ;
	return result;
}

/* NimMainModule内の呼び出し */
colontmpD_ = addSuffix__proc95runtime_u1(TM__gDfDQgHjebac2MQAzYgKng_5); /* "nim" */
