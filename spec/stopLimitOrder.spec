
using DummyERC20A as tokenA
using DummyERC20B as tokenB
using SimpleOrderReceiver as receiver

methods {
	
	makerHarness() returns (address) envfree
	receiverHarness() returns (address) envfree
	tokenInHarness() returns (address) envfree
	tokenOutHarness() returns (address) envfree
	amountInHarness() returns (uint256) envfree
	amountOutHarness() returns (uint256) envfree
    recipientHarness() returns (address) envfree 
    startTimeHarness() returns (uint256) envfree
    endTimeHarness() returns (uint256) envfree
    stopPriceHarness() returns (uint256) envfree
    oracleAddressHarness() returns (address) envfree
	oracleDataHarness() returns (bytes) envfree
    amountToFillHarness() returns (uint256) envfree
	vHarness() returns (uint8) envfree
    rHarness() returns (bytes32) envfree
    sHarness() returns (bytes32) envfree



	// fillOrderHarness(address,uint256,uint256,address,uint256,uint256,uint256,address,bytes,uint256,uint8,bytes32,bytes32,bytes) => DISPATCHER(true)


	// swipeFees(IERC20 token) envfree
	// swipe (IERC20 token) envfree

    // setFees(address _feeTo, uint256 _externalOrderFee)
 	// whiteListReceiver(ILimitOrderReceiver receiver) 
	// cancelOrder(bytes32 hash)

	onLimitOrder(address tokenIn, address tokenOut, uint256 amountIn, uint256 amountMinOut, bytes data) => DISPATCHER(true)
}


definition MAX_UINT256() returns uint256 =
	0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
	

// rule sanity(method f) {
// 	env e;
// 	calldataarg args;
// 	f(e,args);
// 	assert false;
// }


// Should do a hook for abstract_keecack so it is uninterpreted.

// rule sanity1() {
// 	env e;
// 	calldataarg args;
// 	address account;
// 	require receiverHarness() == receiver;
// 	require tokenInHarness() == tokenA;
// 	require tokenOutHarness() == tokenB;

// 	require amountInHarness() == 100;
// 	require amountOutHarness() == 200;
// 	require recipientHarness() == account;
//     // uint256 public startTimeHarness;
//     // uint256 public endTimeHarness;
//     require oracleAddressHarness() == 0;
// 	require amountToFillHarness() == 50;
	
// 	sinvoke fillOrderHarness(e, args);
// 	assert false;
// }

rule afterCancelFails() {
	env e;
	calldataarg args;
	calldataarg args2;
	
	require receiverHarness() == receiver;
    require oracleAddressHarness() == 0;
	
	bytes32 digest = getDigestHarness(e, args);
	sinvoke cancelOrder(e, digest);
	fillOrderHarness(e, args2);
	assert lastReverted;
}
