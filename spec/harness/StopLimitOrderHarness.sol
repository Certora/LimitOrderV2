pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "../../contracts/StopLimitOrder.sol";

contract StopLimitOrderHarness is StopLimitOrder {
	// fields of the struct OrderArgs
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

	// variables used in StopLimitOrder
	ILimitOrderReceiver public receiverHarness;
	IERC20 public tokenInHarness;
	IERC20 public tokenOutHarness;

	constructor(uint256 _externalOrderFee, IBentoBoxV1 _bentoBox)
	 StopLimitOrder(_externalOrderFee, _bentoBox) public { }
	
	function bentoBalanceOf(IERC20 token, address user) public view returns (uint256) {
		return bentoBox.balanceOf(token, user);
	}

	address public ecrecover_return;
	function ec_recover(bytes32 digest, uint8 v, bytes32 r, bytes32 s) external view returns (address) {
		return ecrecover_return;
	}

	function setStopPrice(uint256 val) public {
		stopPriceHarness = val;
	}
	
	function createOrder() public view returns (OrderArgs memory order) {
		order = OrderArgs(makerHarness, amountInHarness, amountOutHarness,
						  recipientHarness, startTimeHarness, endTimeHarness, 
						  stopPriceHarness, oracleAddressHarness, oracleDataHarness,
						  amountToFillHarness, vHarness, rHarness, sHarness);
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
	/*
		OrderArgs[] memory orders = new OrderArgs[](1); 
		orders[0] = createOrder();

		batchFillOrder(orders, tokenInHarness, tokenOutHarness, receiverHarness, data);
	*/
	 }

	function batchFillOrderOpenHarness(bytes calldata data) public { 
	/*
		OrderArgs[] memory orders = new OrderArgs[](1); 
		orders[0] = createOrder();

		batchFillOrderOpen(orders, tokenInHarness, tokenOutHarness, receiverHarness, data);
	*/
	}

	// TODO - override all functions and use super ... 
	// function fillOrder(
    //         OrderArgs memory order,
    //         IERC20 tokenIn,
    //         IERC20 tokenOut, 
    //         ILimitOrderReceiver receiver, 
    //         bytes calldata data) 
    // public override { 
	// 	require order.maker == makerHarness;
	// 	super.fillOrder()
	// }

	fallback() external {
	    bytes memory data;
        data = abi.decode(msg.data[4:], (bytes));
    }

	// overwriting batch for simplification
	function batch(bytes[] calldata calls, bool revertOnFail) external override
		payable returns (bool[] memory successes, bytes[] memory results) { }



	// simplify computation
	mapping(uint256 => mapping(uint256 => mapping(uint256 => uint256))) public amountToBeReturned;

	function computAmoutOut(uint256 amountIn, uint256 amountOut, uint256 amountToBeFilled ) external view returns (uint256) {
		uint256 res =  amountToBeReturned[amountIn][amountOut][amountToBeFilled];
		require(res <= amountOut );
		require(res < amountOut || amountIn == amountToBeFilled);
	}
}