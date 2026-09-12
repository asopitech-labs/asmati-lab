/* Nim 2.2.10 generated C. Selected static and dynamic dispatch evidence. */

struct TNimTypeV2 {
	void* destructor;
	NI size;
	NI16 align;
	NI16 depth;
	NU32* display;
	void* traceImpl;
	void* typeInfoV1;
	NI flags;
	void* vTable[SEQ_DECL_SIZE];
};
struct RootObj {
	TNimTypeV2* m_type;
};
struct tyObject_AnimalcolonObjectType___C0R13XiArqqkH1YL9c5hpew {
	RootObj Sup;
	NI id;
};
struct tyObject_DogcolonObjectType___TV3eoUJ9cS4B8yq9b9aE3YRkQ {
	tyObject_AnimalcolonObjectType___C0R13XiArqqkH1YL9c5hpew Sup;
	NI bonus;
};

N_LIB_PRIVATE TNimTypeV2 NTIv2__TV3eoUJ9cS4B8yq9b9aE3YRkQ_ = {.destructor = (void*)NIM_NIL, .size = sizeof(tyObject_DogcolonObjectType___TV3eoUJ9cS4B8yq9b9aE3YRkQ), .align = (NI16) NIM_ALIGNOF(tyObject_DogcolonObjectType___TV3eoUJ9cS4B8yq9b9aE3YRkQ), .depth = 2, .display = TM__AYJYrT4q0PSYqpR85Tqj4A_4, .traceImpl = (void*)NIM_NIL, .flags = 0};

static N_INLINE(NIM_BOOL, isObjDisplayCheck)(TNimTypeV2* source_p0, NI16 targetDepth_p1, NU32 token_p2) {
	NIM_BOOL result;
	NIM_BOOL T1_;
	nimfr_("isObjDisplayCheck", "<NIM_ROOT>/lib/system/arc.nim");
	nimlf_(288, "<NIM_ROOT>/lib/system/arc.nim");	T1_ = (NIM_BOOL)0;
	T1_ = (targetDepth_p1 <= (*source_p0).depth);
	if (!(T1_)) goto LA2_;
	T1_ = ((*source_p0).display[targetDepth_p1] == token_p2);
LA2_: ;
	result = T1_;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NOINLINE(NI, staticScore__static95dynamic95dispatch_u7)(tyObject_AnimalcolonObjectType___C0R13XiArqqkH1YL9c5hpew* animal_p0) {
	NI result;
	NI TM__AYJYrT4q0PSYqpR85Tqj4A_7;
	nimfr_("staticScore", "<EXPERIMENT>/src/static_dynamic_dispatch.nim");
{	result = (NI)0;
	nimln_(8);	if (nimAddInt((*animal_p0).id, ((NI)100), &TM__AYJYrT4q0PSYqpR85Tqj4A_7)) { raiseOverflow(); goto BeforeRet_;
	};
	result = (NI)(TM__AYJYrT4q0PSYqpR85Tqj4A_7);
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NOINLINE(NI, dynamicScore__static95dynamic95dispatch_u10)(tyObject_AnimalcolonObjectType___C0R13XiArqqkH1YL9c5hpew* animal_p0) {
	NI result;
	NI TM__AYJYrT4q0PSYqpR85Tqj4A_2;
	nimfr_("dynamicScore", "<EXPERIMENT>/src/static_dynamic_dispatch.nim");
{	result = (NI)0;
	nimlf_(11, "<EXPERIMENT>/src/static_dynamic_dispatch.nim");	if (nimAddInt((*animal_p0).id, ((NI)100), &TM__AYJYrT4q0PSYqpR85Tqj4A_2)) { raiseOverflow(); goto BeforeRet_;
	};
	result = (NI)(TM__AYJYrT4q0PSYqpR85Tqj4A_2);
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NOINLINE(NI, dynamicScore__static95dynamic95dispatch_u15)(tyObject_DogcolonObjectType___TV3eoUJ9cS4B8yq9b9aE3YRkQ* dog_p0) {
	NI result;
	NI TM__AYJYrT4q0PSYqpR85Tqj4A_3;
	nimfr_("dynamicScore", "<EXPERIMENT>/src/static_dynamic_dispatch.nim");
{	result = (NI)0;
	nimln_(14);	if (nimAddInt((*dog_p0).Sup.id, (*dog_p0).bonus, &TM__AYJYrT4q0PSYqpR85Tqj4A_3)) { raiseOverflow(); goto BeforeRet_;
	};
	result = (NI)(TM__AYJYrT4q0PSYqpR85Tqj4A_3);
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NOINLINE(NI, callStatic__static95dynamic95dispatch_u18)(tyObject_AnimalcolonObjectType___C0R13XiArqqkH1YL9c5hpew* animal_p0) {
	NI result;
NIM_BOOL* nimErr_;
	nimfr_("callStatic", "<EXPERIMENT>/src/static_dynamic_dispatch.nim");
{nimErr_ = nimErrorFlag();
	result = (NI)0;
	nimln_(17);	result = staticScore__static95dynamic95dispatch_u7(animal_p0);
	if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NOINLINE(NI, callDynamic__static95dynamic95dispatch_u21)(tyObject_AnimalcolonObjectType___C0R13XiArqqkH1YL9c5hpew* animal_p0) {
	NI result;
NIM_BOOL* nimErr_;
	nimfr_("callDynamic", "<EXPERIMENT>/src/static_dynamic_dispatch.nim");
{nimErr_ = nimErrorFlag();
	result = (NI)0;
	nimln_(20);	result = dynamicScore__static95dynamic95dispatch_u13(animal_p0);
	if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NOINLINE(NI, dynamicScore__static95dynamic95dispatch_u13)(tyObject_AnimalcolonObjectType___C0R13XiArqqkH1YL9c5hpew* animal_p0) {
	NI result;
NIM_BOOL* nimErr_;
	nimfr_("dynamicScore", "<EXPERIMENT>/src/static_dynamic_dispatch.nim");
{nimErr_ = nimErrorFlag();
	result = (NI)0;
	nimlf_(114, "<NIM_ROOT>/lib/system/chcks.nim");	chckNilDisp(animal_p0);
	nimlf_(10, "<EXPERIMENT>/src/static_dynamic_dispatch.nim");	{
		if (!((animal_p0) && (isObjDisplayCheck((*animal_p0).Sup.m_type, 2, 1574871296)))) goto LA3_;
		if (animal_p0 && !isObjDisplayCheck((*animal_p0).Sup.m_type, 2, 1574871296)){ raiseObjectConversionError(); goto BeforeRet_;
		}
		result = dynamicScore__static95dynamic95dispatch_u15(((tyObject_DogcolonObjectType___TV3eoUJ9cS4B8yq9b9aE3YRkQ*) (animal_p0)));
		if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
		goto BeforeRet_;
	}
	goto LA1_;
LA3_: ;
	{
		if (!((animal_p0) && (isObjDisplayCheck((*animal_p0).Sup.m_type, 1, 1148574976)))) goto LA6_;
		result = dynamicScore__static95dynamic95dispatch_u10(animal_p0);
		if (NIM_UNLIKELY(*nimErr_)) goto BeforeRet_;
		goto BeforeRet_;
	}
	goto LA1_;
LA6_: ;
LA1_: ;
	}BeforeRet_: ;
	popFrame();
	return result;
}
