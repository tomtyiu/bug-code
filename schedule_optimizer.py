from dataclasses import dataclass
from itertools import combinations
from typing import Iterable


@dataclass(frozen=True)
class Task:
    name: str
    category: str
    duration: int
    value: int


@dataclass(frozen=True)
class Plan:
    value: int = 0
    duration: int = 0
    tasks: tuple[Task, ...] = ()


def better_plan(first: Plan, second: Plan) -> Plan:
    """Prefer higher value, then shorter duration."""
    first_score = (first.value, -first.duration)
    second_score = (second.value, -second.duration)
    return first if first_score >= second_score else second


def optimize_schedule(tasks: Iterable[Task], budget: int) -> Plan:
    """
    Select tasks while preserving their original order.

    Rules:
    - Total duration must not exceed the budget.
    - Consecutive selected tasks must have different categories.
    """
    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    items = tuple(tasks)

    if any(task.duration <= 0 for task in items):
        raise ValueError("Task durations must be positive.")

    memo: dict[tuple[int, int], Plan] = {}

    def search(
        index: int,
        remaining: int,
        previous_category: str | None,
    ) -> Plan:
        if index >= len(items) or remaining == 0:
            return Plan()

        key = (index, remaining)
        if key in memo:
            return memo[key]

        task = items[index]
        best = search(index + 1, remaining, previous_category)

        if (
            task.duration <= remaining
            and task.category != previous_category
        ):
            tail = search(
                index + 1,
                remaining - task.duration,
                task.category,
            )

            candidate = Plan(
                value=task.value + tail.value,
                duration=task.duration + tail.duration,
                tasks=(task,) + tail.tasks,
            )
            best = better_plan(best, candidate)

        memo[key] = best
        return best

    return search(0, budget, None)


def validate_plan(plan: Plan, budget: int) -> bool:
    within_budget = plan.duration <= budget
    correct_duration = plan.duration == sum(
        task.duration for task in plan.tasks
    )
    correct_value = plan.value == sum(
        task.value for task in plan.tasks
    )
    alternating = all(
        left.category != right.category
        for left, right in zip(plan.tasks, plan.tasks[1:])
    )
    return all((
        within_budget,
        correct_duration,
        correct_value,
        alternating,
    ))


def exhaustive_reference(tasks: list[Task], budget: int) -> Plan:
    """Slow reference implementation for small inputs."""
    best = Plan()

    for size in range(len(tasks) + 1):
        for selected in combinations(tasks, size):
            candidate = Plan(
                value=sum(task.value for task in selected),
                duration=sum(task.duration for task in selected),
                tasks=selected,
            )

            if validate_plan(candidate, budget):
                best = better_plan(best, candidate)

    return best


def main() -> None:
    tasks = [
        Task("Index documents", "compute", 2, 8),
        Task("Fetch updates", "network", 2, 7),
        Task("Build embeddings", "compute", 2, 10),
        Task("Upload archive", "network", 3, 9),
        Task("Generate report", "compute", 1, 4),
    ]
    budget = 5
    plan = optimize_schedule(tasks, budget)

    print("Selected tasks:")
    for task in plan.tasks:
        print(f"  {task.name}: {task.duration}h, value={task.value}")

    print(f"\nTotal duration: {plan.duration}/{budget}h")
    print(f"Total value: {plan.value}")
    print(f"Plan passes validation: {validate_plan(plan, budget)}")

    # Enable this comparison when investigating:
    # reference = exhaustive_reference(tasks, budget)
    # print(f"Reference value: {reference.value}")


if __name__ == "__main__":
    main()
