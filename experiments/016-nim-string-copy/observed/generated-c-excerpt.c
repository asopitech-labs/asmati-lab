/* Nim 2.2.10 observed/nimcache/@mstring_copy.nim.c.
 * Selected string layout, pass/return functions, mutation guard, and caller only.
 * Local paths normalized to <EXPERIMENT> and <NIM_ROOT>. */

struct NimStringV2 {
	NI len;
	NimStrPayload* p;
};

N_LIB_PRIVATE N_NOINLINE(NIM_BOOL, passAliases__string95copy_u4)(NimStringV2 value_p0, void* expected_p1);
N_LIB_PRIVATE N_NOINLINE(NimStringV2, identity__string95copy_u8)(NimStringV2 value_p0);

N_LIB_PRIVATE N_NOINLINE(NIM_BOOL, passAliases__string95copy_u4)(NimStringV2 value_p0, void* expected_p1) {
	NIM_BOOL result;
	void* T1_;
NIM_BOOL* nimErr_;
	nimfr_("passAliases", "<EXPERIMENT>/src/string_copy.nim");
{nimErr_ = nimErrorFlag();
	result = (NIM_BOOL)0;
	nimln_(8);	T1_ = (void*)0;
	T1_ = address__string95copy_u1(value_p0);
	if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
	result = (T1_ == expected_p1);
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NOINLINE(NimStringV2, identity__string95copy_u8)(NimStringV2 value_p0) {
	NimStringV2 result;
	nimfr_("identity", "<EXPERIMENT>/src/string_copy.nim");
	result.len = 0; result.p = NIM_NIL;
	nimlf_(1715, "<NIM_ROOT>/lib/system.nim");	eqcopy___system_u2754((&result), value_p0);
	popFrame();
	return result;
}

static N_INLINE(void, nimPrepareStrMutationV2)(NimStringV2* s_p0) {
	{
		NIM_BOOL T3_;
		T3_ = (NIM_BOOL)0;
		T3_ = !(((*s_p0).p == ((NimStrPayload*) NIM_NIL)));
		if (!(T3_)) goto LA4_;
		T3_ = ((NI)((*(*s_p0).p).cap & ((NI)IL64(4611686018427387904))) == ((NI)IL64(4611686018427387904)));
LA4_: ;
		if (!T3_) goto LA5_;
		nimPrepareStrMutationImpl__system_u2493(s_p0);
	}
LA5_: ;
}

N_LIB_PRIVATE N_NIMCALL(void, NimMainModule)(void) {
{
	NimStringV2 colontmpD_;
	NimStringV2 colontmpD__2;
	NimStringV2 colontmpD__3;
	NimStringV2 colontmpD__4;
	NimStringV2 colontmpD__5;
	NimStringV2 colontmpD__6;
	void* T2_;
	tyArray__A2YC0h9cZydgH7zGAndH9bLg T3_;
	NIM_BOOL T4_;
	NimStringV2 T5_;
	tyArray__A2YC0h9cZydgH7zGAndH9bLg T6_;
	void* T7_;
	tyArray__A2YC0h9cZydgH7zGAndH9bLg T8_;
	void* T9_;
	tyArray__A2YC0h9cZydgH7zGAndH9bLg T10_;
	void* T11_;
NIM_BOOL* nimErr_;
	nimfr_("string_copy", "<EXPERIMENT>/src/string_copy.nim");
nimErr_ = nimErrorFlag();
	colontmpD_.len = 0; colontmpD_.p = NIM_NIL;
	colontmpD__2.len = 0; colontmpD__2.p = NIM_NIL;
	colontmpD__3.len = 0; colontmpD__3.p = NIM_NIL;
	colontmpD__4.len = 0; colontmpD__4.p = NIM_NIL;
	colontmpD__5.len = 0; colontmpD__5.p = NIM_NIL;
	colontmpD__6.len = 0; colontmpD__6.p = NIM_NIL;
	nimlf_(13, "<EXPERIMENT>/src/string_copy.nim");	original__string95copy_u11 = mnewString(((NI)4));
	nimln_(14);	if (((NI)0) < 0 || ((NI)0) >= original__string95copy_u11.len){ raiseIndexError2(((NI)0),original__string95copy_u11.len-1); goto LA1_;
	}
	nimPrepareStrMutationV2((&original__string95copy_u11));
	original__string95copy_u11.p->data[((NI)0)] = 65;
	nimln_(15);	if (((NI)1) < 0 || ((NI)1) >= original__string95copy_u11.len){ raiseIndexError2(((NI)1),original__string95copy_u11.len-1); goto LA1_;
	}
	nimPrepareStrMutationV2((&original__string95copy_u11));
	original__string95copy_u11.p->data[((NI)1)] = 66;
	nimln_(16);	if (((NI)2) < 0 || ((NI)2) >= original__string95copy_u11.len){ raiseIndexError2(((NI)2),original__string95copy_u11.len-1); goto LA1_;
	}
	nimPrepareStrMutationV2((&original__string95copy_u11));
	original__string95copy_u11.p->data[((NI)2)] = 67;
	nimln_(17);	if (((NI)3) < 0 || ((NI)3) >= original__string95copy_u11.len){ raiseIndexError2(((NI)3),original__string95copy_u11.len-1); goto LA1_;
	}
	nimPrepareStrMutationV2((&original__string95copy_u11));
	original__string95copy_u11.p->data[((NI)3)] = 68;
	nimln_(19);	T2_ = (void*)0;
	T2_ = address__string95copy_u1(original__string95copy_u11);
	if (NIM_UNLIKELY(*nimErr_)) goto LA1_;
	originalAddress__string95copy_u12 = T2_;
	nimln_(20);	T3_[0] = TM__bynQK8UxcTCG80ulN4H02w_3;
	colontmpD_ = dollar___systemZdollars_u14(original__string95copy_u11.len);
	if (NIM_UNLIKELY(*nimErr_)) goto LA1_;
	T3_[1] = colontmpD_;
	T3_[2] = TM__bynQK8UxcTCG80ulN4H02w_5;
	T4_ = (NIM_BOOL)0;
	T4_ = passAliases__string95copy_u4(original__string95copy_u11, originalAddress__string95copy_u12);
	if (NIM_UNLIKELY(*nimErr_)) goto LA1_;
	colontmpD__2 = nimBoolToStr(T4_);
	T3_[3] = colontmpD__2;
	T3_[4] = TM__bynQK8UxcTCG80ulN4H02w_7;
	T3_[5] = original__string95copy_u11;
	echoBinSafe(T3_, 6);
	nimln_(23);	T5_.len = 0; T5_.p = NIM_NIL;
	T5_ = identity__string95copy_u8(original__string95copy_u11);
	if (NIM_UNLIKELY(*nimErr_)) {eqdestroy___system_u281(T5_); goto LA1_;}
	returned__string95copy_u13 = T5_;
	nimln_(24);	T6_[0] = TM__bynQK8UxcTCG80ulN4H02w_9;
	colontmpD__3 = dollar___systemZdollars_u14(returned__string95copy_u13.len);
	if (NIM_UNLIKELY(*nimErr_)) goto LA1_;
	T6_[1] = colontmpD__3;
	T6_[2] = TM__bynQK8UxcTCG80ulN4H02w_10;
	T7_ = (void*)0;
	T7_ = address__string95copy_u1(returned__string95copy_u13);
	if (NIM_UNLIKELY(*nimErr_)) goto LA1_;
	colontmpD__4 = nimBoolToStr((T7_ == originalAddress__string95copy_u12));
	T6_[3] = colontmpD__4;
	T6_[4] = TM__bynQK8UxcTCG80ulN4H02w_11;
	T6_[5] = returned__string95copy_u13;
	echoBinSafe(T6_, 6);
	nimlf_(1715, "<NIM_ROOT>/lib/system.nim");	eqcopy___system_u2754((&assigned__string95copy_u14), original__string95copy_u11);
	nimlf_(28, "<EXPERIMENT>/src/string_copy.nim");	T8_[0] = TM__bynQK8UxcTCG80ulN4H02w_13;
	T9_ = (void*)0;
	T9_ = address__string95copy_u1(assigned__string95copy_u14);
	if (NIM_UNLIKELY(*nimErr_)) goto LA1_;
	colontmpD__5 = nimBoolToStr((T9_ == originalAddress__string95copy_u12));
	T8_[1] = colontmpD__5;
	T8_[2] = TM__bynQK8UxcTCG80ulN4H02w_15;
	T8_[3] = original__string95copy_u11;
	T8_[4] = TM__bynQK8UxcTCG80ulN4H02w_17;
	T8_[5] = assigned__string95copy_u14;
	echoBinSafe(T8_, 6);
	nimln_(31);	if (((NI)0) < 0 || ((NI)0) >= assigned__string95copy_u14.len){ raiseIndexError2(((NI)0),assigned__string95copy_u14.len-1); goto LA1_;
	}
	nimPrepareStrMutationV2((&assigned__string95copy_u14));
	assigned__string95copy_u14.p->data[((NI)0)] = 90;
	nimln_(32);	T10_[0] = TM__bynQK8UxcTCG80ulN4H02w_19;
	T11_ = (void*)0;
	T11_ = address__string95copy_u1(assigned__string95copy_u14);
	if (NIM_UNLIKELY(*nimErr_)) goto LA1_;
	colontmpD__6 = nimBoolToStr((T11_ == originalAddress__string95copy_u12));
	T10_[1] = colontmpD__6;
	T10_[2] = TM__bynQK8UxcTCG80ulN4H02w_20;
	T10_[3] = original__string95copy_u11;
	T10_[4] = TM__bynQK8UxcTCG80ulN4H02w_21;
	T10_[5] = assigned__string95copy_u14;
	echoBinSafe(T10_, 6);
	{
		LA1_:;
	}
	{
		nimlf_(394, "<NIM_ROOT>/lib/system.nim");		if (colontmpD__6.p && !(colontmpD__6.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(colontmpD__6.p);
}
		if (colontmpD__5.p && !(colontmpD__5.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(colontmpD__5.p);
}
		if (colontmpD__4.p && !(colontmpD__4.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(colontmpD__4.p);
}
		if (colontmpD__3.p && !(colontmpD__3.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(colontmpD__3.p);
}
		if (colontmpD__2.p && !(colontmpD__2.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(colontmpD__2.p);
}
		if (colontmpD_.p && !(colontmpD_.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(colontmpD_.p);
}
	}
	if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
	if (assigned__string95copy_u14.p && !(assigned__string95copy_u14.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(assigned__string95copy_u14.p);
}
	if (returned__string95copy_u13.p && !(returned__string95copy_u13.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(returned__string95copy_u13.p);
}
	if (original__string95copy_u11.p && !(original__string95copy_u11.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(original__string95copy_u11.p);
}
	BeforeRet_: ;
	nimTestErrorFlag();
	popFrame();
}
}
