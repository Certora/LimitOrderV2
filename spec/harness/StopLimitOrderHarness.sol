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
    uint public oracleDataHarness;
    uint256 public amountToFillHarness;
	uint8 public vHarness; 
    bytes32 public rHarness;
    bytes32 public sHarness;

	function setStopPrice(uint256 val) public {
		stopPriceHarness = val;
	}
	
	function createOrder() public view returns (OrderArgs memory order) {
		order = OrderArgs(makerHarness, amountInHarness, amountOutHarness, recipientHarness, startTimeHarness, endTimeHarness, stopPriceHarness, oracleAddressHarness, oracleDataHarness, amountToFillHarness, vHarness, rHarness, sHarness);
	}

	function getDigestHarness() public view returns (bytes32) {
		return _getDigest(createOrder(), tokenInHarness, tokenOutHarness);
	}

	function fillOrderHarness(bytes calldata data) public {
		fillOrder(createOrder(), tokenInHarness, tokenOutHarness, receiverHarness, data);
	}

	function fillOrderOpenHarness(bytes calldata data) public {
		fillOrderOpen(createOrder(), tokenInHarness, tokenOutHarness, receiverHarness, data);
	}

	function batchFillOrderHarness(bytes calldata data) public {
		OrderArgs[] memory orders = new OrderArgs[](1); 
		orders[0] = createOrder();

		batchFillOrder(orders, tokenInHarness, tokenOutHarness, receiverHarness, data);
	 }

	function batchFillOrderOpenHarness(bytes calldata data) public {
		OrderArgs[] memory orders = new OrderArgs[](1); 
		orders[0] = createOrder();

		batchFillOrderOpen(orders, tokenInHarness, tokenOutHarness, receiverHarness, data);
	}

	//todo - override all functions and use super. ... 


	fallback() external {
	    bytes memory data;
        data = abi.decode(msg.data[4:], (bytes));
    }
}