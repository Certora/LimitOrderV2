pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "../../contracts/StopLimitOrder.sol";

contract Simplifications is A {
	// for simplifications
	mapping(uint256 => mapping(uint256 => mapping(uint256 => uint256))) public amountToBeReturned;
	address public ecrecover_return;

	function abstract_keccak256(address maker, IERC20 tokenIn, IERC20 tokenOut,
								uint256 amountIn, uint256 amountOut, address recipient,
								uint256 startTime, uint256 endTime, uint256 stopPrice,
								IOracle oracleAddress, uint oracleData)
								external override pure returns (bytes32) {
		// abstract_keccak256 has a ghost summary on it, so the return
		// value can be ignored.
		return "ignored";
	}
	
	// simplifies the division in _preFillOrder
	function computeAmountOut(uint256 amountIn, uint256 amountOut, uint256 amountToBeFilled)
							  external override view returns (uint256) {
		uint256 res = amountToBeReturned[amountIn][amountOut][amountToBeFilled];
		require(res <= amountOut);
		require(res < amountOut || amountIn == amountToBeFilled);
	}

	function ec_recover(bytes32 digest, uint8 v, bytes32 r, bytes32 s) 
						external override view returns (address) {
		return ecrecover_return;
	}
}

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

	////////////////////////////////////////////////////////////
	//                 constructors and inits                 //
	////////////////////////////////////////////////////////////
	constructor(uint256 _externalOrderFee, IBentoBoxV1 _bentoBox)
		StopLimitOrder(_externalOrderFee, _bentoBox) public {
			a = new Simplifications();
		}

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