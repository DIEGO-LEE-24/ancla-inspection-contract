from inspection import ExplanationFailure, PolicySnapshot, explain, judge


def unavailable(_inspection):
    raise ExplanationFailure("synthetic failure")


snapshot = PolicySnapshot("0.50000000000000000001", "policy-demo", "model-demo")
result = judge("0.6", snapshot)
print("judgment:", result.to_record())
print("explanation:", explain(result, unavailable))
print("judgment_after:", result.to_record())
