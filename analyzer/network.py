# analyzer/network.py
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import Relationship, Alert

RELATION_SCORES = {
    "board": 20,
    "lawyer": 15,
    "school": 10,
    "family": 10,
}


class NetworkAnalyzer:
    """Scores a trader-company pair based on relationship graph."""

    def compute_score(self, session: Session, trader_id: int, company_id: int) -> float:
        rels = session.execute(
            select(Relationship).where(
                (Relationship.trader_a_id == trader_id) |
                (Relationship.trader_b_id == trader_id)
            )
        ).scalars().all()

        score = 0.0
        for rel in rels:
            score += RELATION_SCORES.get(rel.relation_type, 0)

        # Repeat offender bonus
        prior_alerts = session.execute(
            select(Alert).where(Alert.trader_id == trader_id)
        ).scalars().all()
        if len(prior_alerts) >= 2:
            score += 15

        return min(50.0, round(score, 2))
