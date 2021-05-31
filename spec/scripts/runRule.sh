certoraRun spec/harness/StopLimitOrderHarness.sol spec/harness/SimpleBentoBox.sol spec/harness/SimpleOrderReceiver.sol \
    --verify StopLimitOrderHarness:spec/stopLimitOrder.spec \
    --link StopLimitOrderHarness:bentoBox=SimpleBentoBox \
    --link SimpleOrderReceiver:bentoBox=SimpleBentoBox \
    --settings -enableStorageAnalysis=true,-ignoreViewFunctions,-assumeUnwindCond,-patient=30,-rule=$1 ֿ\
    --msg "StopLimitOrder $1 $2"