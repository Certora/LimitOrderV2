// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
import "@boringcrypto/boring-solidity/contracts/libraries/BoringMath.sol";
import "@sushiswap/bentobox-sdk/contracts/IBentoBoxV1.sol";


library SimpleRebase {
    using BoringMath for uint256;
    using BoringMath128 for uint128;

    uint256 private constant RATIO = 1;

    function toBase(Rebase memory total, uint256 elastic, bool roundUp) internal pure returns (uint256 base) {
        if (RATIO == 1)
			return elastic;
        if (elastic == 0)
			return 0;
	    if (roundUp)
			return (elastic.add(1)) / RATIO;
		else 
			return elastic / RATIO;
            
    }

    function toElastic(Rebase memory total, uint256 base, bool roundUp) internal pure returns (uint256 elastic) {
       	if (RATIO == 1)
			return base;
        return base.mul(RATIO);
    }

    function add(Rebase memory total, uint256 elastic, bool roundUp) internal pure returns (Rebase memory, uint256 base) {
        base = toBase(total, elastic, roundUp);
        total.elastic = total.elastic.add(elastic.to128());
        total.base = total.base.add(base.to128());
        return (total, base);
    }

    function sub(Rebase memory total, uint256 base, bool roundUp) internal pure returns (Rebase memory, uint256 elastic) {
        elastic = toElastic(total, base, roundUp);
        total.elastic = total.elastic.sub(elastic.to128());
        total.base = total.base.sub(base.to128());
        return (total, elastic);
    }

    function add(Rebase memory total, uint256 elastic, uint256 base) internal pure returns (Rebase memory) {
        total.elastic = total.elastic.add(elastic.to128());
        total.base = total.base.add(base.to128());
        return total;
    }    

    function sub(Rebase memory total, uint256 elastic, uint256 base) internal pure returns (Rebase memory) {
        total.elastic = total.elastic.sub(elastic.to128());
        total.base = total.base.sub(base.to128());
        return total;
    }    

    function addElastic(Rebase storage total, uint256 elastic) internal returns(uint256 newElastic) {
        newElastic = total.elastic = total.elastic.add(elastic.to128());
    }

    function subElastic(Rebase storage total, uint256 elastic) internal returns(uint256 newElastic) {
        newElastic = total.elastic = total.elastic.sub(elastic.to128());
    }
}