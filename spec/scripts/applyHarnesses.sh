# SafeTransfer simplification
#sed -i 's/safeT/t/g' contracts/BentoBoxPlus.sol
#sed -i 's/safeT/t/g' contracts/LendingPair.sol
# Virtualize functions
perl -0777 -i -pe 's/public payable \{/public virtual payable \{/g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol
perl -0777 -i -pe 's/external payable returns/external virtual payable returns/g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol
perl -0777 -i -pe 's/external view returns \(uint256 /external virtual view returns \(uint256 /g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol
perl -0777 -i -pe 's/uint256\[\] calldata amounts,\s+bytes calldata data\s+\) public/uint256\[\] calldata amounts,bytes calldata data\) public virtual/g' node_modules/@sushiswap/bentobox-sdk/contracts/BentoBoxV1.sol 

