/*
    This is a specification file for smart contract verification
    with the Certora prover. For more information,
	visit: https://www.certora.com/

    This file is run with scripts/...
	Assumptions:
*/

using SimpleOrderReceiver as receiver
using SimpleBentoBox as bentoBox

////////////////////////////////////////////////////////////////////////////
//                                Methods                                 //
////////////////////////////////////////////////////////////////////////////
/*
    Declaration of methods that are used in the rules.
    envfree indicate that the method is not dependent on the environment (msg.value, msg.sender).
    Methods that are not declared here are assumed to be dependent on env.
*/

methods {	
	// global variables used to construct an order structure
	makerHarness() returns (address) envfree
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

	receiverHarness() returns (address) envfree
	tokenInHarness() returns (address) envfree
	tokenOutHarness() returns (address) envfree

	// signatures
	fillOrder((address, uint256, uint256, address, uint256, uint256, uint256, address,
	  		   uint256, uint256, uint8, bytes32, bytes32), address, address, address, bytes)
	fillOrderOpen((address, uint256, uint256, address, uint256, uint256, uint256, address,
	  			   uint256, uint256, uint8, bytes32, bytes32), address, address, address, bytes)
	batchFillOrder((address, uint256, uint256, address, uint256, uint256, uint256, address,
	  				uint256, uint256, uint8, bytes32, bytes32)[], address, address, address, bytes)
  	batchFillOrderOpen((address, uint256, uint256, address, uint256, uint256, uint256,
	  					address, uint256, uint256, uint8, bytes32, bytes32)[], address,
						address, address, bytes)
	cancelOrder(bytes32)
	whiteListReceiver(address)
	permitToken(address, address, address, uint256, uint256, uint8, bytes32, bytes32)
	setFees(address, uint256)
	setStopPrice(uint256)
	swipe(address)
	swipeFees(address)
	transferOwnership(address, bool, bool)
	claimOwnership()
	batch(bytes[], bool)

	// simplifications to code
	abstract_keccak256(address maker, address tokenIn, address tokenOut,
					   uint256 amountIn, uint256 amountOut, address recipient,
					   uint256 startTime, uint256 endTime, uint256 stopPrice, 
					   address oracleAddress, uint256 oracleData)
		returns(bytes32) envfree => digestGhost(maker, tokenIn, tokenOut,
											    amountIn, amountOut, recipient, 
												startTime, endTime, stopPrice, 
												oracleAddress, oracleData)
	computeAmountOut(uint256 amountIn, uint256 amountOut, uint256 amountToBeFilled)
							returns (uint256) => DISPATCHER(true)
	ec_recover(bytes32 digest, uint8 v, bytes32 r, bytes32 s) 
						returns (address) => DISPATCHER(true)

	// getters 	
	bentoBalanceOf(address, address) returns (uint256) envfree
	cancelledOrder(address sender, bytes32 hash) returns (bool) envfree
	feeTo() returns (address) envfree
	feesCollected(address) returns (uint256) envfree
	externalOrderFee() returns (uint256) envfree
	FEE_DIVISOR() returns (uint256) envfree
	orderStatus(bytes32) returns (uint256) envfree

	// receiver
	onLimitOrder(address tokenIn, address tokenOut, uint256 amountIn,
			     uint256 amountMinOut, bytes data) => DISPATCHER(true)

	// bentobox	
	toAmount(address token, uint256 share, bool roundUp)
		returns (uint256) envfree => DISPATCHER(true)

	// oracle
	get(uint) returns (bool, uint256) => NONDET
}

////////////////////////////////////////////////////////////////////////////
//                                 Ghost                                  //
////////////////////////////////////////////////////////////////////////////
ghost digestGhost(address, address, address, uint256, uint256, address, uint256, 
				uint256, uint256, address, uint256) returns bytes32;

////////////////////////////////////////////////////////////////////////////
//                               Invariants                               //
////////////////////////////////////////////////////////////////////////////
// Both are same, we need to check which one works
// Checks that the contract indeed holds feesCollected tokens.
// invariant feesInvariant(address token) 
// 	bentoBalanceOf(token, currentContract) >= feesCollected(token)
// totally times out..

