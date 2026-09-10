/* Nim 2.2.10 observed/nimcache/@mobject_layout.nim.c.
 * Selected int width, Sample struct, declaration, and field access only.
 * Local paths normalized to <EXPERIMENT> and <NIM_ROOT>. */

#define NIM_INTBITS 64

struct tyObject_Sample__YFx0SAQAdiQmBoAD29byMtQ {
	NI count;
	NIM_BOOL enabled;
	NF ratio;
};

N_LIB_PRIVATE N_NOINLINE(NF, score__object95layout_u5)(tyObject_Sample__YFx0SAQAdiQmBoAD29byMtQ sample_p0);

N_LIB_PRIVATE N_NOINLINE(NF, score__object95layout_u5)(tyObject_Sample__YFx0SAQAdiQmBoAD29byMtQ sample_p0) {
	NF result;
	NF T1_;
	nimfr_("score", "<EXPERIMENT>/src/object_layout.nim");
	T1_ = (NF)0;
	nimlf_(8, "<EXPERIMENT>/src/object_layout.nim");	{
		if (!sample_p0.enabled) goto LA4_;
		nimln_(7);		nimln_(9);		result = ((NF)(((NF) (sample_p0.count))) * (NF)(sample_p0.ratio));
	}
	goto LA2_;
LA4_: ;
	{
		nimln_(7);		nimln_(11);		result = 0.0;
	}
LA2_: ;
	popFrame();
	return result;
}
