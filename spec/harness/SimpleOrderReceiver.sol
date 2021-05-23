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
    IERC20 public token1;
    address public to1;
    uint256 public amount1;

    IERC20 public token2;
    address public to2;
    uint256 public amount2;

    address public somewhere;


    function onLimitOrder (IERC20 tokenIn, IERC20 tokenOut, uint256 amountIn, uint256 amountMinOut, bytes calldata data) override external {
        

        //----------------------------------------------------------------
        // To model a malicious one

        // Ideally just two completely arbitrary transfers
        // bentoBox.transfer(token1, from1, to1, amount1);
        // bentoBox.transfer(token2, from2, to2, amount2);
        // It fails rules because it managed to transfer money from other contracts, by passing the "allowed"
        // modifier, even if it was not the bentoBox, but using the mastercontract stuff.

        // So this is better, and normally I put just one transfer to make verification easier 
        // bentoBox.transfer(token1, address(this), to1, amount1);
        // bentoBox.transfer(token2, address(this), to2, amount2);

        // All this has to be checked with the toBase stuff.
        // This does not take from the maker. The problem is there is actually no check on how much one
        // takes from the maker.. So I don't really let it run free.
    
        // Maybe also give opportunity for revert, and call back..



        // -----------------------------------------------------------------------
        // To abstract sushiSwapLimitOrderReceiver.

        // These are the lines from sushSwapOrderReceiver:
        // bentoBox.withdraw(tokenIn, address(this), address(this), amountIn, 0);
        // bentoBox.deposit(tokenOut, address(bentoBox), msg.sender, amountMinOut, 0);
        // bentoBox.deposit(tokenOut, address(bentoBox), to, amountOut.sub(amountMinOut), 0);
        // so we do:
        bentoBox.transfer(tokenIn, address(this), somewhere, bentoBox.toShare(tokenOut, amountIn, true));
        bentoBox.transfer(tokenOut, address(bentoBox), msg.sender, bentoBox.toShare(tokenOut, amountMinOut, false));
        // The difference is because transfer works with shares, while deposit and withdraw work with tokens, 
        // and they round (withdraw up and deposit down) if they get a token amount parameter.
        // "somewhere" is just so we throw away the coins. In effect i think it only lets us check that
        // there are at least this amount of coins in the balance of "this".
        // Third line we ignore, because "to" is from the data which we know nothing about.
    }
}