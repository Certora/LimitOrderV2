pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "../../contracts/StopLimitOrder.sol";


contract StopLimitOrderHarness is StopLimitOrder {
	constructor(uint256 _externalOrderFee, IBentoBoxV1 _bentoBox) StopLimitOrder(_externalOrderFee, _bentoBox) public { }
	
	function bentoBalanceOf(IERC20 token, address user) public view returns (uint256) {
		return bentoBox.balanceOf(token, user);
	}


	// currently i just commented this call in the code.. so this is not used.
	address public ecrecover_return;
	function _ecrecover(bytes32 digest, uint8 v, bytes32 r, bytes32 s) public view returns (address) {
		return ecrecover_return;
	}


	ILimitOrderReceiver public receiverHarness;
	IERC20 public tokenInHarness;
	IERC20 public tokenOutHarness;
	
	address public makerHarness; 
	uint256 public amountInHarness;
	uint256 public amountOutHarness; 
    address public recipientHarness; 
    uint256 public startTimeHarness;
    uint256 public endTimeHarness;
    uint256 public stopPriceHarness;
    IOracle public oracleAddressHarness;
    bytes public oracleDataHarness;
    uint256 public amountToFillHarness;
	uint8 public vHarness; 
    bytes32 public rHarness;
    bytes32 public sHarness;

	function requireOrderParams(OrderArgs memory order) public view {
		require(order.maker == makerHarness);
		require(order.amountIn == amountInHarness);
		require(order.amountOut == amountOutHarness);
		require(order.recipient == recipientHarness);
		require(order.startTime == startTimeHarness);
	 	require(order.endTime == endTimeHarness);
		require(order.stopPrice == stopPriceHarness);
	    require(order.oracleAddress == oracleAddressHarness);
    	// require(order.oracleData == oracleDataHarness);
		require(order.amountToFill == amountToFillHarness);
		require(order.v == vHarness); 
    	require(order.r == rHarness);
    	require(order.s == sHarness);
	}

	function thisAddress() public view returns (address) {
		return address(this);
	}

	function getDigestHarness(OrderArgs memory order) public view returns (bytes32) {
		requireOrderParams(order);
		return _getDigest(order, tokenInHarness, tokenOutHarness);
	}

	function fillOrderHarnessNoRevert(OrderArgs memory order, bytes calldata data) public returns (bool) {
		if (order.maker != makerHarness ||
			order.amountIn != amountInHarness ||
			order.amountOut != amountOutHarness ||
			order.recipient != recipientHarness ||
			order.startTime != startTimeHarness ||
	 		order.endTime != endTimeHarness ||
			order.stopPrice != stopPriceHarness ||
	    	order.oracleAddress != oracleAddressHarness ||
    	// require(order.oracleData == oracleDataHarness);
			order.amountToFill != amountToFillHarness ||
			order.v != vHarness ||
    		order.r != rHarness ||
    		order.s != sHarness)
			return false;

		fillOrder(order, tokenInHarness, tokenOutHarness, receiverHarness, data);
		return true;
	}

	function fillOrderHarness(OrderArgs memory order, bytes calldata data) public {
		requireOrderParams(order);
		fillOrder(order, tokenInHarness, tokenOutHarness, receiverHarness, data);
	}

	function fillOrderOpenHarness(OrderArgs memory order, bytes calldata data) public {
		requireOrderParams(order);
		fillOrderOpen(order, tokenInHarness, tokenOutHarness, receiverHarness, data);
	}

	function batchFillOrderHarness(OrderArgs memory order, bytes calldata data) public {
		OrderArgs[] memory orders = new OrderArgs[](1); 
		requireOrderParams(order);
		orders[0] = order;

		batchFillOrder(orders, tokenInHarness, tokenOutHarness, receiverHarness, data);
	}

	function batchFillOrderOpenHarness(OrderArgs memory order, bytes calldata data) public {
		OrderArgs[] memory orders = new OrderArgs[](1); 
		requireOrderParams(order);
		orders[0] = order;

		batchFillOrderOpen(orders, tokenInHarness, tokenOutHarness, receiverHarness, data);
	}

}