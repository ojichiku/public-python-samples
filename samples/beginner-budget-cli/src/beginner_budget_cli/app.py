from dataclasses import dataclass


@dataclass(frozen=True)
class BudgetSummary:
    budget: int
    total_spent: int
    remaining: int
    count: int
    status: str


def parse_amounts(raw_value: str) -> list[int]:
    parts = [part.strip() for part in raw_value.split(",") if part.strip()]
    if not parts:
        raise ValueError("Enter at least one expense.")

    amounts: list[int] = []
    for part in parts:
        amount = int(part)
        if amount < 0:
            raise ValueError("Expenses must be 0 or greater.")
        amounts.append(amount)
    return amounts


def calculate_budget(budget: int, amounts: list[int]) -> BudgetSummary:
    if budget < 0:
        raise ValueError("Budget must be 0 or greater.")
    if not amounts:
        raise ValueError("No expenses were provided.")

    total_spent = sum(amounts)
    remaining = budget - total_spent
    status = choose_status(remaining, budget)
    return BudgetSummary(
        budget=budget,
        total_spent=total_spent,
        remaining=remaining,
        count=len(amounts),
        status=status,
    )


def choose_status(remaining: int, budget: int) -> str:
    if remaining < 0:
        return "Over budget"
    if budget == 0:
        return "No spending"
    if remaining > budget * 0.3:
        return "Comfortable"
    return "Watch spending"


def build_report(summary: BudgetSummary) -> str:
    return (
        "Budget Report\n"
        f"Expense count: {summary.count}\n"
        f"Total spent: {summary.total_spent} yen\n"
        f"Remaining: {summary.remaining} yen\n"
        f"Status: {summary.status}"
    )


def main() -> None:
    print("Simple Budget Check")

    try:
        budget = int(input("Enter your monthly budget: ").strip())
        raw_amounts = input(
            "Enter expenses separated by commas (example: 1200,850,3000): "
        )
        amounts = parse_amounts(raw_amounts)
        summary = calculate_budget(budget, amounts)
    except ValueError as exc:
        print(f"Input error: {exc}")
        return

    print()
    print(build_report(summary))
