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

    // these should be limited in the spec.
    uint256 public giveOut;
    uint256 public extraOut;
    address public to;

    function onLimitOrder (IERC20 tokenIn, IERC20 tokenOut, uint256 amountIn, uint256 amountMinOut, bytes calldata data) override external {
        // we are ignoring the check that bentobox indeed got amountIn, and we are not withdrawing it.

        bentoBox.transfer(tokenOut, address(bentoBox), msg.sender, giveOut);
        bentoBox.transfer(tokenOut, address(bentoBox), to, extraOut);

        // Maybe also give opportunity for revert, and call back..
    }
}