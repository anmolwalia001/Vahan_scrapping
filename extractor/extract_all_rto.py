# extractor/extract_all_rto.py
"""
Extract all RTOs from database with state matching
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from db.session import SessionLocal
from db.models import RTO, State

logger = logging.getLogger("app.extractor.rto")


@dataclass
class RTOData:
    """Represents an RTO with state information"""
    id: int
    state_id: int
    state_name: str
    state_code: str
    name: str
    code: str
    value: Optional[str]
    full_text: Optional[str]
    is_active: bool


class RTOExtractor:
    """Extracts RTOs from database with state matching"""
    
    def __init__(self):
        self.rtos = []
        self.rtos_by_state = {}
    
    def extract_all_rtos(self, active_only: bool = True, states_with_rtos_only: bool = True) -> List[RTOData]:
        """Extract all RTOs with state information"""
        try:
            with SessionLocal() as db:
                # Build query with join
                query = db.query(RTO, State).join(State, RTO.state_id == State.id)
                
                if active_only:
                    query = query.filter(RTO.is_active == True)
                
                if states_with_rtos_only:
                    query = query.filter(State.total_rto != 0)
                
                results = query.order_by(State.name, RTO.name).all()
                
                self.rtos = [
                    RTOData(
                        id=rto.id,
                        state_id=rto.state_id,
                        state_name=state.name,
                        state_code=state.code,
                        name=rto.name,
                        code=rto.code,
                        value=rto.value,
                        full_text=rto.full_text,
                        is_active=rto.is_active
                    )
                    for rto, state in results
                ]
                
                # Group by state
                self._group_rtos_by_state()
                
                logger.info(f"Extracted {len(self.rtos)} RTOs from database")
                return self.rtos
                
        except Exception as e:
            logger.error(f"Failed to extract RTOs: {e}")
            return []
    
    def extract_rtos_by_state_id(self, state_id: int, active_only: bool = True) -> List[RTOData]:
        """Extract RTOs for a specific state ID"""
        try:
            with SessionLocal() as db:
                query = db.query(RTO, State).join(State, RTO.state_id == State.id).filter(
                    RTO.state_id == state_id
                )
                
                if active_only:
                    query = query.filter(RTO.is_active == True)
                
                results = query.order_by(RTO.name).all()
                
                state_rtos = [
                    RTOData(
                        id=rto.id,
                        state_id=rto.state_id,
                        state_name=state.name,
                        state_code=state.code,
                        name=rto.name,
                        code=rto.code,
                        value=rto.value,
                        full_text=rto.full_text,
                        is_active=rto.is_active
                    )
                    for rto, state in results
                ]
                
                logger.info(f"Extracted {len(state_rtos)} RTOs for state ID {state_id}")
                return state_rtos
                
        except Exception as e:
            logger.error(f"Failed to extract RTOs for state {state_id}: {e}")
            return []
    
    def extract_rtos_by_state_code(self, state_code: str, active_only: bool = True) -> List[RTOData]:
        """Extract RTOs for a specific state code"""
        try:
            with SessionLocal() as db:
                query = db.query(RTO, State).join(State, RTO.state_id == State.id).filter(
                    State.code == state_code
                )
                
                if active_only:
                    query = query.filter(RTO.is_active == True)
                
                results = query.order_by(RTO.name).all()
                
                state_rtos = [
                    RTOData(
                        id=rto.id,
                        state_id=rto.state_id,
                        state_name=state.name,
                        state_code=state.code,
                        name=rto.name,
                        code=rto.code,
                        value=rto.value,
                        full_text=rto.full_text,
                        is_active=rto.is_active
                    )
                    for rto, state in results
                ]
                
                logger.info(f"Extracted {len(state_rtos)} RTOs for state code {state_code}")
                return state_rtos
                
        except Exception as e:
            logger.error(f"Failed to extract RTOs for state {state_code}: {e}")
            return []
    
    def _group_rtos_by_state(self):
        """Group RTOs by state for easier access"""
        self.rtos_by_state = {}
        
        for rto in self.rtos:
            state_key = rto.state_code
            if state_key not in self.rtos_by_state:
                self.rtos_by_state[state_key] = []
            self.rtos_by_state[state_key].append(rto)
    
    def get_rtos_by_state_code(self, state_code: str) -> List[RTOData]:
        """Get RTOs for a state from cached data"""
        if not self.rtos:
            self.extract_all_rtos()
        
        return self.rtos_by_state.get(state_code, [])
    
    def get_rtos_by_state_id(self, state_id: int) -> List[RTOData]:
        """Get RTOs for a state ID from cached data"""
        if not self.rtos:
            self.extract_all_rtos()
        
        matching_rtos = [rto for rto in self.rtos if rto.state_id == state_id]
        return matching_rtos
    
    def get_rto_by_id(self, rto_id: int) -> Optional[RTOData]:
        """Get RTO by ID"""
        if not self.rtos:
            self.extract_all_rtos()
        
        for rto in self.rtos:
            if rto.id == rto_id:
                return rto
        return None
    
    def get_rto_by_code(self, rto_code: str, state_code: Optional[str] = None) -> Optional[RTOData]:
        """Get RTO by code, optionally filtered by state"""
        if not self.rtos:
            self.extract_all_rtos()
        
        for rto in self.rtos:
            if rto.code == rto_code:
                if state_code is None or rto.state_code == state_code:
                    return rto
        return None
    
    def get_states_with_rtos(self) -> Dict[str, Dict]:
        """Get unique states that have RTOs"""
        if not self.rtos:
            self.extract_all_rtos()
        
        states = {}
        for rto in self.rtos:
            state_key = rto.state_code
            if state_key not in states:
                states[state_key] = {
                    "id": rto.state_id,
                    "name": rto.state_name,
                    "code": rto.state_code,
                    "rto_count": 0
                }
            states[state_key]["rto_count"] += 1
        
        return states
    
    def get_rto_count_by_state(self) -> Dict[str, int]:
        """Get count of RTOs per state"""
        if not self.rtos:
            self.extract_all_rtos()
        
        counts = {}
        for rto in self.rtos:
            state_key = rto.state_code
            counts[state_key] = counts.get(state_key, 0) + 1
        
        return counts
    
    def get_total_rto_count(self) -> int:
        """Get total count of RTOs"""
        if not self.rtos:
            self.extract_all_rtos()
        return len(self.rtos)
    
    def search_rtos(self, search_term: str, state_code: Optional[str] = None) -> List[RTOData]:
        """Search RTOs by name, code, or full_text"""
        if not self.rtos:
            self.extract_all_rtos()
        
        search_term_lower = search_term.lower()
        matching_rtos = []
        
        for rto in self.rtos:
            # Filter by state if specified
            if state_code and rto.state_code != state_code:
                continue
            
            # Check if search term matches any field
            if (search_term_lower in rto.name.lower() or
                search_term_lower in rto.code.lower() or
                (rto.full_text and search_term_lower in rto.full_text.lower())):
                matching_rtos.append(rto)
        
        return matching_rtos
    
    def refresh_rtos(self) -> List[RTOData]:
        """Force refresh RTOs from database"""
        self.rtos = []
        self.rtos_by_state = {}
        return self.extract_all_rtos()
    
    def get_rtos_summary(self) -> Dict:
        """Get summary of RTOs data"""
        if not self.rtos:
            self.extract_all_rtos()
        
        active_count = sum(1 for rto in self.rtos if rto.is_active)
        states_count = len(self.get_states_with_rtos())
        
        return {
            "total_rtos": len(self.rtos),
            "active_rtos": active_count,
            "inactive_rtos": len(self.rtos) - active_count,
            "states_with_rtos": states_count,
            "average_rtos_per_state": round(len(self.rtos) / states_count, 2) if states_count > 0 else 0
        }


def main():
    """CLI interface for RTO extraction"""
    import sys
    
    extractor = RTOExtractor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "state" and len(sys.argv) > 2:
            # Extract RTOs for specific state
            state_code = sys.argv[2].upper()
            rtos = extractor.extract_rtos_by_state_code(state_code)
            
            print(f"\n=== RTOs for State: {state_code} ({len(rtos)}) ===")
            for rto in rtos:
                print(f"  {rto.id}: {rto.name} ({rto.code})")
            return
        
        elif sys.argv[1] == "summary":
            # Show summary
            extractor.extract_all_rtos()
            summary = extractor.get_rtos_summary()
            
            print("\n=== RTO Summary ===")
            for key, value in summary.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            return
    
    # Default: show all RTOs
    rtos = extractor.extract_all_rtos()
    
    print(f"\n=== All RTOs ({len(rtos)}) ===")
    print(f"{'ID':<6} {'State':<15} {'RTO Name':<40} {'Code':<15}")
    print("-" * 78)
    
    current_state = None
    for rto in rtos:
        if current_state != rto.state_code:
            current_state = rto.state_code
            print(f"\n--- {rto.state_name} ({rto.state_code}) ---")
        
        print(f"{rto.id:<6} {rto.state_code:<15} {rto.name:<40} {rto.code:<15}")
    
    # Show summary
    summary = extractor.get_rtos_summary()
    print(f"\nSummary: {summary['total_rtos']} total RTOs across {summary['states_with_rtos']} states")


if __name__ == "__main__":
    main()