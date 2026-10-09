import json
import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal

from inspection import Decision, ExplanationFailure, Inspection, PolicySnapshot, explain, judge


class InspectionContractTest(unittest.TestCase):
    def setUp(self):
        self.policy = PolicySnapshot("0.50000000000000000001", "v1", "synthetic-model")

    def test_normal_below_threshold(self):
        self.assertEqual(judge("0.4", self.policy).decision, Decision.NORMAL)

    def test_defect_at_exact_threshold(self):
        self.assertEqual(judge(self.policy.threshold, self.policy).decision, Decision.DEFECT)

    def test_unknown_without_score(self):
        result = judge(None, self.policy)
        self.assertEqual(result.decision, Decision.UNKNOWN)
        self.assertIs(result.policy, self.policy)

    def test_successful_explanation_does_not_change_judgment(self):
        result = judge("0.6", self.policy)
        before = result.to_record()
        self.assertEqual(explain(result, lambda _: "Synthetic observation").status, "complete")
        self.assertEqual(result.to_record(), before)

    def test_failed_explanation_does_not_change_judgment(self):
        def fail(_):
            raise ExplanationFailure("synthetic failure")
        result = judge("0.6", self.policy)
        before = result.to_record()
        self.assertEqual(explain(result, fail).status, "fallback")
        self.assertEqual(result.to_record(), before)

    def test_empty_explanation_uses_fallback(self):
        result = judge("0.4", self.policy)
        self.assertEqual(explain(result, lambda _: "  ").status, "fallback")
        self.assertEqual(result.decision, Decision.NORMAL)

    def test_programming_error_is_not_hidden(self):
        def bug(_):
            raise RuntimeError("bug")
        with self.assertRaises(RuntimeError):
            explain(judge("0.4", self.policy), bug)

    def test_non_text_explanation_is_rejected(self):
        with self.assertRaises(TypeError):
            explain(judge("0.4", self.policy), lambda _: None)

    def test_inspection_and_snapshot_are_frozen(self):
        result = judge("0.6", self.policy)
        with self.assertRaises(FrozenInstanceError):
            result.decision = Decision.NORMAL
        with self.assertRaises(FrozenInstanceError):
            self.policy.threshold = Decimal("0.8")
        with self.assertRaises(TypeError):
            PolicySnapshot("0.5", {"mutable": "version"}, "model")
        with self.assertRaises(ValueError):
            PolicySnapshot("0.5", " ", "model")

    def test_precision_survives_json_round_trip(self):
        result = judge("0.50000000000000000002", self.policy)
        loaded = Inspection.from_record(json.loads(json.dumps(result.to_record())))
        self.assertEqual(loaded, result)
        self.assertEqual(str(loaded.policy.threshold), "0.50000000000000000001")

    def test_old_result_keeps_policy_after_new_configuration(self):
        old = judge("0.6", self.policy)
        new_policy = PolicySnapshot("0.9", "v2", "new-synthetic-model")
        self.assertEqual(judge("0.6", new_policy).decision, Decision.NORMAL)
        self.assertEqual(old.decision, Decision.DEFECT)
        self.assertEqual(old.policy.policy_version, "v1")

    def test_serialized_record_cannot_mutate_snapshot(self):
        result = judge("0.6", self.policy)
        record = result.to_record()
        record["policy"]["threshold"] = "0.9"
        self.assertEqual(str(result.policy.threshold), "0.50000000000000000001")

    def test_legacy_record_without_policy(self):
        loaded = Inspection.from_record({"decision": "normal", "score": "0.1"})
        self.assertIsNone(loaded.policy)
        self.assertEqual(loaded.decision, Decision.NORMAL)
        self.assertIsNone(loaded.to_record()["policy"])

    def test_legacy_null_policy_and_missing_score(self):
        loaded = Inspection.from_record({"decision": "unknown", "policy": None})
        self.assertIsNone(loaded.score)
        self.assertIsNone(loaded.policy)

    def test_legacy_explanation_does_not_invent_lineage(self):
        loaded = Inspection.from_record({"decision": "normal", "score": "0.1"})
        explain(loaded, lambda _: "Synthetic legacy explanation")
        self.assertIsNone(loaded.policy)

    def test_float_is_rejected_to_avoid_implicit_precision_loss(self):
        with self.assertRaises(TypeError):
            judge(0.6, self.policy)
        with self.assertRaises(TypeError):
            PolicySnapshot(0.5, "v1", "model")

    def test_nonfinite_and_out_of_range_inputs_are_rejected(self):
        for score in ("NaN", "Infinity", "-0.1", "1.1"):
            with self.subTest(score=score), self.assertRaises(ValueError):
                judge(score, self.policy)
        with self.assertRaises(ValueError):
            PolicySnapshot("1.1", "v1", "model")

    def test_invalid_historical_decision_is_not_silently_coerced(self):
        with self.assertRaises(ValueError):
            Inspection.from_record({"decision": "unrecognized"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
