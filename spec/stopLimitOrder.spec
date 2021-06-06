/*
    This is a specification file for smart contract verification with the Certora prover.
    For more information, visit: https://www.certora.com/

    This file is run with scripts/...
	Assumptions:
*/

using SimpleOrderReceiver as receiver
using SimpleBentoBox as bentoBox


////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////


/*
    Declaration of methods that are used in the rules.
    envfree indicate that the method is not dependent on the environment (msg.value, msg.sender).
    Methods that are not declared here are assumed to be dependent on env.
*/


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
	oracleDataHarness() returns (uint) envfree
    amountToFillHarness() returns (uint256) envfree
	vHarness() returns (uint8) envfree
    rHarness() returns (bytes32) envfree
    sHarness() returns (bytes32) envfree

	setStopPrice(uint256) envfree
		
	bentoBalanceOf(address, address) returns (uint256) envfree
	cancelledOrder(address sender, bytes32 hash) returns (bool) envfree
	feeTo() returns (address) envfree
	feesCollected(address) returns (uint256) envfree
	externalOrderFee() returns (uint256) envfree
	FEE_DIVISOR() returns (uint256) envfree
	orderStatus(bytes32) returns (uint256) envfree


	getDigestHarness() envfree
	fillOrderHarness(bytes)
	fillOrderOpenHarness(bytes)
	batchFillOrderHarness(bytes)
	batchFillOrderOpenHarness(bytes)


	onLimitOrder(address tokenIn, address tokenOut, uint256 amountIn, uint256 amountMinOut, bytes data) => DISPATCHER(true)
	
	abstract_keccak256(address maker, address tokenIn, address tokenOut, uint256 amountIn, uint256 amountOut, address recipient, uint256 startTime, uint256 endTime, uint256 stopPrice, address oracleAddress) returns(bytes32) envfree => digestGhost(maker, tokenIn, tokenOut, amountIn, amountOut, recipient, startTime, endTime, stopPrice, oracleAddress)

	toAmount(address token, uint256 share, bool roundUp) returns (uint256) envfree => DISPATCHER(true)

	token1() returns (address) envfree => DISPATCHER(true)
	to1() returns (address) envfree => DISPATCHER(true)
	amount1() returns (uint256) envfree => DISPATCHER(true)
	
	token2() returns (address) envfree => DISPATCHER(true)
	to2() returns (address) envfree => DISPATCHER(true)
	amount2() returns (uint256) envfree => DISPATCHER(true)

	whiteListReceiver(address)
}


////////////////////////////////////////////////////////////////////////////
//                       Ghost                                            //
////////////////////////////////////////////////////////////////////////////

ghost digestGhost(address, address, address, uint256, uint256, address, uint256, uint256, uint256, address) returns bytes32;


////////////////////////////////////////////////////////////////////////////
//                       Invariants                                       //
////////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////////
//                       Rules                                            //
////////////////////////////////////////////////////////////////////////////



/* 	Rule: Integrity of Canceling the flag is on.  
 	Description: Performing a cancelOrder sets the cancelledOrder to true
	Formula: 
			{ digest = _getDigest(order{maker=u}, tIn, tOut) }
					cancelOrder(digest)
			{ cancelledOrder(u, digest) }	

	
*/
rule cancelTurnsOnFlag() {
	env e;
	require makerHarness() == e.msg.sender;
	bytes32 digest = getDigestHarness();
	cancelOrder(e, digest);
	assert cancelledOrder(e.msg.sender, digest);
}

/* 	Rule: Integrity of Canceling the flag is on.  
 	Description: if cancel flag is on, it will always remain on.
	Formula: 
			{ cancelledOrder(u, digest) }
					op
			{ cancelledOrder(u, digest) }	

	
*/
// part 2: 
rule afterCancelFails2() {
	bytes32 digest;
	address sender;
	require cancelledOrder(sender, digest);

	method f;
	env e;
	calldataarg args;
	f(e, args);

	assert cancelledOrder(sender, digest);
}
/*
// part 3: if cancel flag is on then fillOrder fails 
rule afterCancelFails3(method f) filtered { f -> 
	f.selector == fillOrderHarness(bytes).selector || 
	f.selector == fillOrderOpenHarness(bytes).selector || 
	f.selector ==  batchFillOrderHarness(bytes).selector || 
	f.selector == batchFillOrderOpenHarness(bytes).selector 
	} {
	address maker;	
	require makerHarness() == maker;
	bytes32 digest = getDigestHarness();

	require cancelledOrder(maker, digest);
	calldataarg args;
	env e;
	f(e, args);
	assert lastReverted;
}

*/
// Basically:
// recipient != bentoBox, because then onLoan can take coins from receipient instead of giving to it, because bentoBox can always be taken from.
// Also there are mastercontract stuff in the bentobox transfer which allow transfers - this still needs to be understood better.


