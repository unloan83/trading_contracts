from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NO_TRADE = "NO_TRADE"


class MarketRegime(str, Enum):
    TRENDING = "TRENDING"
    RANGE_BOUND = "RANGE_BOUND"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_LIQUIDITY = "LOW_LIQUIDITY"


class MarketState(BaseModel):
    model_config = ConfigDict(frozen=True)

    instrument_id: str
    exchange: str = "NSE"
    event_time: datetime
    received_time: datetime
    price: float
    volume: float
    spread: Optional[float] = None
    oi: Optional[float] = None
    oi_change: Optional[float] = None
    vwap: Optional[float] = None
    cpr_state: Optional[str] = None
    data_quality: str = "VALID"
    session_id: str


class SignalCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    signal_id: str
    instrument_id: str
    created_at: datetime
    valid_until: datetime
    direction: Direction
    setup_type: str
    regime: MarketRegime
    confidence: float = Field(ge=0.0, le=1.0)
    entry_trigger: Optional[float] = None
    invalidation_level: Optional[float] = None
    expected_holding_minutes: int = 15
    expected_edge_bps: Optional[float] = None
    reason_codes: List[str]
    slippage_bps_per_side: Optional[float] = Field(default=None, ge=0.0)
    cohort: str = "STANDARD"
    feature_version: str = "v1.0"
    data_quality: str = "VALID"


class RiskDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision_id: str
    signal_id: str
    approved: bool
    max_position_size: int = 0
    allocated_risk_bps: float = 0.0
    rejected_reason: Optional[str] = None
    evaluated_at: datetime
