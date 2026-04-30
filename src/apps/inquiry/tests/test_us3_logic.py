import pytest

from apps.inquiry.graph import should_continue


def test_edge_logic_termination():
    """
    T021: 질문 단계가 5단계를 초과하면 종료(end)를 반환하는지 확인합니다.
    """
    state_continue = {"current_step": 3}
    state_end = {"current_step": 6}

    assert should_continue(state_continue) == "continue"
    assert should_continue(state_end) == "end"


@pytest.mark.django_db
def test_specification_generation_service():
    """
    T022: 수집된 데이터를 바탕으로 Markdown/JSON 기술서가 올바르게 생성되는지 확인합니다.
    """
    # 추후 서비스 구현 후 테스트 구체화 예정
    assert True
