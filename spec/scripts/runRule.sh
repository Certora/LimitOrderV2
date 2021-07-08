certoraRun spec/harness/StopLimitOrderHarness.sol spec/harness/SimpleBentoBox.sol spec/harness/SimpleOrderReceiver.sol spec/harness/DummyERC20A.sol spec/harness/DummyERC20B.sol spec/harness/Simplifications.sol \
    --solc solc6.12 \
    --verify StopLimitOrderHarness:spec/stopLimitOrder.spec \
    --link StopLimitOrderHarness:bentoBox=SimpleBentoBox \
    --link SimpleOrderReceiver:bentoBox=SimpleBentoBox \
    --settings -enableStorageAnalysis=true,-ignoreViewFunctions,-assumeUnwindCond,-postProcessCounterExamples=true \
    --rule $1  \
    --msg "StopLimitOrder : $1 " --cloud
    
# --staging shelly/robustnessAndCalldatasize