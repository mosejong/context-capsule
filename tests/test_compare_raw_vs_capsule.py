from scripts.compare_raw_vs_capsule import max_pts, score, score_pts


def test_score_accepts_korean_synonyms_for_expected_keys():
    result = score(
        "정확도 98.08%이고, 재시도 로직과 배포 설정, 마이그레이션 파일을 확인했습니다.",
        {
            "98.08": True,
            "accuracy": True,
            "retry": True,
            "deploy": True,
            "migration": True,
        },
    )

    assert all(result.values())


def test_score_rewards_absent_wrong_answer():
    result = score(
        "정확도는 98.08%입니다. qa_defense 문서와 accuracy 값을 확인했습니다.",
        {"98.08": True, "qa_defense": True, "accuracy": True},
        wrong="98.6",
    )

    assert result["_wrong_answer"] is False
    assert score_pts(result) == 4
    assert max_pts(result) == 4


def test_score_does_not_reward_present_wrong_answer():
    result = score(
        "정확도 후보로 98.08%와 98.6%가 함께 보입니다.",
        {"98.08": True, "accuracy": True},
        wrong="98.6",
    )

    assert result["_wrong_answer"] is True
    assert score_pts(result) == 2
    assert max_pts(result) == 3
