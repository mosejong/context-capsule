from scripts.compare_raw_vs_capsule import score


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