function prepare(address recipient, address maker, address tokenIn, address tokenOut, uint256 amountIn, uint amountToFill, uint256 amountOut) {
	require receiverHarness() == receiver;

	require recipientHarness() == recipient;	
	require makerHarness() == maker;
	require tokenInHarness() == tokenIn;
	require tokenOutHarness() == tokenOut;
	require amountInHarness() == amountIn;
	require amountToFillHarness() == amountToFill;
	require amountOutHarness() == amountOut;
}



/****************************************************************************************************/

definition outOnly() returns uint = 1;
definition inOnly() returns uint = 2;
definition sameSame() returns uint = 3;

function fillOrderGeneralFunction(method f, uint type) {
	address recipient = 1; //todo no alias with
	address maker;
	address tokenIn;
	address tokenOut;
	uint256 amountIn;
	uint256 amountToFill;
	uint256 amountOut;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountToFill, amountOut);

	if (type == sameSame())
	 	require (maker == recipient) && (tokenIn == tokenOut);
	else
	 	require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));

	require amountIn != 0;
	uint256 expectedAmountOut = amountOut * amountToFill / amountIn;

	uint256 _bentoBalanceOut;
	uint256 _bentoBalanceIn;	
	uint256 bentoBalanceOut_;
	uint256 bentoBalanceIn_;
	
	if (type == sameSame() || type == outOnly())
		require _bentoBalanceOut == bentoBalanceOf(tokenOut, recipient);
	else 
		require _bentoBalanceIn == bentoBalanceOf(tokenIn, maker);	

	calldataarg args;
	env e;
	f(e, args);

	if (type == sameSame() || type == outOnly())
		require bentoBalanceOut_ == bentoBalanceOf(tokenOut, recipient);
	else 
		require bentoBalanceIn_ == bentoBalanceOf(tokenIn, maker);	


	if (type == sameSame() || type == outOnly()) {
		uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);
		uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);
		if (type == sameSame())
			// Actually this is probably incorrect if we change ratio from 1..
			assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + expectedAmountOut - amountToFill;
		else
			assert bentoBalanceOutCoins_ + 1 >= _bentoBalanceOutCoins + expectedAmountOut;
	} else 
		assert bentoBalanceIn_ >= _bentoBalanceIn - amountToFill;
}

/****************************************************************************************************/

/*
rule fillOrderOut(method f) filtered { f -> 
	f.selector == fillOrderHarness(bytes).selector  || 
	f.selector == fillOrderOpenHarness(bytes).selector || 
	f.selector ==  batchFillOrderHarness(bytes).selector || 
	f.selector == batchFillOrderOpenHarness(bytes).selector  
	} {
	require amountToFillHarness() == amountInHarness();
	fillOrderGeneralFunction(f, outOnly());
	assert(true);
}

rule fillOrderIn(method f) filtered { f -> 
	f.selector == fillOrderHarness(bytes).selector  || 
	f.selector == fillOrderOpenHarness(bytes).selector || 
	f.selector ==  batchFillOrderHarness(bytes).selector || 
	f.selector == batchFillOrderOpenHarness(bytes).selector  
	} {
	require amountToFillHarness() == amountInHarness();
	fillOrderGeneralFunction(f, inOnly());
	assert(true);
}

rule fillOrderSameSame(method f) filtered { f -> 
	f.selector == fillOrderHarness(bytes).selector  || 
	f.selector == fillOrderOpenHarness(bytes).selector || 
	f.selector ==  batchFillOrderHarness(bytes).selector || 
	f.selector == batchFillOrderOpenHarness(bytes).selector  
	} {
	require amountToFillHarness() == amountInHarness();
	fillOrderGeneralFunction(f, sameSame());
	assert(true);
}

*/
/****************************************************************************************************/




// Passes
rule fillOrderAmountToFillIn(method f) filtered { f -> 
	f.selector == fillOrderHarness(bytes).selector /* || 
	f.selector == fillOrderOpenHarness(bytes).selector || 
	f.selector ==  batchFillOrderHarness(bytes).selector || 
	f.selector == batchFillOrderOpenHarness(bytes).selector */ 
	} {
	fillOrderGeneralFunction(f, inOnly());
	assert(true);
}


rule fillOrderAmountToFillSameSame(method f) filtered { f -> 
	f.selector == fillOrderHarness(bytes).selector /* || 
	f.selector == fillOrderOpenHarness(bytes).selector || 
	f.selector ==  batchFillOrderHarness(bytes).selector || 
	f.selector == batchFillOrderOpenHarness(bytes).selector */ 
	} {
	fillOrderGeneralFunction(f, sameSame());
	assert(true);
}


/****************************************************************************************************/


