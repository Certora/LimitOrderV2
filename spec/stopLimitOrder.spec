
// using DummyERC20A as tokenA
// using DummyERC20B as tokenB
using SimpleOrderReceiver as receiver
using SimpleBentoBox as bentoBox

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

	setStopPrice(uint256)
	
	thisAddress() returns (address) envfree
	
	bentoBalanceOf(address, address) returns (uint256) envfree
	cancelledOrder(address sender, bytes32 hash) returns (bool) envfree
	feeTo() returns (address) envfree
	feesCollected(address) returns (uint256) envfree
	externalOrderFee() returns (uint256) envfree
	FEE_DIVISOR() returns (uint256) envfree


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

ghost digestGhost(address, address, address, uint256, uint256, address, uint256, uint256, uint256, address) returns bytes32; // are there rules that require that this is one-to-one?

definition MAX_UINT256() returns uint256 =
	0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
	


// part 1: after a cancel, the flag is on.
rule afterCancelFails1() {
	env e;
	require makerHarness() == e.msg.sender;
	bytes32 digest = getDigestHarness();
	cancelOrder(e, digest);
	assert cancelledOrder(e.msg.sender, digest);
}

// part 2: if cancel flag is on, it will always remain on.
rule afterCancelFails2() {
	bytes32 digest;
	address sender;
	require cancelledOrder(sender, digest);

	method f;
	env e;
	calldataarg args;
	sinvoke f(e, args);

	assert cancelledOrder(sender, digest);
}

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


// Checks fillOrder methods result in tokenOut balance increasing at least as much as it should, and that tokenIn balance does not decrease too much.
rule basicFillOrder(method f) filtered {f -> 
	f.selector == fillOrderHarness(bytes).selector /* || 
	f.selector == fillOrderOpenHarness(bytes).selector || 
	f.selector ==  batchFillOrderHarness(bytes).selector || 
	f.selector == batchFillOrderOpenHarness(bytes).selector */ 
	} {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));
	uint256 amountIn;
	uint256 amountOut;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountIn, amountOut);

	uint256 _bentoBalanceIn = bentoBalanceOf(tokenIn, maker);	
	uint256 _bentoBalanceOut = bentoBalanceOf(tokenOut, recipient);
	uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);

	calldataarg args;
	env e;
	f(e, args);

	uint256 bentoBalanceIn_ = bentoBalanceOf(tokenIn, maker);
	uint256 bentoBalanceOut_ = bentoBalanceOf(tokenOut, recipient);
	uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);

	// at least amountOut coins were added to recipient. 
	assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + amountOut;
	// no more than amountIn tokens were taken from maker.
	assert bentoBalanceIn_ + amountIn >= _bentoBalanceIn;
}


// Just for experiments..
rule basicFillOrderSimple(method f) filtered {f -> 
	f.selector == fillOrderHarness(bytes).selector /* || 
	f.selector == fillOrderOpenHarness(bytes).selector || 
	f.selector ==  batchFillOrderHarness(bytes).selector || 
	f.selector == batchFillOrderOpenHarness(bytes).selector */ 
	} {
	address recipient;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker != recipient) || ((maker == recipient) && (tokenIn != tokenOut));
	uint256 amountIn;
	uint256 amountOut;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountIn, amountOut);
	require recipient != bentoBox;
	require maker != bentoBox;
	require recipient != receiver;
	require maker != receiver;

//	uint256 _bentoBalanceIn = bentoBalanceOf(tokenIn, maker);
	uint256 _bentoBalanceOut = bentoBalanceOf(tokenOut, recipient);
	uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);

	calldataarg args;
	env e;
	f(e, args);

//	uint256 bentoBalanceIn_ = bentoBalanceOf(tokenIn, maker);
	uint256 bentoBalanceOut_ = bentoBalanceOf(tokenOut, recipient);
	uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);

	// at least amountOut coins were added to recipient. 
	assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + amountOut;
	// no more than amountIn tokens were taken from maker.
	//	assert bentoBalanceIn_ + amountIn >= _bentoBalanceIn;
}


