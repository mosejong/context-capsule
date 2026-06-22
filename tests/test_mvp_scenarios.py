from scripts.validate_mvp import run_validation, scenarios


def test_mvp_validation_scenarios():
    results = run_validation(repeat=1)

    assert len(results) == len(scenarios())
    assert all("ok" in result for result in results)
