# tests/test_network.py
from analyzer.network import NetworkAnalyzer
from db.database import Relationship


def test_network_score_board_member(session, sample_trader, sample_company):
    rel = Relationship(
        trader_a_id=sample_trader.id,
        trader_b_id=sample_company.id,
        relation_type="board",
        source="sec",
    )
    session.add(rel)
    session.commit()
    analyzer = NetworkAnalyzer()
    score = analyzer.compute_score(session, sample_trader.id, sample_company.id)
    assert score >= 20


def test_network_score_no_relationship(session, sample_trader, sample_company):
    analyzer = NetworkAnalyzer()
    score = analyzer.compute_score(session, sample_trader.id, sample_company.id)
    assert score == 0


def test_network_score_capped_at_50(session, sample_trader, sample_company):
    for rel_type in ["board", "lawyer", "school"]:
        rel = Relationship(
            trader_a_id=sample_trader.id,
            trader_b_id=sample_company.id,
            relation_type=rel_type,
            source="test",
        )
        session.add(rel)
    session.commit()
    analyzer = NetworkAnalyzer()
    score = analyzer.compute_score(session, sample_trader.id, sample_company.id)
    assert score <= 50
