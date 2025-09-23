# extractor/extract_states.py
"""
Extract states from database where total_rto != 0
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from db.session import SessionLocal
from db.models import State

logger = logging.getLogger("app.extractor.states")


@dataclass
class StateData:
    """Represents a state with RTO data"""
    id: int
    name: str
    code: str
    total_rto: int


class StateExtractor:
    """Extracts active states from database"""
    
    def __init__(self):
        self.states = []
    
    def extract_active_states(self) -> List[StateData]:
        """Extract states where total_rto != 0"""
        try:
            with SessionLocal() as db:
                states = db.query(State).filter(
                    State.total_rto != 0
                ).order_by(State.name).all()
                
                self.states = [
                    StateData(
                        id=state.id,
                        name=state.name,
                        code=state.code,
                        total_rto=state.total_rto
                    )
                    for state in states
                ]
                
                logger.info(f"Extracted {len(self.states)} active states")
                return self.states
                
        except Exception as e:
            logger.error(f"Failed to extract states: {e}")
            return []
    
    def get_state_by_code(self, code: str) -> Optional[StateData]:
        """Get state by code"""
        if not self.states:
            self.extract_active_states()
            
        for state in self.states:
            if state.code == code:
                return state
        return None
    
    def get_state_by_id(self, state_id: int) -> Optional[StateData]:
        """Get state by ID"""
        if not self.states:
            self.extract_active_states()
            
        for state in self.states:
            if state.id == state_id:
                return state
        return None
    
    def get_states_dict(self) -> Dict[str, StateData]:
        """Get states as dictionary with code as key"""
        if not self.states:
            self.extract_active_states()
            
        return {state.code: state for state in self.states}
    
    def get_state_count(self) -> int:
        """Get total count of active states"""
        if not self.states:
            self.extract_active_states()
        return len(self.states)
    
    def refresh_states(self) -> List[StateData]:
        """Force refresh states from database"""
        self.states = []
        return self.extract_active_states()


def main():
    """CLI interface for state extraction"""
    extractor = StateExtractor()
    states = extractor.extract_active_states()
    
    print(f"\n=== Active States ({len(states)}) ===")
    """ these number are used for column width , so that printed table is clean"""
    print(f"{'ID':<5} {'Code':<10} {'Name':<30} {'RTOs':<8}")      
    print("-" * 55)
    
    for state in states:
        print(f"{state.id:<5} {state.code:<10} {state.name:<30} {state.total_rto:<8}")


if __name__ == "__main__":
    main()