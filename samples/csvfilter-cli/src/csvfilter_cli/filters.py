from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol


class Condition(Protocol):
    def matches(self, value: str) -> bool: ...


def _compile_regex(pattern: str) -> re.Pattern[str]:
    try:
        return re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"正規表現が不正です: {exc}") from exc


@dataclass(frozen=True)
class ContainsCondition:
    needle: str

    def matches(self, value: str) -> bool:
        return self.needle in value


@dataclass(frozen=True)
class RegexCondition:
    pattern: re.Pattern[str]

    def matches(self, value: str) -> bool:
        return bool(self.pattern.search(value))


def build_condition(operator: str, operand: str) -> Condition:
    op = operator.lower()
    if op == "contains":
        return ContainsCondition(operand)
    if op == "regex":
        return RegexCondition(_compile_regex(operand))
    raise ValueError(f"無効な演算子です: {operator}")


def all_conditions_match(value: str, conditions: list[Condition]) -> bool:
    for cond in conditions:
        if not cond.matches(value):
            return False
    return True
