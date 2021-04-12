

methods {
	
}


definition MAX_UINT256() returns uint256 =
	0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
	

rule sanity(method f) {
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}