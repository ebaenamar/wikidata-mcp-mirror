import time
import datetime
from typing import Dict, List, Optional, Any

class QuerySignal:
    def __init__(
        self,
        query_type: str,
        entities: List[str],
        temporal_constraints: Optional[Dict[str, Any]] = None,
        limit_constraints: Optional[int] = None,
        strength: float = 1.0,
        message: str = "",
        current_date: Optional[datetime.date] = None,
    ):
        self.id = f"query_{int(time.time())}_{query_type}"
        self.query_type = query_type
        self.entities = entities
        self.temporal_constraints = temporal_constraints or {}
        self.limit_constraints = limit_constraints
        self.strength = strength
        self.message = message
        self.timestamp_created = time.time()
        # Store the current date for temporal context
        self.current_date = current_date or datetime.date.today()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query_type": self.query_type,
            "entities": self.entities,
            "temporal_constraints": self.temporal_constraints,
            "limit_constraints": self.limit_constraints,
            "strength": self.strength,
            "message": self.message,
            "current_date": self.current_date.isoformat(),
            "timestamp_created": self.timestamp_created
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuerySignal':
        signal = cls(
            query_type=data["query_type"],
            entities=data["entities"],
            temporal_constraints=data.get("temporal_constraints"),
            limit_constraints=data.get("limit_constraints"),
            strength=data.get("strength", 1.0),
            message=data.get("message", "")
        )
        signal.id = data["id"]
        signal.timestamp_created = data["timestamp_created"]
        return signal
