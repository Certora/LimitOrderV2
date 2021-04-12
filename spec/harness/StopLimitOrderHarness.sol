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
	OrderArgs public orderHarness;

	function fillOrderHarness(
            bytes calldata data)
    public {
		fillOrder(orderHarness, tokenInHarness, tokenOutHarness, receiverHarness, data);
	}

}