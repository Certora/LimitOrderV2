pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@sushiswap/bentobox-sdk/contracts/IBentoBoxV1.sol";


contract SuperSimpleBentoBox is IBentoBoxV1 {

    mapping(IERC20 => mapping(address => uint256)) public _balanceOf;


	function balanceOf(IERC20 token, address user) external override view returns (uint256) {
		return _balanceOf[token][user];
	}

	function deposit(IERC20 token, address from, address to, uint256 amount, uint256 share) external override payable returns (uint256 amountOut, uint256 shareOut) {
		assert(amount == 0);
		token.transferFrom(from, address(this), amount);
	}


    function batch(bytes[] calldata calls, bool revertOnFail) external override payable returns (bool[] memory successes, bytes[] memory results) {}

    function batchFlashLoan(IBatchFlashBorrower borrower, address[] calldata receivers, IERC20[] calldata tokens, uint256[] calldata amounts, bytes calldata data) override external {}

  	function claimOwnership() override external {}

    function deploy(address masterContract, bytes calldata data, bool useCreate2) external override payable {}

  
    function flashLoan(IFlashBorrower borrower, address receiver, IERC20 token, uint256 amount, bytes calldata data) external override {}

    function harvest(IERC20 token, bool balance, uint256 maxChangeAmount) external override {}
    function masterContractApproved(address, address) external override view returns (bool) {}
    function masterContractOf(address) external override view returns (address) {}
    function nonces(address) external override view returns (uint256) {}
    function owner() external override view returns (address) {}
    function pendingOwner() external override view returns (address) {}
    function pendingStrategy(IERC20) external override view returns (IStrategy) {}
    function permitToken(IERC20 token, address from, address to, uint256 amount, uint256 deadline, uint8 v, bytes32 r, bytes32 s) override external {}
    function registerProtocol() override external {}
    function setMasterContractApproval(address user, address masterContract, bool approved, uint8 v, bytes32 r, bytes32 s) override external {}
    function setStrategy(IERC20 token, IStrategy newStrategy) override external {}
    function setStrategyTargetPercentage(IERC20 token, uint64 targetPercentage_) override external {}
    function strategy(IERC20) override external view returns (IStrategy) {}

    function strategyData(IERC20) override external view returns (uint64 strategyStartDate, uint64 targetPercentage, uint128 balance) {}

    function toAmount(IERC20 token, uint256 share, bool roundUp) override external view returns (uint256 amount) {}

    function toShare(IERC20 token, uint256 amount, bool roundUp) override external view returns (uint256 share) {}

    function totals(IERC20) override external view returns (Rebase memory totals_) {}

    function transfer(IERC20 token, address from, address to, uint256 share) override external {}
    function transferMultiple(IERC20 token, address from, address[] calldata tos, uint256[] calldata shares) override external {}

    function transferOwnership(address newOwner, bool direct, bool renounce) override external {}

    function whitelistMasterContract(address masterContract, bool approved) override external {}
    function whitelistedMasterContracts(address) override external view returns (bool) {}

    function withdraw(IERC20 token_, address from, address to, uint256 amount, uint256 share) override external returns (uint256 amountOut, uint256 shareOut) {}
}