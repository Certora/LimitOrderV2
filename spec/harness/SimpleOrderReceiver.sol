// SPDX-License-Identifier: GPL-3.0

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@boringcrypto/boring-solidity/contracts/libraries/BoringERC20.sol";
import "@boringcrypto/boring-solidity/contracts/libraries/BoringMath.sol";
import "@sushiswap/core/contracts/uniswapv2/libraries/TransferHelper.sol";
import "@sushiswap/bentobox-sdk/contracts/IBentoBoxV1.sol";
import "../../contracts/interfaces/ILimitOrderReceiver.sol";


contract SimpleOrderReceiver is ILimitOrderReceiver {
    using BoringERC20 for IERC20;

    IBentoBoxV1 private immutable bentoBox;

    constructor (IBentoBoxV1 _bentoBox) public {
        bentoBox = _bentoBox;
    }

    // these can be limited in the spec.
    IERC20 token1;
    address from1;
    address to1;
    uint256 amount1;

    IERC20 token2;
    address from2;
    address to2;
    uint256 amount2;


    function onLimitOrder (IERC20 tokenIn, IERC20 tokenOut, uint256 amountIn, uint256 amountMinOut, bytes calldata data) override external {
        
        // Just two completely arbitrary transfers
        // bentoBox.transfer(token1, from1, to1, amount1);
        // bentoBox.transfer(token2, from2, to2, amount2);
        // this timed out, and when it didn't it failed rules because
        // it managed to transfer money from other contracts, by passing the "allowed"
        // modifier, even if it was not the bentoBox, but using the mastercontract stuff.
        
        // maybe should do three. 
        bentoBox.transfer(token1, address(this), to1, amount1);
        bentoBox.transfer(token2, address(this), to2, amount2);
    
        // Maybe also give opportunity for revert, and call back..

        // another interesting possibility is let this be an abstract function
        // that can only increase balance of other addresses,
        // and can either increase or decrease the balance of address(this);
    }
}