"""Independent contract example using synthetic scores and in-memory records."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable


def exact_decimal(value: str | Decimal) -> Decimal:
    if not isinstance(value, (str, Decimal)):
        raise TypeError("Use a decimal string or Decimal, never a float")
    result = Decimal(value)
    if not result.is_finite():
        raise ValueError("Finite value required")
    return result


class Decision(str, Enum):
    NORMAL = "normal"
    DEFECT = "defect"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PolicySnapshot:
    threshold: Decimal
    policy_version: str
    model_version: str

    def __post_init__(self):
        value = exact_decimal(self.threshold)
        if value < 0 or value > 1:
            raise ValueError("Threshold must be in [0, 1]")
        if not isinstance(self.policy_version, str) or not isinstance(self.model_version, str):
            raise TypeError("Versions must be immutable strings")
        if not self.policy_version.strip() or not self.model_version.strip():
            raise ValueError("Versions required")
        object.__setattr__(self, "threshold", value)

    def to_record(self) -> dict:
        return {
            "threshold": str(self.threshold),
            "policy_version": self.policy_version,
            "model_version": self.model_version,
        }

    @classmethod
    def from_record(cls, record: dict):
        return cls(exact_decimal(record["threshold"]), record["policy_version"], record["model_version"])


@dataclass(frozen=True)
class Inspection:
    decision: Decision
    score: Decimal | None
    policy: PolicySnapshot | None

    def to_record(self) -> dict:
        return {
            "decision": self.decision.value,
            "score": str(self.score) if self.score is not None else None,
            "policy": self.policy.to_record() if self.policy is not None else None,
        }

    @classmethod
    def from_record(cls, record: dict):
        # Missing lineage is supported; do not invent a historical policy.
        snapshot = record.get("policy")
        raw_score = record.get("score")
        return cls(
            Decision(record["decision"]),
            exact_decimal(raw_score) if raw_score is not None else None,
            PolicySnapshot.from_record(snapshot) if snapshot is not None else None,
        )


@dataclass(frozen=True)
class Explanation:
    status: str
    text: str


class ExplanationFailure(Exception):
    """Declared explanation failure; programming errors remain visible."""


def judge(score: str | Decimal | None, policy: PolicySnapshot) -> Inspection:
    if score is None:
        return Inspection(Decision.UNKNOWN, None, policy)
    value = exact_decimal(score)
    if value < 0 or value > 1:
        raise ValueError("Synthetic score must be in [0, 1]")
    decision = Decision.DEFECT if value >= policy.threshold else Decision.NORMAL
    return Inspection(decision, value, policy)


def explain(inspection: Inspection, explainer: Callable[[Inspection], str]) -> Explanation:
    try:
        text = explainer(inspection)
        if not isinstance(text, str):
            raise TypeError("Explanation must be text")
        if not text.strip():
            raise ExplanationFailure("Empty explanation")
        return Explanation("complete", text)
    except ExplanationFailure:
        # No judgment fields are returned or overwritten by this stage.
        return Explanation("fallback", "Explanation unavailable; human review required")
