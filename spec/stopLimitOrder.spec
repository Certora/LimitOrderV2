/*
    This is a specification file for smart contract verification
    with the Certora prover. For more information,
	visit: https://www.certora.com/

    This file is run with scripts/...
	Assumptions:
*/

using SimpleOrderReceiver as receiver
using SimpleBentoBox as bentoBox
using DummyERC20A as tokenA
using DummyERC20B as tokenB
using Simplifications as simplified

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

	makerHarnessOther() returns (address) envfree
	tokenOutHarnessOther() returns (address) envfree

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
	simplified.computeAmountOut(uint256 amountIn, uint256 amountOut, uint256 amountToBeFilled)
							returns (uint256) envfree => DISPATCHER(true)
	ec_recover(bytes32 digest, uint8 v, bytes32 r, bytes32 s) 
						returns (address) => NONDET

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
	toShare(address token, uint256 amount, bool roundUp) 
		returns (uint256) envfree => DISPATCHER(true)
	registerProtocol() => NONDET

	// oracle
	get(uint) returns (bool, uint256) => NONDET

	// ERC20
	tokenA.balanceOf(address) returns (uint256) => DISPATCHER(true)
	tokenB.balanceOf(address) returns (uint256) => DISPATCHER(true)
	tokenA.transfer(address, uint256) => DISPATCHER(true)
	tokenB.transfer(address, uint256) => DISPATCHER(true)
	permit(address from, address to, uint amount, uint deadline, uint8 v, bytes32 r, bytes32 s) => NONDET
}

////////////////////////////////////////////////////////////////////////////
//                                 Ghost                                  //
////////////////////////////////////////////////////////////////////////////
ghost digestGhost(address, address, address, uint256, uint256, address, uint256, 
				uint256, uint256, address, uint256) returns bytes32;

////////////////////////////////////////////////////////////////////////////
//                               Invariants                               //
////////////////////////////////////////////////////////////////////////////
// Checks that the bentobox indeed holds the feesCollected tokens.
invariant feesInvariant(address token)
	bentoBalanceOf(token, currentContract) >= feesCollected(token) {
		preserved {
			require makerHarness() != currentContract;
		}
	}

////////////////////////////////////////////////////////////////////////////
//                                 Rules                                  //
////////////////////////////////////////////////////////////////////////////
// Once fee is collected in terms of some token, it never becomes zero again
rule feesCollectedNeverZero(method f, address token) {
	require feesCollected(token) > 0;

	env e;
	calldataarg args;
	f(e, args);

	assert feesCollected(token) > 0;
}

// Any operation shouldn’t affect other fill orders
rule noChangeToOtherOrders(method f) {
	env e;

	calldataarg digestArgs;
	bytes32 digest = getDigest(e, digestArgs);

	calldataarg digestArgsOther;
	bytes32 otherDigest = getDigestOther(e, digestArgsOther);

	require digest != otherDigest;

	// record other's state before
	bool _isOtherCancelled = cancelledOrder(makerHarnessOther(), otherDigest);
	uint256 _otherOrderStatus = orderStatus(otherDigest);
	uint256 _otherTokenOutFeesCollected = feesCollected(tokenOutHarnessOther());

	// Call f with digest order
	calldataarg args;
	f(e, args);

	// record other's state after
	bool isOtherCancelled_ = cancelledOrder(makerHarnessOther(), otherDigest);
	uint256 otherOrderStatus_ = orderStatus(otherDigest);
	uint256 otherTokenOutFeesCollected_ = feesCollected(tokenOutHarnessOther());

	// compare
	assert _isOtherCancelled == isOtherCancelled_;
	assert _otherOrderStatus == otherOrderStatus_;
	assert _otherTokenOutFeesCollected == otherTokenOutFeesCollected_;
}

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
rule cancelledCannotBeFilled(method f) filtered { f -> 
		f.selector == fillOrder((address, uint256, uint256, address, uint256, uint256, uint256,
		 						 address, uint256, uint256, uint8, bytes32, bytes32), address, address,
								 address, bytes).selector ||
		f.selector == fillOrderOpen((address, uint256, uint256, address, uint256, uint256, uint256,
								     address, uint256, uint256, uint8, bytes32, bytes32), address, 
									 address, address, bytes).selector /*||
		f.selector == batchFillOrder((address, uint256, uint256, address, uint256, uint256,
									  uint256, address, uint256, uint256, uint8, bytes32,
									  bytes32)[], address, address, address, bytes).selector || 
		f.selector == batchFillOrderOpen((address, uint256, uint256, address, uint256, uint256, uint256,
	  					address, uint256, uint256, uint8, bytes32, bytes32)[], address,
						address, address, bytes)*/ } { // TODO: If we are able to make batchFillOrder work, uncomment them
	env e;

	calldataarg digestArgs;
	bytes32 digest = getDigest(e, digestArgs);

	require cancelledOrder(makerHarness(), digest);

	calldataarg args;
	f(e, args);

	assert lastReverted;
}

