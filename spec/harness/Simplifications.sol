pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@boringcrypto/boring-solidity/contracts/libraries/BoringERC20.sol";
import "../../contracts/interfaces/IOracle.sol";

contract Simplifications {
	// for simplifications
	mapping(uint256 => mapping(uint256 => mapping(uint256 => uint256))) public amountToBeReturned;
	address public ecrecover_return;

	function abstract_keccak256(address maker, IERC20 tokenIn, IERC20 tokenOut,
								uint256 amountIn, uint256 amountOut, address recipient,
								uint256 startTime, uint256 endTime, uint256 stopPrice,
								IOracle oracleAddress, uint oracleData)
								external pure returns (bytes32) {
		// abstract_keccak256 has a ghost summary on it, so the return
		// value can be ignored.
		return "";
	}
	
	// simplifies the division in _preFillOrder
	function computeAmountOut(uint256 amountIn, uint256 amountOut, uint256 amountToBeFilled)
							  external view returns (uint256) {
		uint256 res = amountToBeReturned[amountIn][amountOut][amountToBeFilled];
		require(res <= amountOut);
		require(res < amountOut || amountIn == amountToBeFilled);
	}

	// simplifies the ecrecover method
	function ec_recover(bytes32 digest, uint8 v, bytes32 r, bytes32 s) 
						external view returns (address) {
		return ecrecover_return;
	}
}