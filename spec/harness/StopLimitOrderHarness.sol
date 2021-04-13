pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "../../contracts/StopLimitOrder.sol";


contract StopLimitOrderHarness is StopLimitOrder {
	constructor(uint256 _externalOrderFee, IBentoBoxV1 _bentoBox) StopLimitOrder(_externalOrderFee, _bentoBox) public { }
	
	address public ecrecover_return;
	
	function ecrecover(bytes32 digest, uint8 v, bytes32 r, bytes32 s) public view returns (address) {
		return ecrecover_return;
	}


	ILimitOrderReceiver public receiverHarness;
	IERC20 public tokenInHarness;
	IERC20 public tokenOutHarness;
	
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

	function requireOrderParams(OrderArgs memory order) internal view {
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


	function fillOrderHarness(OrderArgs memory order, bytes calldata data)
    public {
		requireOrderParams(order);
		fillOrder(order, tokenInHarness, tokenOutHarness, receiverHarness, data);
	}

}