// Should actually run this on all methods except the unharnessed versions of the fillOrder methods.
rule CheckFeesInvariant(method f) filtered { f -> 
	f.selector == fillOrderOpen((address, uint256, uint256, address, uint256, uint256, uint256,
								     address, uint256, uint256, uint8, bytes32, bytes32), address, 
									 address, address, bytes).selector ||
	f.selector == swipeFees(address).selector } {
	// otherwise the order takes away the fees to the receiver.
	require makerHarness() != currentContract;

	address token; 
	require bentoBalanceOf(token, currentContract) >= feesCollected(token);

	calldataarg args;
	env e;
	f(e, args);

	assert bentoBalanceOf(token, currentContract) >= feesCollected(token);
}

////////////////////////////////////////////////////////////////////////////
//                                 Rules                                  //
////////////////////////////////////////////////////////////////////////////
/*	
	Rule: Integrity of Canceling the flag is on.  
 	Description: Performing a cancelOrder sets the cancelledOrder to true
	Formula: 
			{ digest = _getDigest(order{maker=u}, tIn, tOut) }
					cancelOrder(digest)
			{ cancelledOrder(u, digest) }
*/
rule cancelTurnsOnFlag() {
	env e;

	require makerHarness() == e.msg.sender;

	calldataarg digestArgs;
	bytes32 digest = getDigest(e, digestArgs);
	cancelOrder(e, digest);

	assert cancelledOrder(e.msg.sender, digest);
}

/*
 	Rule: Always cancelled.  
 	Description: if cancel flag is on, it will always remain on.
	Formula: 
			{ cancelledOrder(u, digest) }
					op
			{ cancelledOrder(u, digest) }
*/
rule onceCancelledAlways() {
	method f;
	env e;
	bytes32 digest;
	address sender;

	require cancelledOrder(sender, digest);
	
	calldataarg args;
	f(e, args);

	assert cancelledOrder(sender, digest);
}

/*	
	Rule: A cancelled order can not be filled.  
 	Description: any of the fill order function reverts when the order is cancelled 
	Formula: 
			{ cancelledOrder(u, digest) }
					r = op
			{ false }
			where op is any of the fillOrder operation returns false if failed
*/
rule cancelledCannotBeFilled(method f) {
		env e;
		address maker;

		calldataarg digestArgs;
		bytes32 digest = getDigest(e, digestArgs);

		require makerHarness() == maker;
		require cancelledOrder(maker, digest);

		calldataarg args;
		f(e, args);

		assert lastReverted;
	}

/* 	
	Rule: Fill order is up to the amountIn
 	Description: The total filled amount of an order is never more than the amountIn
	Formula: 
			orderStatus(digest(order)) <= order.amountIn		
*/
rule orderStatusLeAmountToFill(method f) {
		env e;

		address maker;
		address recipient; 
		address tokenIn;
		address tokenOut;
		uint256 amountIn;
		uint256 amountToFill;
		uint256 amountOut;
		prepare(maker, amountIn, amountOut, recipient, amountToFill, tokenIn, tokenOut);

		calldataarg digestArgs;
		bytes32 digest = getDigest(e, digestArgs);

		uint256 orderStatusBefore = orderStatus(digest);

		require orderStatusBefore <= amountInHarness();

		calldataarg args;
		f(e, args);

		uint256 orderStatusAfter = orderStatus(digest);
		
		assert orderStatusAfter <= amountInHarness();
	}

// Checks fees are collected correctly.
// this one passes but is pretty heavy.
rule CheckFees(method f) filtered { f -> 
		f.selector == fillOrderOpen((address, uint256, uint256, address, uint256, uint256, uint256,
								     address, uint256, uint256, uint8, bytes32, bytes32), address, 
									 address, address, bytes).selector /*|| 
		f.selector == batchFillOrderOpen((address, uint256, uint256, address, uint256, uint256, uint256,
	  					address, uint256, uint256, uint8, bytes32, bytes32)[], address,
						address, address, bytes)*/ } {
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
	prepare(maker, amountIn, amountOut, recipient, amountToFill, tokenIn, tokenOut);

	require externalOrderFee() == FEE_DIVISOR() / 4;

	uint256 _feesCollected = feesCollected(tokenOut);

	calldataarg args;
	env e;
	f(e, args);

	uint256 feesCollected_ = feesCollected(tokenOut);

	assert feesCollected_ >= _feesCollected + expectedFee;
}

