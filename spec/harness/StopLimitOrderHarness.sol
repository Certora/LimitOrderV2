pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "../../contracts/StopLimitOrder.sol";


contract StopLimitOrderHarness is StopLimitOrder {
	constructor(uint256 _externalOrderFee, IBentoBoxV1 _bentoBox) StopLimitOrder(_externalOrderFee, _bentoBox) public { }
	
	address ecrecover_return;
	function ecrecover(bytes32 digest, uint8 v, bytes32 r, bytes32 s) public view returns (address) {
		return ecrecover_return;
	}

	function fillOrder(
            OrderArgs memory order,
            IERC20 tokenIn,
            IERC20 tokenOut, 
            ILimitOrderReceiver receiver) 
    public {
		bytes calldata a = "0";
		super.fillOrder(order, tokenIn, tokenOut, receiver, a);
	}

}