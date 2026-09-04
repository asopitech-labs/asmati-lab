/* Nim 2.2.10 observed/nimcache/@mbuffer_api.nim.c.
 * Excerpt: exported functions and constructor; helpers omitted.
 * Local source paths normalized to <EXPERIMENT>. */

N_LIB_EXPORT N_CDECL(size_t, asmati_trimmed_length)(NU8* input_p0, size_t length_p1) {
	size_t result;
	nimfr_("asmati_trimmed_length", "<EXPERIMENT>/src/buffer_api.nim");
	nimlf_(6, "<EXPERIMENT>/src/buffer_api.nim");	result = length_p1;
	{
		nimln_(7);		while (1) {
			NIM_BOOL T3_;
			T3_ = (NIM_BOOL)0;
			T3_ = ((NU64)(((NU)0)) < (NU64)(result));
			if (!(T3_)) goto LA4_;
			T3_ = (input_p0[(NU)((NU64)(result) - (NU64)(((NU)1)))] == ((NU8)0));
LA4_: ;
			if (!T3_) goto LA2;
			nimln_(8);			result -= ((NI)1);
		} LA2: ;
	}
	popFrame();
	return result;
}

static N_INLINE(size_t, min__buffer95api_u23)(size_t x_p0, size_t y_p1) {
	size_t result;
	size_t colontmpD_;
	size_t colontmpD__2;
	colontmpD_ = (size_t)0;
	colontmpD__2 = (size_t)0;
	{
		if (!((NU64)(x_p0) <= (NU64)(y_p1))) goto LA3_;
		colontmpD_ = x_p0;
		result = colontmpD_;
	}
	goto LA1_;
LA3_: ;
	{
		colontmpD__2 = y_p1;
		result = colontmpD__2;
	}
LA1_: ;
	return result;
}

N_LIB_EXPORT N_CDECL(size_t, asmati_write_label)(NU8* output_p0, size_t capacity_p1) {
	size_t result;
	size_t writable_1;
	size_t index_1;
	nimfr_("asmati_write_label", "<EXPERIMENT>/src/buffer_api.nim");
{	nimln_(13);	result = ((size_t)6);
	nimln_(14);	writable_1 = min__buffer95api_u23(capacity_p1, result);
	nimln_(15);	index_1 = ((size_t)0);
	{
		nimln_(16);		while (1) {
			if (!((NU64)(index_1) < (NU64)(writable_1))) goto LA2;
			nimln_(17);			if (index_1 > (size_t)(((NI)IL64(9223372036854775807)))){ raiseRangeErrorNoArgs(); goto BeforeRet_;
			}
			if ((NU)(((NI) (index_1))) > (NU)(5)){ raiseIndexError2(((NI) (index_1)), 5); goto BeforeRet_;
			}
			output_p0[index_1] = Label__buffer95api_u1[(((NI) (index_1)))- 0];
			nimln_(18);			index_1 += ((NI)1);
		} LA2: ;
	}
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE void NIM_POSIX_INIT NimMainInit(void) {
	NimMain();
}
