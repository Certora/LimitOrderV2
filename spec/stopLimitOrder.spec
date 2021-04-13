
using DummyERC20A as tokenA
using DummyERC20B as tokenB
using SimpleOrderReceiver as receiver

methods {
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
//    oracleDataHarness() returns (bytes) envfree
    amountToFillHarness() returns (uint256) envfree
	vHarness() returns (uint8) envfree
    rHarness() returns (bytes32) envfree
    sHarness() returns (bytes32) envfree

	fillOrderHarness(address,uint256,uint256,address,uint256,uint256,uint256,address,bytes,uint256,uint8,bytes32,bytes32,bytes) envfree


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

rule sanity1() {
	env e;
	calldataarg args;
	require receiverHarness() == receiver;
	require tokenInHarness() == tokenA;
	require tokenOutHarness() == tokenB;

	require amountInHarness() == 100;
	require amountOutHarness() == 200;
	require recipientHarness() == this // I want StopLimitOrderHarness's address here; 
    // uint256 public startTimeHarness;
    // uint256 public endTimeHarness;
    require oracleAddressHarness() == 0;
	require amountToFillHarness() == 50;
	
	sinvoke fillOrderHarness(args);
	assert false;
}