// total assets are preserved for every exchange
rule preserveAssets(method f) filtered { f -> 
		f.selector == fillOrder((address, uint256, uint256, address, uint256, uint256, uint256,
		 						 address, uint256, uint256, uint8, bytes32, bytes32), address, address,
								 address, bytes).selector ||
		f.selector == fillOrderOpen((address, uint256, uint256, address, uint256, uint256, uint256,
								     address, uint256, uint256, uint8, bytes32, bytes32), address, 
									 address, address, bytes).selector } {
	require tokenInHarness() != tokenOutHarness();
	require makerHarness() != recipientHarness();
	require makerHarness() != currentContract;
	
	uint256 _bentoBalanceIn = bentoBalanceOf(tokenInHarness(), makerHarness());
	uint256 _bentoBalanceOut = bentoBalanceOf(tokenOutHarness(), recipientHarness());
	uint256 _bentoCurrContractBalance = bentoBalanceOf(tokenOutHarness(), currentContract);

	calldataarg args;
	env e;
	f(e, args);

	uint256 bentoBalanceIn_ = bentoBalanceOf(tokenInHarness(), makerHarness());
	uint256 bentoBalanceOut_ = bentoBalanceOf(tokenOutHarness(), recipientHarness());
	uint256 bentoCurrContractBalance_ = bentoBalanceOf(tokenOutHarness(), currentContract);

	uint256 expectedAmountOut = simplified.computeAmountOut(amountInHarness(), amountOutHarness(), amountToFillHarness());

	assert(bentoBalanceIn_ >= _bentoBalanceIn - bentoBox.toShare(tokenInHarness(),
	        amountToFillHarness(), false), "tokenIn assets not preserved");
	assert(bentoBalanceOut_ >= _bentoBalanceOut + bentoBox.toShare(tokenOutHarness(),
	    	expectedAmountOut, false), "tokenOut assets not preserved");
	assert(bentoCurrContractBalance_ >= _bentoCurrContractBalance, "StopLimitOrder balance decreased");
}

/* 	
	Rule: Fill order is up to the amountIn
 	Description: The total filled amount of an order is never more than the amountIn
	Formula: 
			orderStatus(digest(order)) <= order.amountIn		
*/
rule orderStatusLeAmountToFill(method f) {
	env e;

	calldataarg digestArgs;
	bytes32 digest = getDigest(e, digestArgs);

	uint256 orderStatusBefore = orderStatus(digest);

	require orderStatusBefore <= amountInHarness();

	calldataarg args;
	f(e, args);

	uint256 orderStatusAfter = orderStatus(digest);
	
	assert orderStatusAfter <= amountInHarness();
}

////////////////////////////////////////////////////////////////////////////
//                                Temporary                               //
////////////////////////////////////////////////////////////////////////////
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