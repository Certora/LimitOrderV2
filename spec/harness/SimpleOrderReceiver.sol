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

    function onLimitOrder (IERC20 tokenIn, IERC20 tokenOut, uint256 amountIn, uint256 amountMinOut, bytes calldata data) override external {
        bentoBox.withdraw(tokenIn, address(this), address(this), amountIn, 0);
        (, uint256 amountOutMinExternal, address to) = abi.decode(data, (address[], uint256, address));
        bentoBox.deposit(tokenOut, address(bentoBox), msg.sender, giveOut, 0);
        bentoBox.deposit(tokenOut, address(bentoBox), to, extraOut, 0);

        // Maybe also give opportunity for revert, and call back..
    }
}