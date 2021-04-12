
using DummyERC20A as tokenA
using DummyERC20B as tokenB
using SimpleOrderReceiver as receiver 

methods {
	// removed memory and calldata modifiers in the next signature. ok?
	// fillOrderHarness(OrderArgs order, IERC20 tokenIn, IERC20 tokenOut, ILimitOrderReceiver receiver) envfree 
	// swipeFees(IERC20 token) envfree
	// swipe (IERC20 token) envfree

    // setFees(address _feeTo, uint256 _externalOrderFee)
 	// whiteListReceiver(ILimitOrderReceiver receiver) 
	// cancelOrder(bytes32 hash)
}


definition MAX_UINT256() returns uint256 =
	0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
	

// rule sanity(method f) {
// 	env e;
// 	calldataarg args;
// 	f(e,args);
// 	assert false;
// }

rule sanity1() {
	env e;
	calldataarg args;
	fillOrder(e, args);
	assert false;
}
