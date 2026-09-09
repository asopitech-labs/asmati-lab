/* Nim 2.2.10 observed/nimcache/@mseq_capacity.nim.c.
 * Selected seq layout, capacity, caller, and cleanup only.
 * Local paths normalized to <EXPERIMENT> and <NIM_ROOT>. */

struct tySequence__qwqHTkRvwhrRyENtudHQ7g {
  NI len; tySequence__qwqHTkRvwhrRyENtudHQ7g_Content* p;
};
struct tySequence__qwqHTkRvwhrRyENtudHQ7g_Content { NI cap; NI data[SEQ_DECL_SIZE]; };

static N_INLINE(NI, capacity__seq95capacity_u157)(tySequence__qwqHTkRvwhrRyENtudHQ7g self_p0);
N_LIB_PRIVATE N_NIMCALL(void, add__seq95capacity_u210)(tySequence__qwqHTkRvwhrRyENtudHQ7g* x_p0, NI y_p1);
N_LIB_PRIVATE N_NIMCALL(void, eqdestroy___seq95capacity_u53)(tySequence__qwqHTkRvwhrRyENtudHQ7g dest_p0);

static N_INLINE(NI, capacity__seq95capacity_u157)(tySequence__qwqHTkRvwhrRyENtudHQ7g self_p0) {
	NI result;
	tyObject_NimSeqV2__iBLQBZISDVbzop0Kpde9bgw* sek_1;
	NI T1_;
	sek_1 = ((tyObject_NimSeqV2__iBLQBZISDVbzop0Kpde9bgw*) ((&self_p0)));
	T1_ = (NI)0;
	{
		if (!!(((*sek_1).p == ((tyObject_NimSeqPayload__derV431WzYFLuE9bQM0SCfg*) NIM_NIL)))) goto LA4_;
		result = (NI)((*(*sek_1).p).cap & ((NI)IL64(-4611686018427387905)));
	}
	goto LA2_;
LA4_: ;
	{
		result = ((NI)0);
	}
LA2_: ;
	return result;
}

N_LIB_PRIVATE N_NIMCALL(void, eqdestroy___seq95capacity_u53)(tySequence__qwqHTkRvwhrRyENtudHQ7g dest_p0) {
	if (dest_p0.p && !(dest_p0.p->cap & NIM_STRLIT_FLAG)) {
 alignedDealloc(dest_p0.p, NIM_ALIGNOF(NI));
}
}

N_LIB_PRIVATE N_NIMCALL(void, NimMainModule)(void) {
{
NIM_BOOL* nimErr_;
	nimfr_("seq_capacity", "<EXPERIMENT>/src/seq_capacity.nim");
nimErr_ = nimErrorFlag();
	nimlf_(10, "<EXPERIMENT>/src/seq_capacity.nim");	show__seq95capacity_u151(((NI)0), values__seq95capacity_u204);
	if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
	{
		NI res_1;
		nimlf_(96, "<NIM_ROOT>/lib/system/iterators_1.nim");		res_1 = ((NI)1);
		{
			nimln_(97);			while (1) {
				NI TM__7f6eHQmXG3OLDck8uMerow_13;
				if (!(res_1 <= ((NI)10))) goto LA3;
				nimlf_(11, "<EXPERIMENT>/src/seq_capacity.nim");				value__seq95capacity_u209 = ((NI) (res_1));
				nimln_(12);				add__seq95capacity_u210((&values__seq95capacity_u204), value__seq95capacity_u209);
				nimln_(13);				show__seq95capacity_u151(value__seq95capacity_u209, values__seq95capacity_u204);
				if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
				nimlf_(102, "<NIM_ROOT>/lib/system/iterators_1.nim");				if (nimAddInt(res_1, ((NI)1), &TM__7f6eHQmXG3OLDck8uMerow_13)) { raiseOverflow(); goto BeforeRet_;
				};
				res_1 = (NI)(TM__7f6eHQmXG3OLDck8uMerow_13);
			} LA3: ;
		}
	}
	nimlf_(2, "<EXPERIMENT>/src/seq_capacity.nim");	eqdestroy___seq95capacity_u53(values__seq95capacity_u204);
	BeforeRet_: ;
	nimTestErrorFlag();
	popFrame();
}
}
