
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
	thisAddress() returns (address) envfree
	
	bentoBalanceOf(address, address) returns (uint256) envfree
	cancelled(address sender, bytes32 hash) returns (bool) envfree
	feeTo() returns (address) envfree
	feesCollected(address) returns (uint256) envfree
	externalOrderFee() returns (uint256) envfree
	FEE_DIVISOR() returns (uint256) envfree


	getDigestHarness((address,uint256,uint256,address,uint256,uint256,uint256,address,bytes,uint256,uint8,bytes32,bytes32)) envfree
	
	fillOrderHarness((address,uint256,uint256,address,uint256,uint256,uint256,address,bytes,uint256,uint8,bytes32,bytes32),bytes)

	fillOrderOpenHarness((address,uint256,uint256,address,uint256,uint256,uint256,address,bytes,uint256,uint8,bytes32,bytes32),bytes)

	
	onLimitOrder(address tokenIn, address tokenOut, uint256 amountIn, uint256 amountMinOut, bytes data) => DISPATCHER(true) // HAVOC_ECF
	
	
	abstract_keccak256(address maker, address tokenIn, address tokenOut, uint256 amountIn, uint256 amountOut, address recipient, uint256 startTime, uint256 endTime, uint256 stopPrice, address oracleAddress) => ALWAYS(20)
	// => digestGhost(maker, tokenIn, tokenOut, amountIn, amountOut, recipient, startTime, endTime, stopPrice, oracleAddress); 

	toAmount(address token, uint256 share, bool roundUp) returns (uint256) envfree => DISPATCHER(true)
}

ghost digestGhost(address, address, address, uint256, uint256, address, uint256, uint256, uint256, address) returns bytes32;

definition MAX_UINT256() returns uint256 =
	0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
	

// part 1: after a cancel, the flag is on.
rule afterCancelFails1() {
	env e;
	calldataarg args;
	require makerHarness() == e.msg.sender;
	bytes32 digest = getDigestHarness(args);
	sinvoke cancelOrder(e, digest);
	assert cancelled(e.msg.sender, digest);
}

// part 2: if cancel flag is on, it will always remain on.
rule afterCancelFails2() {
	bytes32 digest;
	address sender;
	require cancelled(sender, digest);

	method f;
	env e;
	calldataarg args;
	sinvoke f(e, args);

	assert cancelled(sender, digest);
}

// part 3: if cancel flag is on then fillOrder fails 
rule afterCancelFails3() {
	calldataarg args;
	address maker;	
	require makerHarness() == maker;
	bytes32 digest = getDigestHarness(args);

	require cancelled(maker, digest);
	env e;
	fillOrderHarness(e, args);
	assert lastReverted;
}

// part 4: if cancel flag is on then fillOrderOpen fails 
rule afterCancelFails4() {
	calldataarg args;
	address maker;	
	require makerHarness() == maker;
	bytes32 digest = getDigestHarness(args);

	require cancelled(maker, digest);
	env e;
	fillOrderOpenHarness(e, args);
	assert lastReverted;
}


// Basically:
// recepient != bentoBox, because then onLoan can take coins from receipient instead of giving to it, because bentoBox can always be taken from.
// tokenIn != tokenOut, because otherwise accounting goes wrong.



// Checks fillOrder results in tokenOut balance increasing as it should.
rule simpleFillOrder1() {
	require receiverHarness() == receiver;

	address recipient = 1;
	require recipientHarness() == recipient;	
	address maker = 2;
	require makerHarness() == maker;
	address tokenIn = 3;
	require tokenInHarness() == tokenIn;
	address tokenOut = 4;
	require tokenOutHarness() == tokenOut;
	// I am counting on all other address being more than 4...

	uint256 amountIn;
	require amountInHarness() == amountIn;
	require amountToFillHarness() == amountIn;
	uint256 amountOut;
	require amountOutHarness() == amountOut;
		
	uint256 _bentoBalanceOut = bentoBalanceOf(tokenOut, recipient);
	uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);

	calldataarg args;
	env e;
	sinvoke fillOrderHarness(e, args);

	uint256 bentoBalanceOut_ = bentoBalanceOf(tokenOut, recipient);
	uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);

	// at least amountOut coins were added to recipient. 
	assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + amountOut;
}


// Checks fillOrder results in tokenIn balance not decreasing too much.
rule simpleFillOrder2() {
	require receiverHarness() == receiver;

	address recipient = 1;
	require recipientHarness() == recipient;	
	address maker = 2;
	require makerHarness() == maker;
	address tokenIn = 3;
	require tokenInHarness() == tokenIn;
	address tokenOut = 4;
	require tokenOutHarness() == tokenOut;

	uint256 amountIn;
	require amountInHarness() == amountIn;
	require amountToFillHarness() == amountIn;
	uint256 amountOut;
	require amountOutHarness() == amountOut;
		
	uint256 _bentoBalanceIn = bentoBalanceOf(tokenIn, maker);	
	calldataarg args;
	env e;
	sinvoke fillOrderHarness(e, args);
	
	uint256 bentoBalanceIn_ = bentoBalanceOf(tokenIn, maker);

	// no more than amountIn tokens were taken from maker.
	assert bentoBalanceIn_ + amountIn >= _bentoBalanceIn;
}

