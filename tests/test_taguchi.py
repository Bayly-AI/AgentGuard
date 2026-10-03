"""Unit tests for Taguchi Robust Design and Orthogonal Array Testing in AgentGuard."""

import unittest

from agentguard.governance.taguchi import (
    ArrayType,
    Factor,
    SNRType,
    TaguchiEngine,
    TaguchiLossFunction,
    calculate_snr,
)


class TestTaguchiMethods(unittest.TestCase):
    def test_snr_smaller_is_better(self):
        responses = [10.0, 12.0, 8.0, 11.0]
        snr = calculate_snr(responses, snr_type=SNRType.SMALLER_THE_BETTER)
        self.assertIsInstance(snr, float)
        self.assertLess(snr, 0.0)  # Negative dB for mean sq > 1

    def test_snr_larger_is_better(self):
        responses = [90.0, 95.0, 88.0, 92.0]
        snr = calculate_snr(responses, snr_type=SNRType.LARGER_THE_BETTER)
        self.assertIsInstance(snr, float)
        self.assertGreater(snr, 35.0)

    def test_snr_nominal_the_best(self):
        responses = [10.0, 10.1, 9.9, 10.0]
        snr = calculate_snr(responses, snr_type=SNRType.NOMINAL_THE_BEST)
        self.assertIsInstance(snr, float)
        self.assertGreater(snr, 40.0)

    def test_quality_loss_function(self):
        loss_fn = TaguchiLossFunction(target=100.0, cost_at_tolerance=50.0, tolerance=5.0)
        self.assertEqual(loss_fn.k, 2.0)
        
        # At target, loss is $0
        self.assertEqual(loss_fn.calculate_loss(100.0), 0.0)
        # At target + 5, loss is $50
        self.assertEqual(loss_fn.calculate_loss(105.0), 50.0)
        # Average loss over [98, 102]
        avg_loss = loss_fn.calculate_average_loss([98.0, 102.0])
        self.assertEqual(avg_loss, 8.0)

    def test_generate_l9_matrix(self):
        factors = [
            Factor(name="temperature", levels=["low", "med", "high"]),
            Factor(name="pressure", levels=[10, 20, 30]),
            Factor(name="time", levels=[60, 120, 180]),
        ]
        runs = TaguchiEngine.generate_matrix(ArrayType.L9, factors)
        self.assertEqual(len(runs), 9)
        self.assertIn("temperature", runs[0])
        self.assertIn("pressure", runs[0])
        self.assertIn("time", runs[0])

    def test_taguchi_anova_analysis(self):
        factors = [
            Factor(name="temp", levels=["L1", "L2", "L3"]),
            Factor(name="press", levels=[1, 2, 3]),
        ]
        # Simulate 9 experimental runs with 3 replicates each
        responses = [
            [12.0, 13.0, 11.5],
            [15.0, 14.5, 16.0],
            [18.0, 17.5, 19.0],
            [10.0, 10.5, 11.0],
            [14.0, 13.5, 14.2],
            [16.0, 16.5, 15.8],
            [9.0, 9.5, 9.2],
            [13.0, 12.8, 13.4],
            [15.0, 15.2, 14.8],
        ]
        res = TaguchiEngine.analyze(
            array_type=ArrayType.L9,
            factors=factors,
            responses=responses,
            snr_type=SNRType.SMALLER_THE_BETTER,
        )
        self.assertEqual(len(res.snr_values), 9)
        self.assertIn("temp", res.optimal_levels)
        self.assertIn("press", res.optimal_levels)


if __name__ == "__main__":
    unittest.main()