// work on this to write it properly and make it pass
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
	prepare(maker, amountIn, amountOut, recipient, amountToFill, tokenIn, tokenOut);
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

////////////////////////////////////////////////////////////////////////////
//                            Helper Functions                            //
////////////////////////////////////////////////////////////////////////////
// Change the order of params
// Basically:
// recipient != bentoBox, because then onLoan can take coins from receipient instead of giving to it, because bentoBox can always be taken from.
// Also there are mastercontract stuff in the bentobox transfer which allow transfers - this still needs to be understood better.
function prepare(address maker, uint256 amountIn, uint256 amountOut,
				 address recipient, uint256 amountToFill, address tokenIn, address tokenOut) {
	require makerHarness() == maker;
	require amountInHarness() == amountIn;
	require amountOutHarness() == amountOut;
	require recipientHarness() == recipient;
	require amountToFillHarness() == amountToFill;

	require receiverHarness() == receiver;
	require tokenInHarness() == tokenIn;
	require tokenOutHarness() == tokenOut;
}

////////////////////////////////////////////////////////////////////////////
//                                Temporary                               //
////////////////////////////////////////////////////////////////////////////
definition outOnly() returns uint = 1;
definition inOnly() returns uint = 2;
definition sameSame() returns uint = 3;

rule fillOrderGeneralFunction(method f, uint type) filtered { f -> 
		f.selector == fillOrder((address, uint256, uint256, address, uint256, uint256, uint256,
		 						 address, uint256, uint256, uint8, bytes32, bytes32), address, address,
								 address, bytes).selector /*||
		f.selector == fillOrderOpen((address, uint256, uint256, address, uint256, uint256, uint256,
								     address, uint256, uint256, uint8, bytes32, bytes32), address, 
									 address, address, bytes).selector*/ } {
	address recipient = 1; //todo no alias with
	address maker;
	address tokenIn;
	address tokenOut;
	uint256 amountIn;
	uint256 amountToFill;
	uint256 amountOut;
	prepare(maker, amountIn, amountOut, recipient, amountToFill, tokenIn, tokenOut);
	require tokenIn != tokenOut;
	require maker != recipient;
	require maker != currentContract;
/*	if (type == sameSame())
		require (maker == recipient) && (tokenIn == tokenOut);
	else
		require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));
*/
	require amountIn != 0;
	uint256 expectedAmountOut = amountOut * amountToFill / amountIn;

	uint256 _bentoBalanceOut;
	uint256 _bentoBalanceIn;	
	uint256 bentoBalanceOut_;
	uint256 bentoBalanceIn_;
	
	//if (type == sameSame() || type == outOnly())
		require _bentoBalanceOut == bentoBalanceOf(tokenOut, recipient);
	//else 
		require _bentoBalanceIn == bentoBalanceOf(tokenIn, maker);	

	calldataarg args;
	env e;
	f(e, args);

//	if (type == sameSame() || type == outOnly())
		require bentoBalanceOut_ == bentoBalanceOf(tokenOut, recipient);
//	else 
		require bentoBalanceIn_ == bentoBalanceOf(tokenIn, maker);	


//	if (type == sameSame() || type == outOnly()) {
		uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);
		uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);
//		if (type == sameSame())
			// Actually this is probably incorrect if we change ratio from 1..
	//		assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + expectedAmountOut - amountToFill;
	//	else
			assert bentoBalanceOutCoins_ + 1 >= _bentoBalanceOutCoins + expectedAmountOut;
	//} else 
		assert bentoBalanceIn_ >= _bentoBalanceIn - amountToFill;
}

// Doesn't work, and i don't get counter example.
/*
rule fillOrderLiveness()  {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));

	uint256 amountIn;
	uint256 amountOut;
	prepare(maker, amountIn, amountOut, recipient, amountToFill, tokenIn, tokenOut);

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

/*
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
	prepare(maker, amountIn, amountOut, recipient, amountToFill, tokenIn, tokenOut);
	require feesCollected(tokenOut) == 0;
	require bentoBalanceOf(tokenOut, currentContract) == 0;

	// CHANGED SIMPLELIMITORDERRECEIVER
	calldataarg args;
	env e;
	fillOrderHarness(e, args);

	assert(false);
}
*/

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