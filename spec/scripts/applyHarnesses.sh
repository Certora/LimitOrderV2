# SafeTransfer simplification
perl -0777 -i -pe 's/safeT/t/g' contracts/StopLimitOrder.sol

# Add transfer function declaration 
perl -0777 -i -pe 's/;\s*\}/;\n    function transfer\(address to, uint256 amount\) external;\n    function transferFrom\(address from, address to, uint256 amount\) external;\/\/ done \n\}/g' node_modules/@boringcrypto/boring-solidity/contracts/interfaces/IERC20.sol

# virtualize functions for BentoBoxV1
perl -0777 -i -pe 's/public payable \{/public virtual payable \{/g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol
perl -0777 -i -pe 's/external payable returns/external virtual payable returns/g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol
perl -0777 -i -pe 's/external view returns \(uint256 /external virtual view returns \(uint256 /g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol
perl -0777 -i -pe 's/uint256\[\] calldata amounts,\s+bytes calldata data\s+\) public/uint256\[\] calldata amounts,bytes calldata data\) public virtual/g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol 

# remove hardhat console and add import for Simplifications
perl -0777 -i -pe 's/import \"hardhat/\/\/ import \"hardhat/g' contracts/StopLimitOrder.sol
perl -0777 -i -pe 's/import \".\/interfaces\/IOracle.sol\";/import \".\/interfaces\/IOracle.sol\";\nimport \"..\/spec\/harness\/Simplifications.sol\";/g' contracts/StopLimitOrder.sol

# adding Simplifications object
perl -0777 -i -pe 's/struct OrderArgs/Simplifications public simplified;\n
    struct OrderArgs/g' contracts/StopLimitOrder.sol

# private to internal
perl -0777 -i -pe 's/private/internal/g' contracts/StopLimitOrder.sol

# external to public
perl -0777 -i -pe 's/external /public /g' contracts/StopLimitOrder.sol

# oracleData bytes -> uint
perl -0777 -i -pe 's/bytes oracleData;/uint oracleData;/g' contracts/StopLimitOrder.sol
perl -0777 -i -pe 's/keccak256\(order.oracleData\)/order.oracleData/g' contracts/StopLimitOrder.sol
perl -0777 -i -pe 's/function get\(bytes calldata data\)/function get\(uint data\)/g' contracts/interfaces/IOracle.sol
perl -0777 -i -pe 's/function get\(bytes calldata data\)/function get\(uint data\)/g' spec/harness/OracleHarness.sol

# simplify digest
perl -0777 -i -pe 's/function _getDigest\(OrderArgs memory order, IERC20 tokenIn, IERC20 tokenOut\) internal/function _getDigest\(OrderArgs memory order, IERC20 tokenIn, IERC20 tokenOut\) virtual internal view returns \(bytes32\) {
        return simplified.abstract_keccak256\(
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

# simplify ecrecover
perl -0777 -i -pe 's/ecrecover/simplified.ec_recover/g' contracts/StopLimitOrder.sol 

# simplify computation
perl -0777 -i -pe 's/order.amountOut.mul\(amountToBeFilled\) \/ order.amountIn/simplified.computeAmountOut(order.amountOut, order.amountIn, amountToBeFilled)/g' contracts/StopLimitOrder.sol 

# virtualize batch
perl -0777 -i -pe 's/function batch\(bytes\[\] calldata calls, bool revertOnFail\) external/function batch\(bytes\[\] calldata calls, bool revertOnFail\) virtual external/g' node_modules/@boringcrypto/boring-solidity/contracts/BoringBatchable.sol

# virtualizing fillOrders and other functions
perl -0777 -i -pe 's/function fillOrder\(
            OrderArgs memory order,
            IERC20 tokenIn,
            IERC20 tokenOut, 
            ILimitOrderReceiver receiver, 
            bytes calldata data\) 
    public \{/function fillOrder\(
            OrderArgs memory order,
            IERC20 tokenIn,
            IERC20 tokenOut, 
            ILimitOrderReceiver receiver, 
            bytes calldata data\) 
    virtual public \{/g' contracts/StopLimitOrder.sol

perl -0777 -i -pe 's/function fillOrderOpen\(
            OrderArgs memory order,
            IERC20 tokenIn,
            IERC20 tokenOut, 
            ILimitOrderReceiver receiver, 
            bytes calldata data\) 
    public \{/function fillOrderOpen\(
            OrderArgs memory order,
            IERC20 tokenIn,
            IERC20 tokenOut, 
            ILimitOrderReceiver receiver, 
            bytes calldata data\) 
    virtual public \{/g' contracts/StopLimitOrder.sol 

perl -0777 -i -pe 's/function batchFillOrder\(
            OrderArgs\[\] memory order,
            IERC20 tokenIn,
            IERC20 tokenOut,
            ILimitOrderReceiver receiver, 
            bytes calldata data\)/function batchFillOrder\(
            OrderArgs\[\] memory order,
            IERC20 tokenIn,
            IERC20 tokenOut,
            ILimitOrderReceiver receiver, 
            bytes calldata data\) 
    virtual /g' contracts/StopLimitOrder.sol

perl -0777 -i -pe 's/function batchFillOrderOpen\(
            OrderArgs\[\] memory order,
            IERC20 tokenIn,
            IERC20 tokenOut,
            ILimitOrderReceiver receiver, 
            bytes calldata data\)/function batchFillOrderOpen\(
            OrderArgs\[\] memory order,
            IERC20 tokenIn,
            IERC20 tokenOut,
            ILimitOrderReceiver receiver, 
            bytes calldata data\) 
    virtual /g' contracts/StopLimitOrder.sol 
