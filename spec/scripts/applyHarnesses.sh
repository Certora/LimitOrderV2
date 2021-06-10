# SafeTransfer simplification
# sed -i 's/safeT/t/g' contracts/BentoBoxPlus.sol
# sed -i 's/safeT/t/g' contracts/LendingPair.sol
# perl -0777 -i -pe 's/safeT/t/g' contracts/StopLimitOrder.sol

# Virtualize functions
perl -0777 -i -pe 's/public payable \{/public virtual payable \{/g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol
perl -0777 -i -pe 's/external payable returns/external virtual payable returns/g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol
perl -0777 -i -pe 's/external view returns \(uint256 /external virtual view returns \(uint256 /g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol
perl -0777 -i -pe 's/uint256\[\] calldata amounts,\s+bytes calldata data\s+\) public/uint256\[\] calldata amounts,bytes calldata data\) public virtual/g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol 

# Remove hardhat console
perl -0777 -i -pe 's/import \"hardhat/\/\/import  \"hardhat/g' contracts/StopLimitOrder.sol

# private to internal
perl -0777 -i -pe 's/private/internal/g' contracts/StopLimitOrder.sol

# external to public
perl -0777 -i -pe 's/external /public /g' contracts/StopLimitOrder.sol

# oracleData bytes -> uint
perl -0777 -i -pe 's/bytes oracleData;/uint oracleData;/g' contracts/StopLimitOrder.sol
perl -0777 -i -pe 's/function get\(bytes calldata data\)/function get\(uint data\)/g' contracts/interfaces/IOracle.sol
perl -0777 -i -pe 's/keccak256\(order.oracleData\)/order.oracleData/g' contracts/StopLimitOrder.sol

# Add ghost
perl -0777 -i -pe 's/contract StopLimitOrder/interface A {
        function abstract_keccak256\(address maker, IERC20 tokenIn, IERC20 tokenOut, uint256 amountIn, uint256 amountOut, address recipient, uint256 startTime, uint256 endTime, uint256 stopPrice, IOracle oracleAddress, uint oracleData\) external\/*trick*\/ pure returns \(bytes32\);
        function ec_recover\(bytes32 digest, uint8 v, bytes32 r, bytes32 s\) external view returns \(address\); 
    }
    contract  StopLimitOrder/g' contracts/StopLimitOrder.sol
perl -0777 -i -pe 's/struct OrderArgs/A public a;
struct  OrderArgs/g' contracts/StopLimitOrder.sol

# Simplify digest
perl -0777 -i -pe 's/function _getDigest\(OrderArgs memory order, IERC20 tokenIn, IERC20 tokenOut\) internal/function _getDigest\(OrderArgs memory order, IERC20 tokenIn, IERC20 tokenOut\)   internal view returns \(bytes32\) {
    return a.abstract_keccak256\(
                order.maker,
                tokenIn,
                tokenOut,
                order.amountIn,
                order.amountOut,
                order.recipient,
                order.startTime,
                order.endTime,
                order.stopPrice,
                order.oracleAddress,
                order.oracleData
    \);
}
function _getDigestOld\(OrderArgs memory order, IERC20 tokenIn, IERC20 tokenOut\) private/g' contracts/StopLimitOrder.sol 

# Simplify ecrecover
perl -0777 -i -pe 's/ecrecover/a.ec_recover/g' contracts/StopLimitOrder.sol 

# Virtualize batch
perl -0777 -i -pe 's/function batch\(bytes\[\] calldata calls, bool revertOnFail\) external/function batch\(bytes\[\] calldata calls, bool revertOnFail\) virtual external/g' node_modules/@boringcrypto/boring-solidity/contracts/BoringBatchable.sol