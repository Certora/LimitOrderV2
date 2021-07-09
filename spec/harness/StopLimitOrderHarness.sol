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
	IERC20 public tokenInHarness;
	IERC20 public tokenOutHarness;
	ILimitOrderReceiver public receiverHarness;

	// ONLY FOR THE RULE noChangeToOtherOrders
	address public makerHarnessOther;
	IERC20 public tokenOutHarnessOther;

	////////////////////////////////////////////////////////////
	//                 constructors and inits                 //
	////////////////////////////////////////////////////////////
	constructor(uint256 _externalOrderFee, IBentoBoxV1 _bentoBox)
		StopLimitOrder(_externalOrderFee, _bentoBox) public { }

	////////////////////////////////////////////////////////////
	//                   getters and setters                  //
	////////////////////////////////////////////////////////////
	function bentoBalanceOf(IERC20 token, address user) public view returns (uint256) {
		return bentoBox.balanceOf(token, user);
	}

	function getDigest(OrderArgs memory order, IERC20 tokenIn, IERC20 tokenOut)
					   public view returns (bytes32) {
		_getDigest(order, tokenIn, tokenOut);
	}

	function getDigestOther(OrderArgs memory order, IERC20 tokenIn, IERC20 tokenOut)
                       public view returns (bytes32) {
		require(order.maker != makerHarness && order.maker == makerHarnessOther); 
		require(order.v != vHarness);
		require(order.r != rHarness);
		require(order.s != sHarness);
		require(tokenIn != tokenInHarness);
		require(tokenOut != tokenOutHarness && tokenOut == tokenOutHarnessOther);

		super._getDigest(order, tokenIn, tokenOut);
	}

	function setStopPrice(uint256 val) public {
		stopPriceHarness = val;
	}

	////////////////////////////////////////////////////////////
	//                    overrided methods                   //
	////////////////////////////////////////////////////////////
	function _getDigest(OrderArgs memory order, IERC20 tokenIn, IERC20 tokenOut)
						internal view override returns (bytes32 digest) {
		compareOrder(order);
		require(tokenIn == tokenInHarness);
		require(tokenOut == tokenOutHarness);

		super._getDigest(order, tokenIn, tokenOut);
	}

	function fillOrder(
            OrderArgs memory order,
            IERC20 tokenIn,
            IERC20 tokenOut, 
            ILimitOrderReceiver receiver, 
            bytes calldata data) 
    public override {
		compareOrder(order);
		require(tokenIn == tokenInHarness);
		require(tokenOut == tokenOutHarness);
		require(receiver == receiverHarness);

		super.fillOrder(order, tokenIn, tokenOut, receiver, data);
	}

	function fillOrderOpen(
            OrderArgs memory order,
            IERC20 tokenIn,
            IERC20 tokenOut, 
            ILimitOrderReceiver receiver, 
            bytes calldata data) 
    public override {
		compareOrder(order);
		require(tokenIn == tokenInHarness);
		require(tokenOut == tokenOutHarness);
		require(receiver == receiverHarness);

		super.fillOrder(order, tokenIn, tokenOut, receiver, data);
	}

	function batchFillOrder(
            OrderArgs[] memory order,
            IERC20 tokenIn,
            IERC20 tokenOut,
            ILimitOrderReceiver receiver, 
            bytes calldata data) 
    public override { }

	function batchFillOrderOpen(
            OrderArgs[] memory order,
            IERC20 tokenIn,
            IERC20 tokenOut,
            ILimitOrderReceiver receiver, 
            bytes calldata data) 
    public override { }

	function batch(bytes[] calldata calls, bool revertOnFail) external override
		payable returns (bool[] memory successes, bytes[] memory results) { }

	////////////////////////////////////////////////////////////
	//                    simplifications                     //
	////////////////////////////////////////////////////////////
	fallback() external {
	    bytes memory data;
        data = abi.decode(msg.data[4:], (bytes));
    }

	////////////////////////////////////////////////////////////
	//                    helper functions                    //
	////////////////////////////////////////////////////////////
	function compareOrder(OrderArgs memory order) private view {
		require(order.maker == makerHarness); 
		require(order.amountIn == amountInHarness);
		require(order.amountOut == amountOutHarness); 
		require(order.recipient == recipientHarness); 
		require(order.startTime == startTimeHarness);
		require(order.endTime == endTimeHarness);
		require(order.stopPrice == stopPriceHarness);
		require(order.oracleAddress == oracleAddressHarness);
		require(order.oracleData == oracleDataHarness);
		require(order.amountToFill == amountToFillHarness);
		require(order.v == vHarness);
		require(order.r == rHarness);
		require(order.s == sHarness);
	}
}