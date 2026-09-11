/* Nim 2.2.10 normal generated C. Selected type metadata and checks. */

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
struct tyObject_AnimalcolonObjectType___q6grIfCmUkcnq9bcDHhp4AA {
	RootObj Sup;
	NI id;
};
struct tyObject_DogcolonObjectType___TDr38nP9afD6AlAK1hco8hA {
	tyObject_AnimalcolonObjectType___q6grIfCmUkcnq9bcDHhp4AA Sup;
	NI barkVolume;
};
struct tyObject_CatcolonObjectType___ib559bpRcMUD85klcZ0tdDw {
	tyObject_AnimalcolonObjectType___q6grIfCmUkcnq9bcDHhp4AA Sup;
	NI lives;
};

static NIM_CONST NU32 TM__PpFyGYkjOX7Qiad9bt0OZdA_2[3] = {3701606400, 2821398784, 989327872};
N_LIB_PRIVATE TNimTypeV2 NTIv2__TDr38nP9afD6AlAK1hco8hA_ = {.destructor = (void*)NIM_NIL, .size = sizeof(tyObject_DogcolonObjectType___TDr38nP9afD6AlAK1hco8hA), .align = (NI16) NIM_ALIGNOF(tyObject_DogcolonObjectType___TDr38nP9afD6AlAK1hco8hA), .depth = 2, .display = TM__PpFyGYkjOX7Qiad9bt0OZdA_2, .traceImpl = (void*)NIM_NIL, .flags = 0};
static NIM_CONST NU32 TM__PpFyGYkjOX7Qiad9bt0OZdA_3[3] = {3701606400, 2821398784, 3195664896};
N_LIB_PRIVATE TNimTypeV2 NTIv2__ib559bpRcMUD85klcZ0tdDw_ = {.destructor = (void*)NIM_NIL, .size = sizeof(tyObject_CatcolonObjectType___ib559bpRcMUD85klcZ0tdDw), .align = (NI16) NIM_ALIGNOF(tyObject_CatcolonObjectType___ib559bpRcMUD85klcZ0tdDw), .depth = 2, .display = TM__PpFyGYkjOX7Qiad9bt0OZdA_3, .traceImpl = (void*)NIM_NIL, .flags = 0};

T2_ = (tyObject_DogcolonObjectType___TDr38nP9afD6AlAK1hco8hA*) nimNewObjUninit(sizeof(tyObject_DogcolonObjectType___TDr38nP9afD6AlAK1hco8hA), NIM_ALIGNOF(tyObject_DogcolonObjectType___TDr38nP9afD6AlAK1hco8hA));
	(*T2_).Sup.Sup.m_type = (&NTIv2__TDr38nP9afD6AlAK1hco8hA_);
	(*T2_).Sup.id = ((NI)1);
	(*T2_).barkVolume = ((NI)7);
	dog__object95type95cast_u179 = &T2_->Sup;
T3_ = (tyObject_CatcolonObjectType___ib559bpRcMUD85klcZ0tdDw*) nimNewObjUninit(sizeof(tyObject_CatcolonObjectType___ib559bpRcMUD85klcZ0tdDw), NIM_ALIGNOF(tyObject_CatcolonObjectType___ib559bpRcMUD85klcZ0tdDw));
	(*T3_).Sup.Sup.m_type = (&NTIv2__ib559bpRcMUD85klcZ0tdDw_);
	(*T3_).Sup.id = ((NI)2);
	(*T3_).lives = ((NI)9);
	cat__object95type95cast_u180 = &T3_->Sup;

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

N_LIB_PRIVATE N_NOINLINE(NI, identify__object95type95cast_u10)(tyObject_AnimalcolonObjectType___q6grIfCmUkcnq9bcDHhp4AA* animal_p0);

N_LIB_PRIVATE N_NOINLINE(NI, identify__object95type95cast_u10)(tyObject_AnimalcolonObjectType___q6grIfCmUkcnq9bcDHhp4AA* animal_p0) {
	NI result;
	NI T1_;
	nimfr_("identify", "<EXPERIMENT>/src/object_type_cast.nim");
{	result = (NI)0;
	T1_ = (NI)0;
	nimlf_(10, "<EXPERIMENT>/src/object_type_cast.nim");	{
		if (!((animal_p0) && (isObjDisplayCheck((*animal_p0).Sup.m_type, 2, 989327872)))) goto LA4_;
		nimln_(9);		nimln_(11);		if (animal_p0 && !isObjDisplayCheck((*animal_p0).Sup.m_type, 2, 989327872)){ raiseObjectConversionError(); goto BeforeRet_;
		}
		result = (*((tyObject_DogcolonObjectType___TDr38nP9afD6AlAK1hco8hA*) (animal_p0))).barkVolume;
	}
	goto LA2_;
LA4_: ;
	{
		nimln_(12);		if (!((animal_p0) && (isObjDisplayCheck((*animal_p0).Sup.m_type, 2, 3195664896)))) goto LA7_;
		nimln_(9);		nimln_(13);		if (animal_p0 && !isObjDisplayCheck((*animal_p0).Sup.m_type, 2, 3195664896)){ raiseObjectConversionError(); goto BeforeRet_;
		}
		if ((*((tyObject_CatcolonObjectType___ib559bpRcMUD85klcZ0tdDw*) (animal_p0))).lives == (IL64(-9223372036854775807) - IL64(1))){ raiseOverflow(); goto BeforeRet_;
		}
		result = ((NI64)-((*((tyObject_CatcolonObjectType___ib559bpRcMUD85klcZ0tdDw*) (animal_p0))).lives));
	}
	goto LA2_;
LA7_: ;
	{
		nimln_(9);		nimln_(15);		result = ((NI)0);
	}
LA2_: ;
	}BeforeRet_: ;
	popFrame();
	return result;
}
