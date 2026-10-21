"""Check threshold predictions against direct expected payoffs."""
import pytest
from src.auction import MAIN, outcome, trust_threshold
from final_sensitivity import sensitivity_rows


@pytest.mark.parametrize('baseline', [0.0, 0.25, 0.5])
def test_threshold_matches_direct_best_reply(baseline):
    t = trust_threshold(MAIN, baseline)
    for dt, high_should_win in [(-0.01, False), (0.01, True)]:
        q = baseline + (1 - baseline) * (t + dt)
        def expected(action):
            return (1-q)*outcome(MAIN, action, 'Low')['u1'] + q*outcome(MAIN, action, 'High')['u1']
        assert (expected('High') > expected('Low')) is high_should_win


def test_report_checks_equal_payoffs_and_evidence_status():
    rows = sensitivity_rows()
    assert [r['threshold_fraction'] for r in rows] == ['2/3', '5/9', '1/3']
    assert all(abs(r['low_payoff'] - r['high_payoff']) < 1e-12 for r in rows)
    assert all(r['evidence_status'] == 'exact model calculation' for r in rows)
