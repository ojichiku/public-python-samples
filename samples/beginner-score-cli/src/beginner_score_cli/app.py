from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreSummary:
    average: float
    highest: int
    lowest: int
    grade: str
    count: int


def parse_scores(raw_value: str) -> list[int]:
    parts = [part.strip() for part in raw_value.split(",") if part.strip()]
    if not parts:
        raise ValueError("点数を1つ以上入力してください。")

    scores: list[int] = []
    for part in parts:
        score = int(part)
        if score < 0 or score > 100:
            raise ValueError("点数は0から100の範囲で入力してください。")
        scores.append(score)
    return scores


def calculate_summary(scores: list[int]) -> ScoreSummary:
    if not scores:
        raise ValueError("点数がありません。")

    average = sum(scores) / len(scores)
    highest = max(scores)
    lowest = min(scores)
    grade = choose_grade(average)
    return ScoreSummary(
        average=average,
        highest=highest,
        lowest=lowest,
        grade=grade,
        count=len(scores),
    )


def choose_grade(average: float) -> str:
    if average >= 90:
        return "S"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "E"


def build_report(name: str, summary: ScoreSummary) -> str:
    return (
        f"{name}さんの結果\n"
        f"科目数: {summary.count}\n"
        f"平均点: {summary.average:.1f}\n"
        f"最高点: {summary.highest}\n"
        f"最低点: {summary.lowest}\n"
        f"評価: {summary.grade}"
    )


def main() -> None:
    print("点数集計サンプル")
    name = input("名前を入力してください: ").strip() or "受講者"
    raw_scores = input("点数をカンマ区切りで入力してください (例: 80,75,92): ")

    try:
        scores = parse_scores(raw_scores)
        summary = calculate_summary(scores)
    except ValueError as exc:
        print(f"入力エラー: {exc}")
        return

    print()
    print(build_report(name, summary))