// Checks fillOrder results in tokenOut balance increasing as it should. 
// When AmountToFill is 1/4 of AmountIn 
rule FillOrderWithAmountIn1() {
	require receiverHarness() == receiver;

	address recipient = 1;
	require recipientHarness() == recipient;	
	address maker = 2;
	require makerHarness() == maker;
	address tokenIn = 3;
	require tokenInHarness() == tokenIn;
	address tokenOut = 4;
	require tokenOutHarness() == tokenOut;

	uint256 amountToFill;
	require amountToFillHarness() == amountToFill;
	uint256 amountIn = amountToFill * 4;
	require amountInHarness() == amountIn;
	uint256 expectedAmountOut;
	uint256 amountOut = expectedAmountOut * 4;
	require amountOutHarness() == amountOut;

	require amountToFill < 10000000;
	require expectedAmountOut < 10000000;

	// Otherwise effect on balances will be wrong:
	// so maybe need this in the code. or write a rule for this case.
	require tokenIn != tokenOut;
	
	uint256 _bentoBalanceOut = bentoBalanceOf(tokenOut, recipient);
	uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);

	calldataarg args;
	env e;
	sinvoke fillOrderHarness(e, args);

	uint256 bentoBalanceOut_ = bentoBalanceOf(tokenOut, recipient);
	uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);

	// at least expectedAmountOut coins were added to recipient. 
	assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + expectedAmountOut;
}


// Checks fillOrder results in tokenIn balance not decreasing too much.
// When AmountToFill is 1/4 of AmountIn 
rule FillOrderWithAmountIn2() {
	require receiverHarness() == receiver;

	address recipient = 1;
	require recipientHarness() == recipient;	
	address maker = 2;
	require makerHarness() == maker;
	address tokenIn = 3;
	require tokenInHarness() == tokenIn;
	address tokenOut = 4;
	require tokenOutHarness() == tokenOut;

	uint256 amountToFill;
	require amountToFillHarness() == amountToFill;
	uint256 amountIn = amountToFill * 4;
	require amountInHarness() == amountIn;
	uint256 expectedAmountOut;
	uint256 amountOut = expectedAmountOut * 4;
	require amountOutHarness() == amountOut;

	require amountToFill < 10000000;
	require expectedAmountOut < 10000000;
	
	uint256 _bentoBalanceIn = bentoBalanceOf(tokenIn, maker);	
	calldataarg args;
	env e;
	sinvoke fillOrderHarness(e, args);
	
	uint256 bentoBalanceIn_ = bentoBalanceOf(tokenIn, maker);

	// no more than amountToFill tokens were taken from maker.
	assert bentoBalanceIn_ + amountToFill >= _bentoBalanceIn;
}

// Checks fillOrderOpen results in tokenOut balance increasing as it should.
rule simpleFillOrderOpen1() {
	require receiverHarness() == receiver;

	address recipient = 1;
	require recipientHarness() == recipient;	
	address maker = 2;
	require makerHarness() == maker;
	address tokenIn = 3;
	require tokenInHarness() == tokenIn;
	address tokenOut = 4;
	require tokenOutHarness() == tokenOut;

	uint256 amountIn;
	require amountInHarness() == amountIn;
	require amountToFillHarness() == amountIn;
	uint256 amountOut;
	require amountOutHarness() == amountOut;
		
	uint256 _bentoBalanceOut = bentoBalanceOf(tokenOut, recipient);
	uint256 _bentoBalanceOutCoins = bentoBox.toAmount(tokenOut, _bentoBalanceOut, false);

	calldataarg args;
	env e;
	sinvoke fillOrderOpenHarness(e, args);

	uint256 bentoBalanceOut_ = bentoBalanceOf(tokenOut, recipient);
	uint256 bentoBalanceOutCoins_ = bentoBox.toAmount(tokenOut, bentoBalanceOut_, false);

	// at least amountOut coins were added to recipient. 
	assert bentoBalanceOutCoins_ >= _bentoBalanceOutCoins + amountOut;
}

// Checks fillOrderOpen results in tokenIn balance not decreasing too much.
rule simpleFillOrderOpen2() {
	require receiverHarness() == receiver;

	address recipient = 1;
	require recipientHarness() == recipient;	
	address maker = 2;
	require makerHarness() == maker;
	address tokenIn = 3;
	require tokenInHarness() == tokenIn;
	address tokenOut = 4;
	require tokenOutHarness() == tokenOut;

	uint256 amountIn;
	require amountInHarness() == amountIn;
	require amountToFillHarness() == amountIn;
	uint256 amountOut;
	require amountOutHarness() == amountOut;
		
	uint256 _bentoBalanceIn = bentoBalanceOf(tokenIn, maker);	
	calldataarg args;
	env e;
	sinvoke fillOrderOpenHarness(e, args);
	
	uint256 bentoBalanceIn_ = bentoBalanceOf(tokenIn, maker);

	// no more than amountIn tokens were taken from maker.
	assert bentoBalanceIn_ + amountIn >= _bentoBalanceIn;
}

// Checks fees are collected correctly.
rule simpleFillOrderOpen3() {
	require receiverHarness() == receiver;

	address recipient = 1;
	require recipientHarness() == recipient;	
	address maker = 2;
	require makerHarness() == maker;
	address tokenIn = 3;
	require tokenInHarness() == tokenIn;
	address tokenOut = 4;
	require tokenOutHarness() == tokenOut;

	uint256 amountIn;
	require amountInHarness() == amountIn;
	require amountToFillHarness() == amountIn;
	uint256 expectedFee;
	require expectedFee < 10000000;
	uint256 amountOut = 4 * expectedFee;
	require amountOutHarness() == amountOut;


	require externalOrderFee() == FEE_DIVISOR() / 4;
	uint256 _feesCollected = feesCollected(tokenOut);

	calldataarg args;
	env e;
	sinvoke fillOrderOpenHarness(e, args);

	uint256 feesCollected_ = feesCollected(tokenOut);

	assert feesCollected_ >= _feesCollected + expectedFee;
}



// need a liveness version for everything: if conditions are good enough, nothing will fail..

// out of time order fails

// change ratio..

// two orders with amountIn have the same effect as one with the sum.