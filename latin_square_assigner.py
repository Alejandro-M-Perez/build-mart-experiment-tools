"""
Latin Square Assigner
=====================

This script generates balanced assignments of experimental conditions for a
Latin‑square crossover design. When comparing three conditions (e.g.
Control, Human PM and AI PM) across a number of teams, a Latin square
ensures that each condition appears in each position (first, second,
third) equally often. This reduces bias due to learning or fatigue.

The script supports any number of teams that is a multiple of the number of
conditions. Teams are randomly assigned to Latin square rows. The output
associates each team with an ordered sequence of condition labels.

Usage::

    python latin_square_assigner.py --teams 10 --conditions Control HPM AIPM
"""

from __future__ import annotations

import argparse
import random
from typing import List, Dict


def latin_square(n: int) -> List[List[int]]:
    """Construct a simple Latin square of order ``n``.

    Returns a list of rows, where each row is a permutation of
    integers ``[0, n-1]``. The element at ``(i, j)`` is ``(i + j) mod n``.
    """
    return [[(i + j) % n for j in range(n)] for i in range(n)]


def assign_teams(num_teams: int, conditions: List[str]) -> Dict[str, List[str]]:
    """Assign teams to conditions using a Latin‑square design.

    Args:
        num_teams: Total number of teams. Must be a multiple of
            ``len(conditions)``.
        conditions: List of condition names.

    Returns:
        Mapping of team identifiers (e.g. ``Team 1``, ``Team 2``) to an ordered
        list of condition names.
    """
    k = len(conditions)
    if num_teams % k != 0:
        raise ValueError(
            f"Number of teams ({num_teams}) must be a multiple of the number of conditions ({k})."
        )

    square = latin_square(k)
    assignments: Dict[str, List[str]] = {}
    teams_per_square = num_teams // k
    team_indices = list(range(num_teams))
    random.shuffle(team_indices)

    for block in range(teams_per_square):
        for row_idx, row in enumerate(square):
            team_no = team_indices[block * k + row_idx]
            team_name = f"Team {team_no + 1}"
            assignments[team_name] = [conditions[col] for col in row]

    return assignments


def main() -> None:
    parser = argparse.ArgumentParser(description="Assign teams using a Latin square design.")
    parser.add_argument("--teams", type=int, required=True, help="Total number of teams")
    parser.add_argument(
        "--conditions", nargs="+", required=True, help="List of condition names (e.g. Control HPM AIPM)"
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    assignments = assign_teams(args.teams, args.conditions)
    for team, sequence in assignments.items():
        print(f"{team}: {', '.join(sequence)}")


if __name__ == "__main__":
    main()