rule basicFillOrderSameSame(method f) filtered {f -> 
	f.selector == fillOrderHarness(bytes).selector || 
	f.selector == fillOrderOpenHarness(bytes).selector || 
	f.selector ==  batchFillOrderHarness(bytes).selector || 
	f.selector == batchFillOrderOpenHarness(bytes).selector 
	}{
	address recipientAndMaker = 1;
	address token = 2;

	uint256 amountIn;
	uint256 amountOut;
	prepare(recipientAndMaker, recipientAndMaker, token, token, amountIn, amountIn, amountOut);

	uint256 _bentoBalance = bentoBalanceOf(token, recipientAndMaker);
	uint256 _bentoBalanceCoins = bentoBox.toAmount(token, _bentoBalance, false);

	calldataarg args;
	env e;
	f(e, args);

	uint256 bentoBalance_ = bentoBalanceOf(token, recipientAndMaker);
	uint256 bentoBalanceCoins_ = bentoBox.toAmount(token, bentoBalance_, false);

	// after >= before - in +  out
	assert bentoBalanceCoins_ + amountIn >= _bentoBalanceCoins + amountOut;
}

// same as basicFillOrder, when AmountToFill is 1/4 of AmountIn 
// but flag
function fillOrderWithAmountInFunction(bool outFlag, method f) 
{
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));
	uint256 amountToFill;
	uint256 amountIn = amountToFill * 4;
	uint256 expectedAmountOut;
	uint256 amountOut = expectedAmountOut * 4;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountToFill, amountOut);

	require amountToFill < 10000000;
	require expectedAmountOut < 10000000;

	uint256 _bentoBalanceOut; 
	uint256 _bentoBalanceIn;	
	uint256 bentoBalanceOut_;
	uint256 bentoBalanceIn_;	

	if (outFlag)
		require _bentoBalanceOut == bentoBalanceOf(tokenOut, recipient);
	else 
		require _bentoBalanceIn == bentoBalanceOf(tokenIn, maker);	

	calldataarg args;
	env e;
	f(e, args);

	if (outFlag)
		require bentoBalanceOut_ == bentoBalanceOf(tokenOut, recipient);
	else 
		require bentoBalanceIn_ == bentoBalanceOf(tokenIn, maker);	
	
	// at least expectedAmountOut coins were added to recipient. 
	if (outFlag) {
		uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);
		uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);
		assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + expectedAmountOut;
	}
	else 
		assert bentoBalanceIn_ + amountToFill >= _bentoBalanceIn;
}

rule FillOrderWithAmountIn1(method f) filtered {f -> 
	f.selector == fillOrderHarness(bytes).selector // || 
	// f.selector == fillOrderOpenHarness().selector || 
	// f.selector ==  batchFillOrderHarness().selector || 
	// f.selector == batchFillOrderOpenHarness().selector 
	} {
	fillOrderWithAmountInFunction(true, f);
	assert true;
}

rule FillOrderWithAmountIn2(method f) filtered {f -> 
	f.selector == fillOrderHarness(bytes).selector // || 
	// f.selector == fillOrderOpenHarness().selector || 
	// f.selector ==  batchFillOrderHarness().selector || 
	// f.selector == batchFillOrderOpenHarness().selector 
	} {
	fillOrderWithAmountInFunction(false, f);
	assert true;
}


// Checks fees are collected correctly.
rule CheckFees(method f) filtered { f -> 
	f.selector == fillOrderOpenHarness(bytes).selector 
	// ||	
	// f.selector == batchFillOrderOpenHarness((address,uint256,uint256,address,uint256,uint256,uint256,address,bytes,uint256,uint8,bytes32,bytes32),bytes).selector 
	} {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker == 2) || (maker == recipient);
	uint256 amountToFill;
	uint256 amountIn;
	
	uint256 expectedFee;
	require expectedFee < 10000000;
	uint256 amountOut = 4 * expectedFee;

	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountIn, amountOut);
	require externalOrderFee() == FEE_DIVISOR() / 4;

	uint256 _feesCollected = feesCollected(tokenOut);

	calldataarg args;
	env e;
	f(e, args);

	uint256 feesCollected_ = feesCollected(tokenOut);

	assert feesCollected_ >= _feesCollected + expectedFee;
}

// Checks that the contract indeed holds feesCollected tokens.
invariant feesInvariant(address token) 
	bentoBalanceOf(token, thisAddress()) >= feesCollected(token)
// totally times out..


// Doesn't work, and i don't get counter example.
rule fillOrderLiveness()  {
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

	invoke fillOrderHarness(e, args); 
	assert !lastReverted;
}


// Same order called twice works well in the case that the two amountToFill sum to at most amountIn.
rule TwoSameOrders() {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));
	uint256 amountOut = 100;
	uint256 amountToFill = 1000;
	uint256 amountIn = 4000;
	
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountToFill, amountOut);

