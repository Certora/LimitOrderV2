certoraRun spec/harness/StopLimitOrderHarness.sol spec/harness/SimpleBentoBox.sol spec/harness/SimpleOrderReceiver.sol spec/harness/DummyERC20A.sol spec/harness/DummyERC20B.sol spec/harness/Simplifications.sol spec/harness/OracleHarness.sol \
    --solc solc6.12 \
    --verify StopLimitOrderHarness:spec/stopLimitOrder.spec \
    --cache SushiLimitOrder \
    --link StopLimitOrderHarness:bentoBox=SimpleBentoBox \
    --link SimpleOrderReceiver:bentoBox=SimpleBentoBox \
    --settings -enableStorageAnalysis=true,-ignoreViewFunctions,-assumeUnwindCond,-postProcessCounterExamples=true,-optimisticReturnsize=true \
    --msg "StopLimitOrder all rules" --staging
