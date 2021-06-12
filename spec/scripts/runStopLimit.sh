certoraRun spec/harness/StopLimitOrderHarness.sol spec/harness/SimpleBentoBox.sol spec/harness/SimpleOrderReceiver.sol \
    --solc solc6.12 \
    --verify StopLimitOrderHarness:spec/stopLimitOrder.spec \
    --link StopLimitOrderHarness:bentoBox=SimpleBentoBox \
    --link SimpleOrderReceiver:bentoBox=SimpleBentoBox \
    --settings -enableStorageAnalysis=true,-ignoreViewFunctions,-assumeUnwindCond,-postProcessCounterExamples=true \
    --msg "StopLimitOrder all rules" --staging shelly/fixMemorySplitter