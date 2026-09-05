/* Nim 2.2.10 observed/nimcache/@mopenarray_slice.nim.c.
 * Selected openArray functions and caller lowering only.
 * Local source paths normalized to <EXPERIMENT> and <NIM_ROOT>. */

N_LIB_PRIVATE N_NOINLINE(tyTuple__FtZxsWeKlOo83uVL9c4OOmg, summarize__openarray95slice_u11)(NI* values_p0, NI values_p0Len_0);
N_LIB_PRIVATE N_NOINLINE(NIM_BOOL, sameAddress__openarray95slice_u46)(NI* values_p0, NI values_p0Len_0, NI* expected_p1);

N_LIB_PRIVATE N_NOINLINE(tyTuple__FtZxsWeKlOo83uVL9c4OOmg, summarize__openarray95slice_u11)(NI* values_p0, NI values_p0Len_0) {
	tyTuple__FtZxsWeKlOo83uVL9c4OOmg result;
NIM_BOOL* nimErr_;
	nimfr_("summarize", "<EXPERIMENT>/src/openarray_slice.nim");
{nimErr_ = nimErrorFlag();
	nimZeroMem((void*)(&result), sizeof(tyTuple__FtZxsWeKlOo83uVL9c4OOmg));
	nimlf_(6, "<EXPERIMENT>/src/openarray_slice.nim");	result.Field0 = values_p0Len_0;
	nimln_(7);	{
		NI T5_;
		if (!(((NI)0) < values_p0Len_0)) goto LA3_;
		nimln_(8);		if (((NI)0) < 0 || ((NI)0) >= values_p0Len_0){ raiseIndexError2(((NI)0),values_p0Len_0-1); goto BeforeRet_;
		}
		result.Field1 = values_p0[((NI)0)];
		nimln_(9);		T5_ = (NI)0;
		T5_ = X5BX5D___openarray95slice_u21(values_p0, values_p0Len_0, ((NI)1));
		if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
		result.Field2 = T5_;
		{
			NI* value_1;
			NI i_1;
			value_1 = (NI*)0;
			nimlf_(18, "<NIM_ROOT>/lib/system/iterators.nim");			i_1 = ((NI)0);
			{
				nimln_(19);				while (1) {
					NI TM__30qzQsuGDD9b5bJwkidVyyw_5;
					if (!(i_1 < values_p0Len_0)) goto LA8;
					nimlf_(10, "<EXPERIMENT>/src/openarray_slice.nim");					if (i_1 < 0 || i_1 >= values_p0Len_0){ raiseIndexError2(i_1,values_p0Len_0-1); goto BeforeRet_;
					}
					value_1 = (&values_p0[i_1]);
					nimln_(11);					if (nimAddInt(result.Field3, (*value_1), &TM__30qzQsuGDD9b5bJwkidVyyw_5)) { raiseOverflow(); goto BeforeRet_;
					};
					result.Field3 = (NI)(TM__30qzQsuGDD9b5bJwkidVyyw_5);
					nimlf_(13, "<NIM_ROOT>/lib/system/iterators.nim");					i_1 += ((NI)1);
				} LA8: ;
			}
		}
	}
LA3_: ;
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NOINLINE(NIM_BOOL, sameAddress__openarray95slice_u46)(NI* values_p0, NI values_p0Len_0, NI* expected_p1) {
	NIM_BOOL result;
	NIM_BOOL T1_;
	nimfr_("sameAddress", "<EXPERIMENT>/src/openarray_slice.nim");
{	nimlf_(14, "<EXPERIMENT>/src/openarray_slice.nim");	T1_ = (NIM_BOOL)0;
	T1_ = (((NI)0) < values_p0Len_0);
	if (!(T1_)) goto LA2_;
	if (((NI)0) < 0 || ((NI)0) >= values_p0Len_0){ raiseIndexError2(((NI)0),values_p0Len_0-1); goto BeforeRet_;
	}
	T1_ = ((&values_p0[((NI)0)]) == expected_p1);
LA2_: ;
	result = T1_;
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NIMCALL(void, NimMainModule)(void) {
{
	NimStringV2 colontmpD_;
NIM_BOOL* nimErr_;
	nimfr_("openarray_slice", "<EXPERIMENT>/src/openarray_slice.nim");
nimErr_ = nimErrorFlag();
	colontmpD_.len = 0; colontmpD_.p = NIM_NIL;
	nimlf_(23, "<EXPERIMENT>/src/openarray_slice.nim");	dynamicValues__openarray95slice_u126.len = 4; dynamicValues__openarray95slice_u126.p = (tySequence__qwqHTkRvwhrRyENtudHQ7g_Content*) newSeqPayload(4, sizeof(NI), NIM_ALIGNOF(NI));
	dynamicValues__openarray95slice_u126.p->data[0] = ((NI)10);
	dynamicValues__openarray95slice_u126.p->data[1] = ((NI)20);
	dynamicValues__openarray95slice_u126.p->data[2] = ((NI)30);
	dynamicValues__openarray95slice_u126.p->data[3] = ((NI)40);
	nimln_(25);	{
		NIM_BOOL T3_;
		NI T4_;
		T3_ = (NIM_BOOL)0;
		T4_ = (NI)0;
		T4_ = paramCount__stdZcmdline_u61();
		if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
		T3_ = (T4_ == ((NI)1));
		if (!(T3_)) goto LA5_;
		colontmpD_ = paramStr__stdZcmdline_u55(((NI)1));
		if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
		T3_ = eqStrings(colontmpD_, TM__30qzQsuGDD9b5bJwkidVyyw_3);
LA5_: ;
		if (!T3_) goto LA6_;
		nimln_(26);		if (((NI)4)-((NI)1) != -1 && (((NI)1) < 0 || ((NI)1) >= dynamicValues__openarray95slice_u126.len || ((NI)4) < 0 || ((NI)4) >= dynamicValues__openarray95slice_u126.len)){ raiseIndexError4(((NI)1), ((NI)4), dynamicValues__openarray95slice_u126.len); goto BeforeRet_;
		}
		if (((NI)1) < 0 || ((NI)1) >= dynamicValues__openarray95slice_u126.len){ raiseIndexError2(((NI)1),dynamicValues__openarray95slice_u126.len-1); goto BeforeRet_;
		}
		show__openarray95slice_u57(TM__30qzQsuGDD9b5bJwkidVyyw_16, (((dynamicValues__openarray95slice_u126).p) ? ((NI*)dynamicValues__openarray95slice_u126.p->data+(((NI)1))) : NIM_NIL), (((NI)4))-(((NI)1))+1, (&dynamicValues__openarray95slice_u126.p->data[((NI)1)]));
		if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
	}
	goto LA1_;
LA6_: ;
	{
		nimln_(28);		show__openarray95slice_u57(TM__30qzQsuGDD9b5bJwkidVyyw_18, fixedValues__openarray95slice_u121, 4, (&fixedValues__openarray95slice_u121[(((NI)0))- 0]));
		if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
		nimln_(29);		if (((NI)0) < 0 || ((NI)0) >= dynamicValues__openarray95slice_u126.len){ raiseIndexError2(((NI)0),dynamicValues__openarray95slice_u126.len-1); goto BeforeRet_;
		}
		show__openarray95slice_u57(TM__30qzQsuGDD9b5bJwkidVyyw_20, ((dynamicValues__openarray95slice_u126).p) ? (dynamicValues__openarray95slice_u126.p->data) : NIM_NIL, dynamicValues__openarray95slice_u126.len, (&dynamicValues__openarray95slice_u126.p->data[((NI)0)]));
		if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
		nimln_(30);		if (((NI)2)-((NI)1) != -1 && (((NI)1) < 0 || ((NI)1) >= dynamicValues__openarray95slice_u126.len || ((NI)2) < 0 || ((NI)2) >= dynamicValues__openarray95slice_u126.len)){ raiseIndexError4(((NI)1), ((NI)2), dynamicValues__openarray95slice_u126.len); goto BeforeRet_;
		}
		if (((NI)1) < 0 || ((NI)1) >= dynamicValues__openarray95slice_u126.len){ raiseIndexError2(((NI)1),dynamicValues__openarray95slice_u126.len-1); goto BeforeRet_;
		}
		show__openarray95slice_u57(TM__30qzQsuGDD9b5bJwkidVyyw_22, (((dynamicValues__openarray95slice_u126).p) ? ((NI*)dynamicValues__openarray95slice_u126.p->data+(((NI)1))) : NIM_NIL), (((NI)2))-(((NI)1))+1, (&dynamicValues__openarray95slice_u126.p->data[((NI)1)]));
		if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
	}
LA1_: ;
	nimlf_(394, "<NIM_ROOT>/lib/system.nim");	if (colontmpD_.p && !(colontmpD_.p->cap & NIM_STRLIT_FLAG)) {
 deallocShared(colontmpD_.p);
}
	nimlf_(23, "<EXPERIMENT>/src/openarray_slice.nim");	eqdestroy___openarray95slice_u159(dynamicValues__openarray95slice_u126);
	BeforeRet_: ;
	nimTestErrorFlag();
	popFrame();
}
}