//	uint256 _bentoBalanceIn = bentoBalanceOf(tokenIn, maker);	
	uint256 _bentoBalanceOut = bentoBalanceOf(tokenOut, recipient);
	uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);

	calldataarg args;
	env e;
	fillOrderHarness(e, args);

	calldataarg args2;
	env e2;
	fillOrderHarness(e2, args2);

//	uint256 bentoBalanceIn_ = bentoBalanceOf(tokenIn, maker);
	uint256 bentoBalanceOut_ = bentoBalanceOf(tokenOut, recipient);
	uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);

	// at least amountOut coins were added to recipient. 
	assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + 50;
	// no more than amountIn tokens were taken from maker.
//	assert bentoBalanceIn_ + 2000 >= _bentoBalanceIn;
}


// Same order called twice fail in the case that the two amountToFill sum more than amountIn.
rule TwoSameOrdersFail() {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));
	uint256 amountOut = 100;
	uint256 amountToFill = 3000;
	uint256 amountIn = 4000;
	
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountToFill, amountOut);

	calldataarg args;
	env e;
	fillOrderHarness(e, args);

	calldataarg args2;
	env e2;
	invoke fillOrderHarness(e2, args2);

	assert lastReverted;
}

// If two orders differ by something (so that digest is different), they can both succeed. (in therms of tokenOut)
rule TwoDifferentOrdersAreCool1() {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));
	uint256 amountOut = 100;
	uint256 amountToFill = 3000;
	uint256 amountIn = 4000;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountToFill, amountOut);
	
	// Just to be able to get a different digest
	uint256 stopPrice1;
	uint256 stopPrice2;
	require stopPrice1 != stopPrice2;
	require stopPriceHarness() == stopPrice1;
	bytes32 digest1= getDigestHarness();

	uint256 _bentoBalanceOut = bentoBalanceOf(tokenOut, recipient);
	uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);
//	uint256 _bentoBalanceIn = bentoBalanceOf(tokenIn, maker);	

	calldataarg args;
	env e;
	fillOrderHarness(e, args);

	env e2;
	setStopPrice(e2, stopPrice2);
	bytes32 digest2 = getDigestHarness();
	require digest1 != digest2;

	calldataarg args3;
	env e3;
	fillOrderHarness(e3, args3);

	uint256 bentoBalanceOut_ = bentoBalanceOf(tokenOut, recipient);
	uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);
//	uint256 bentoBalanceIn_ = bentoBalanceOf(tokenIn, maker);	

	assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + 150;
//	assert bentoBalanceIn_ + 6000 >= _bentoBalanceIn;
}


// In terms of tokenIn
rule TwoDifferentOrdersAreCool2() {
	address recipient = 1;
	address maker;
	address tokenIn;
	address tokenOut;
	require (maker == 2) || ((maker == recipient) && (tokenIn != tokenOut));
	uint256 amountOut = 100;
	uint256 amountToFill = 3000;
	uint256 amountIn = 4000;
	prepare(recipient, maker, tokenIn, tokenOut, amountIn, amountToFill, amountOut);
	
	// Just to be able to get a different digest
	uint256 stopPrice1;
	uint256 stopPrice2;
	require stopPrice1 != stopPrice2;
	require stopPriceHarness() == stopPrice1;
	bytes32 digest1 = getDigestHarness();

	uint256 _bentoBalanceIn = bentoBalanceOf(tokenIn, maker);	

	calldataarg args;
	env e;
	fillOrderHarness(e, args);

	env e2;
	setStopPrice(e2, stopPrice2);
	bytes32 digest2 = getDigestHarness();
	require digest1 != digest2;

	calldataarg args3;
	env e3;
	fillOrderHarness(e3, args3);

	uint256 bentoBalanceIn_ = bentoBalanceOf(tokenIn, maker);	
	
	assert bentoBalanceIn_ + 6000 >= _bentoBalanceIn;
}







// Should fail!
rule digestSanity() {
	uint256 stopPrice1;
	uint256 stopPrice2;
	require stopPrice1 != stopPrice2;
	require stopPriceHarness() == stopPrice1;
	bytes32 digest1 = getDigestHarness();

	env e;
	setStopPrice(e, stopPrice2);

	bytes32 digest2 = getDigestHarness();
	
	assert digest1 == digest2;
}






// two orders stuff..

// need a liveness version for everything: if conditions are good enough, nothing will fail..

// out of time order fails

// change ratio..

// The batch are strange - even if one fails (because of stop or limit) they all fail.