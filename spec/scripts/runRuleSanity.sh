certoraRun spec/harness/StopLimitOrderHarness.sol spec/harness/SimpleBentoBox.sol spec/harness/SimpleOrderReceiver.sol \
    --solc solc6.12 \
    --verify StopLimitOrderHarness:spec/stopLimitOrder.spec \
    --link StopLimitOrderHarness:bentoBox=SimpleBentoBox \
    --link SimpleOrderReceiver:bentoBox=SimpleBentoBox \
    --settings -ruleSanityChecks,-enableStorageAnalysis=true,-ignoreViewFunctions,-assumeUnwindCond,-patient=30,-rule=$1 \
    --staging --msg "StopLimitOrder Sanity $1 $2"