// Checks fees are collected correctly.
// this one passes but is pretty heavy.
rule CheckFees(method f) filtered { f -> 
	f.selector == fillOrderOpenHarness(bytes).selector 
	// || f.selector == batchFillOrderOpenHarness(bytes).selector 
	} {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	uint256 amountIn;
	uint256 amountToFill = amountIn;	
	uint256 expectedFee;
	uint256 amountOut = 4 * expectedFee;

	require (maker == 2) || (maker == 1);
	require expectedFee < 10000000;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountToFill, amountOut);

	require externalOrderFee() == FEE_DIVISOR() / 4;

	uint256 _feesCollected = feesCollected(tokenOut);

	calldataarg args;
	env e;
	f(e, args);

	uint256 feesCollected_ = feesCollected(tokenOut);

	assert feesCollected_ >= _feesCollected + expectedFee;
}


// Checks that the contract indeed holds feesCollected tokens.
// invariant feesInvariant(address token) 
// 	bentoBalanceOf(token, currentContract) >= feesCollected(token)
// totally times out..

/*
// Should actually run this on all methods except the unharnessed versions of the fillOrder methods.
rule CheckFeesInvariant(method f)  filtered { f -> 
	f.selector == fillOrderOpenHarness(bytes).selector ||
	f.selector == swipeFees(address).selector   
	} {
	// otherwise the order takes away the fees to the receiver.
	require makerHarness() != currentContract;

	address token; 
	require bentoBalanceOf(token, currentContract) >= feesCollected(token);

	calldataarg args;
	env e;
	f(e, args);

	assert bentoBalanceOf(token, currentContract) >= feesCollected(token);
}


*/

/****************************************************************************************************/


// Doesn't work, and i don't get counter example.
/*rule fillOrderLiveness()  {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));

	uint256 amountIn;
	uint256 amountOut;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountIn, amountOut);

	require receiver.token1() == tokenOut;
	// require token2() == tokenOut;
	require receiver.amount1() == amountOut;
	require bentoBalanceOf(tokenOut, receiver) >= amountOut;
	// require amount2() == 0;

	env e1;
	whiteListReceiver(e1, receiver);
	bytes32 digest = getDigestHarness();

	require !cancelledOrder(makerHarness(), digest);

	env e;
	calldataarg args;
	require startTimeHarness() < e.block.number;
	require endTimeHarness() > e.block.number;
	require e.msg.value == 0;

    invoke_fallback(e, args);
    require !lastReverted;

    fillOrderHarness@withrevert(e, args);
    assert !lastReverted;
}

*/

/****************************************************************************************************/

/*
// See that if an order was partially filled, it cannot pass its amountIn.
rule checkOrderStatus() {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	uint256 amountOut;
	uint256 amountToFill;
	uint256 amountIn;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountToFill, amountOut);
	require maker == 1 || maker == 2;
	
	bytes32 digest = getDigestHarness();
	uint256 already = orderStatus(digest);

	require amountToFill + already > amountIn;

	// this should fail
	env e;
	calldataarg args;
    fillOrderHarness@withrevert(e, args);

	assert lastReverted;
}


*/


/*
// Should fail! indeed does.
rule digestSanity() {
	bytes32 digest1 = getDigestHarness();

	uint256 newStopPrice;
	setStopPrice(newStopPrice);

	bytes32 digest2 = getDigestHarness();
	
	assert digest1 == digest2;
}

// should pass. and it does.
rule digestSanity2() {
	bytes32 digest1 = getDigestHarness();

	bytes32 digest2 = getDigestHarness();
	
	assert digest1 == digest2;
}

*/


/****************************************************************************************************/

// Check Bug
// A livness rule should have been able to find this.
rule CheckBug() {
	address recipient = 1;
	address maker = 2;
	address tokenIn = 3;
	address tokenOut = 4;
	uint256 amountIn = 100;
	uint256 amountToFill = amountIn;	
	uint256 amountOut = 101;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountToFill, amountOut);
	require feesCollected(tokenOut) == 0;
	require bentoBalanceOf(tokenOut, currentContract) == 0;

	// CHANGED SIMPLELIMITORDERRECEIVER
	calldataarg args;
	env e;
	fillOrderHarness(e, args);

	assert(false);
	
} 

// I would also do a require in the code after onLimitOrder to see it doesn't take too much.
// especially for melicious ones.



// two orders stuff in batch..

// need a liveness version for everything: if conditions are good enough, nothing will fail..

// out of time order fails

// change ratio. <----------------- important 

// The batch are strange - even if one fails (because of stop or limit) they all fail.

// should think of what happens with malicious receiver - 
// basically we don't need to protect maker and reciever, but do need to protect everyone else, no?

// To be able to make the transfer in _preOrder, the maker approves transfers to the reciever, but this is unlimited... is that ok?
// This means that a malicious receiver can take more from the maker. But I am guessing that it is his problem.

// when ratio changes to 2 or more, should check the rounding, and especially that one does not pay more than he wanted, and does not get less than he wanted to get.

// Have to think about this keeping of 1 balance of currentContract. Can't it be taken away?

// have to check the rounding thing.. because only in one place the contract rounds up - in the require. So there may be a liveness problem.
// Quite sure this is a bug. - but that has to do with the real sushiswapLimitOrder which returns the exact number.
