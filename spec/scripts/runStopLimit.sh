certoraRun.py spec/harness/StopLimitOrderHarness.sol spec/harness/SimpleBentoBox.sol --verify StopLimitOrderHarness:spec/stopLimitOrder.spec --link StopLimitOrderHarness:bentoBox=SimpleBentoBox \
--msg "StopLimitOrderHarness" --staging