import susy_v53_intermediate_referee_verification as referee


def test_independent_referee_verification() -> None:
    assert referee.main() == 0
