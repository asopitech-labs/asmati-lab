/* Nim 2.2.10 failed-cast generated C and runtime helper. */

N_LIB_PRIVATE N_NOINLINE(NI, forceDog__object95type95cast_u176)(tyObject_AnimalcolonObjectType___q6grIfCmUkcnq9bcDHhp4AA* animal_p0);

N_LIB_PRIVATE N_NOINLINE(NI, forceDog__object95type95cast_u176)(tyObject_AnimalcolonObjectType___q6grIfCmUkcnq9bcDHhp4AA* animal_p0) {
	NI result;
	nimfr_("forceDog", "<EXPERIMENT>/src/object_type_cast.nim");
{	nimln_(18);	if (animal_p0 && !isObjDisplayCheck((*animal_p0).Sup.m_type, 2, 989327872)){ raiseObjectConversionError(); goto BeforeRet_;
	}
	result = (*((tyObject_DogcolonObjectType___TDr38nP9afD6AlAK1hco8hA*) (animal_p0))).barkVolume;
	}BeforeRet_: ;
	popFrame();
	return result;
}

N_LIB_PRIVATE N_NOINLINE(void, raiseObjectConversionError)(void) {
	sysFatal__system_u4908(TM__Q5wkpxktOdTGvlSRo9bzt9aw_139);
}
