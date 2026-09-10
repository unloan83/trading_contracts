from datetime import datetime, timezone
import unittest
from pydantic import ValidationError
from trading_contracts.schemas.v1 import (
    Direction,
    MarketRegime,
    MarketState,
    SignalCandidate,
    RiskDecision,
)


class TestSchemas(unittest.TestCase):
    def test_market_state_immutable(self):
        now = datetime.now(timezone.utc)
        state = MarketState(
            instrument_id="RELIANCE",
            event_time=now,
            received_time=now,
            price=2500.0,
            volume=1000.0,
            session_id="SESS1",
        )
        self.assertEqual(state.instrument_id, "RELIANCE")
        with self.assertRaises(ValidationError):
            state.price = 2600.0  # Immutable / frozen

    def test_signal_candidate_serialization(self):
        now = datetime.now(timezone.utc)
        signal = SignalCandidate(
            signal_id="sig-123",
            instrument_id="TCS",
            created_at=now,
            valid_until=now,
            direction=Direction.LONG,
            setup_type="CPR_OI",
            regime=MarketRegime.TRENDING,
            confidence=0.85,
            reason_codes=["CPR_ABOVE_TC", "OI_LONG_BUILDUP"],
        )
        json_data = signal.model_dump_json()
        deserialized = SignalCandidate.model_validate_json(json_data)
        self.assertEqual(deserialized.signal_id, "sig-123")
        self.assertEqual(deserialized.direction, Direction.LONG)
        self.assertEqual(deserialized.confidence, 0.85)

    def test_confidence_validation(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError):
            SignalCandidate(
                signal_id="sig-999",
                instrument_id="INFY",
                created_at=now,
                valid_until=now,
                direction=Direction.SHORT,
                setup_type="CPR_OI",
                regime=MarketRegime.RANGE_BOUND,
                confidence=1.5,  # Out of range 0.0 - 1.0
                reason_codes=[],
            )


if __name__ == "__main__":
    unittest.main()
