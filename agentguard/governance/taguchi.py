"""Taguchi Methods for Robust Design, Orthogonal Array Testing, and Quality Loss in AgentGuard.

Provides standard Orthogonal Arrays (L4, L8, L9, L12, L18), factor-to-matrix mapping,
Signal-to-Noise Ratio (SNR) evaluation, and Taguchi Quality Loss modeling.
Zero external scientific dependencies (pure Python standard library).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


class ArrayType(str, Enum):
    """Standard Taguchi Orthogonal Arrays."""

    L4 = "L4"      # L4(2^3): 4 runs, up to 3 factors at 2 levels
    L8 = "L8"      # L8(2^7): 8 runs, up to 7 factors at 2 levels
    L9 = "L9"      # L9(3^4): 9 runs, up to 4 factors at 3 levels
    L12 = "L12"    # L12(2^11): 12 runs, up to 11 factors at 2 levels
    L18 = "L18"    # L18(2^1 x 3^7): 18 runs, 1 factor at 2 levels, 7 factors at 3 levels


class SNRType(str, Enum):
    """Signal-to-Noise Ratio objective types."""

    SMALLER_THE_BETTER = "smaller_the_better"  # Minimize latency, cost, error rate
    LARGER_THE_BETTER = "larger_the_better"    # Maximize accuracy, eval score, throughput
    NOMINAL_THE_BEST = "nominal_the_best"      # Match target nominal value with minimal variance


# Standard Orthogonal Array definition tables (0-indexed integer levels)
_ORTHOGONAL_ARRAYS: Dict[ArrayType, Dict[str, Any]] = {
    ArrayType.L4: {
        "runs": 4,
        "capacities": [2, 2, 2],
        "matrix": [
            [0, 0, 0],
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0],
        ],
    },
    ArrayType.L8: {
        "runs": 8,
        "capacities": [2, 2, 2, 2, 2, 2, 2],
        "matrix": [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1],
            [0, 1, 1, 0, 0, 1, 1],
            [0, 1, 1, 1, 1, 0, 0],
            [1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 0],
            [1, 1, 0, 0, 1, 1, 0],
            [1, 1, 0, 1, 0, 0, 1],
        ],
    },
    ArrayType.L9: {
        "runs": 9,
        "capacities": [3, 3, 3, 3],
        "matrix": [
            [0, 0, 0, 0],
            [0, 1, 1, 1],
            [0, 2, 2, 2],
            [1, 0, 1, 2],
            [1, 1, 2, 0],
            [1, 2, 0, 1],
            [2, 0, 2, 1],
            [2, 1, 0, 2],
            [2, 2, 1, 0],
        ],
    },
    ArrayType.L12: {
        "runs": 12,
        "capacities": [2] * 11,
        "matrix": [
            [1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0],
            [0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0],
            [0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1],
            [1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1],
            [1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0],
            [0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1],
            [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
    },
    ArrayType.L18: {
        "runs": 18,
        "capacities": [2, 3, 3, 3, 3, 3, 3, 3],
        "matrix": [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1],
            [0, 0, 2, 2, 2, 2, 2, 2],
            [0, 1, 0, 0, 1, 1, 2, 2],
            [0, 1, 1, 1, 2, 2, 0, 0],
            [0, 1, 2, 2, 0, 0, 1, 1],
            [0, 2, 0, 1, 0, 2, 1, 2],
            [0, 2, 1, 2, 1, 0, 2, 0],
            [0, 2, 2, 0, 2, 1, 0, 1],
            [1, 0, 0, 2, 2, 1, 1, 0],
            [1, 0, 1, 0, 0, 2, 2, 1],
            [1, 0, 2, 1, 1, 0, 0, 2],
            [1, 1, 0, 1, 2, 0, 2, 1],
            [1, 1, 1, 2, 0, 1, 0, 2],
            [1, 1, 2, 0, 1, 2, 1, 0],
            [1, 2, 0, 2, 1, 1, 0, 1],
            [1, 2, 1, 0, 2, 2, 1, 0],
            [1, 2, 2, 1, 0, 0, 2, 2],
        ],
    },
}


@dataclass
class Factor:
    """Experimental Factor definition."""

    name: str
    levels: List[Any]

    def __post_init__(self) -> None:
        if not self.levels:
            raise ValueError(f"Factor '{self.name}' must have at least one level.")


@dataclass
class TaguchiAnalysisResult:
    """Summary of Taguchi Design of Experiments evaluation."""

    array_type: ArrayType
    snr_type: SNRType
    factors: List[Factor]
    experiment_runs: List[Dict[str, Any]]
    responses: List[Sequence[float]]
    snr_values: List[float]
    mean_responses: List[float]
    main_effects_snr: Dict[str, Dict[Any, float]]
    optimal_levels: Dict[str, Any]


@dataclass
class TaguchiLossFunction:
    """Taguchi Quality Loss Function evaluator: L(y) = k * (y - m)^2."""

    target: float
    cost_at_tolerance: float
    tolerance: float

    @property
    def k(self) -> float:
        if self.tolerance == 0:
            raise ValueError("Tolerance cannot be zero.")
        return self.cost_at_tolerance / (self.tolerance ** 2)

    def calculate_loss(self, measured_value: float) -> float:
        """Calculate loss for a single measured value."""
        return self.k * ((measured_value - self.target) ** 2)

    def calculate_average_loss(self, values: Sequence[float]) -> float:
        """Calculate average Quality Loss over a set of measured values."""
        if not values:
            return 0.0
        return sum(self.calculate_loss(v) for v in values) / len(values)


def calculate_snr(
    responses: Sequence[float],
    snr_type: SNRType = SNRType.SMALLER_THE_BETTER,
    target: float = 0.0,
) -> float:
    """Calculate Taguchi Signal-to-Noise Ratio (SNR) in decibels (dB)."""
    if not responses:
        raise ValueError("Responses list cannot be empty.")

    n = len(responses)

    if snr_type == SNRType.SMALLER_THE_BETTER:
        sum_sq = sum(y ** 2 for y in responses)
        mean_sq = sum_sq / n
        if mean_sq <= 0:
            return 100.0
        return -10.0 * math.log10(mean_sq)

    elif snr_type == SNRType.LARGER_THE_BETTER:
        sum_sq = sum(1.0 / (y ** 2) for y in responses if y != 0)
        mean_sq = sum_sq / n if n > 0 else 1e-12
        if mean_sq <= 0:
            return 100.0
        return -10.0 * math.log10(mean_sq)

    elif snr_type == SNRType.NOMINAL_THE_BEST:
        mean = sum(responses) / n
        variance = sum((y - mean) ** 2 for y in responses) / (n - 1) if n > 1 else 0.0
        if variance <= 0:
            return 100.0
        return 10.0 * math.log10((mean ** 2) / variance)

    raise ValueError(f"Unsupported SNRType: {snr_type}")


class TaguchiEngine:
    """Core Taguchi Orthogonal Array generator and analysis engine."""

    @staticmethod
    def generate_matrix(
        array_type: ArrayType,
        factors: List[Factor],
    ) -> List[Dict[str, Any]]:
        """Map experimental factors to a Taguchi Orthogonal Array matrix."""
        if array_type not in _ORTHOGONAL_ARRAYS:
            raise ValueError(f"Unsupported ArrayType: {array_type}")

        oa_info = _ORTHOGONAL_ARRAYS[array_type]
        capacities = oa_info["capacities"]
        matrix = oa_info["matrix"]

        if len(factors) > len(capacities):
            raise ValueError(
                f"ArrayType {array_type.value} supports at most {len(capacities)} factors, "
                f"but {len(factors)} were provided."
            )

        # Validate level count against capacities
        for i, factor in enumerate(factors):
            max_levels = capacities[i]
            if len(factor.levels) > max_levels:
                raise ValueError(
                    f"Factor '{factor.name}' has {len(factor.levels)} levels, but column {i} "
                    f"in {array_type.value} supports at most {max_levels} levels."
                )

        runs: List[Dict[str, Any]] = []
        for run_id, row in enumerate(matrix, start=1):
            run_dict: Dict[str, Any] = {"run_id": run_id}
            for col_idx, factor in enumerate(factors):
                raw_level_idx = row[col_idx]
                # Map raw level index safely to factor levels
                mapped_val = factor.levels[raw_level_idx % len(factor.levels)]
                run_dict[factor.name] = mapped_val
            runs.append(run_dict)

        return runs

    @staticmethod
    def analyze(
        array_type: ArrayType,
        factors: List[Factor],
        responses: List[Sequence[float]],
        snr_type: SNRType = SNRType.SMALLER_THE_BETTER,
    ) -> TaguchiAnalysisResult:
        """Perform Taguchi ANOVA / Main Effects analysis on experimental results."""
        runs = TaguchiEngine.generate_matrix(array_type, factors)

        if len(responses) != len(runs):
            raise ValueError(
                f"Expected {len(runs)} response sets for {array_type.value}, but got {len(responses)}."
            )

        snr_values: List[float] = []
        mean_responses: List[float] = []

        for resp in responses:
            snr = calculate_snr(resp, snr_type=snr_type)
            snr_values.append(snr)
            mean_responses.append(sum(resp) / len(resp) if resp else 0.0)

        # Calculate Main Effects for SNR
        main_effects_snr: Dict[str, Dict[Any, float]] = {}
        optimal_levels: Dict[str, Any] = {}

        for factor in factors:
            factor_name = factor.name
            level_snr_sums: Dict[Any, float] = {lvl: 0.0 for lvl in factor.levels}
            level_counts: Dict[Any, int] = {lvl: 0 for lvl in factor.levels}

            for run_dict, snr in zip(runs, snr_values):
                val = run_dict[factor_name]
                level_snr_sums[val] += snr
                level_counts[val] += 1

            # Average SNR per level
            level_snr_means: Dict[Any, float] = {}
            for lvl in factor.levels:
                cnt = level_counts[lvl]
                level_snr_means[lvl] = level_snr_sums[lvl] / cnt if cnt > 0 else 0.0

            main_effects_snr[factor_name] = level_snr_means

            # Select level with highest SNR
            best_level = max(level_snr_means.items(), key=lambda item: item[1])[0]
            optimal_levels[factor_name] = best_level

        return TaguchiAnalysisResult(
            array_type=array_type,
            snr_type=snr_type,
            factors=factors,
            experiment_runs=runs,
            responses=responses,
            snr_values=snr_values,
            mean_responses=mean_responses,
            main_effects_snr=main_effects_snr,
            optimal_levels=optimal_levels,
        )
