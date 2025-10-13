# extractor/extract_vehicle_filter.py
"""
Extract vehicle filters from database
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from db.session import SessionLocal
from db.models import VehicleFilter

logger = logging.getLogger("app.extractor.vehicle")


@dataclass
class VehicleFilterData:
    """Represents a vehicle filter"""
    id: int
    name: str
    code: Optional[str]
    is_active: bool


class VehicleFilterExtractor:
    """Extracts vehicle filters from database"""
    
    def __init__(self):
        self.vehicle_filters = []
    
    def extract_all_vehicle_filters(self, active_only: bool = True) -> List[VehicleFilterData]:
        """Extract all vehicle filters from database"""
        try:
            with SessionLocal() as db:
                query = db.query(VehicleFilter)
                
                if active_only:
                    query = query.filter(VehicleFilter.is_active == True)
                
                filters = query.order_by(VehicleFilter.name).all()
                
                self.vehicle_filters = [
                    VehicleFilterData(
                        id=filter.id,
                        name=filter.name,
                        code=filter.code,
                        is_active=filter.is_active
                    )
                    for filter in filters
                ]
                
                logger.info(f"Extracted {len(self.vehicle_filters)} vehicle filters")
                return self.vehicle_filters
                
        except Exception as e:
            logger.error(f"Failed to extract vehicle filters: {e}")
            return []
    
    def extract_active_vehicle_filters(self) -> List[VehicleFilterData]:
        """Extract only active vehicle filters"""
        return self.extract_all_vehicle_filters(active_only=True)
    
    def get_vehicle_filter_by_name(self, name: str) -> Optional[VehicleFilterData]:
        """Get vehicle filter by name"""
        if not self.vehicle_filters:
            self.extract_all_vehicle_filters()
        
        for filter in self.vehicle_filters:
            if filter.name.lower() == name.lower():
                return filter
        return None
    
    def get_vehicle_filter_by_code(self, code: str) -> Optional[VehicleFilterData]:
        """Get vehicle filter by code"""
        if not self.vehicle_filters:
            self.extract_all_vehicle_filters()
        
        for filter in self.vehicle_filters:
            if filter.code and filter.code.lower() == code.lower():
                return filter
        return None
    
    def get_vehicle_filter_by_id(self, filter_id: int) -> Optional[VehicleFilterData]:
        """Get vehicle filter by ID"""
        if not self.vehicle_filters:
            self.extract_all_vehicle_filters()
        
        for filter in self.vehicle_filters:
            if filter.id == filter_id:
                return filter
        return None
    
    def get_vehicle_filters_dict(self, key_by: str = "name") -> Dict[str, VehicleFilterData]:
        """
        Get vehicle filters as dictionary
        key_by: 'name', 'code', or 'id'
        """
        if not self.vehicle_filters:
            self.extract_all_vehicle_filters()
        
        if key_by == "name":
            return {filter.name: filter for filter in self.vehicle_filters}
        elif key_by == "code":
            return {filter.code: filter for filter in self.vehicle_filters if filter.code}
        elif key_by == "id":
            return {str(filter.id): filter for filter in self.vehicle_filters}
        else:
            raise ValueError(f"Invalid key_by value: {key_by}. Must be 'name', 'code', or 'id'")
    
    def get_vehicle_names_list(self, active_only: bool = True) -> List[str]:
        """Get list of vehicle filter names"""
        if not self.vehicle_filters:
            self.extract_all_vehicle_filters(active_only=active_only)
        
        filters_to_use = self.vehicle_filters
        if active_only:
            filters_to_use = [f for f in self.vehicle_filters if f.is_active]
        
        return [filter.name for filter in filters_to_use]
    
    def get_vehicle_codes_list(self, active_only: bool = True) -> List[str]:
        """Get list of vehicle filter codes (non-null only)"""
        if not self.vehicle_filters:
            self.extract_all_vehicle_filters(active_only=active_only)
        
        filters_to_use = self.vehicle_filters
        if active_only:
            filters_to_use = [f for f in self.vehicle_filters if f.is_active]
        
        return [filter.code for filter in filters_to_use if filter.code]
    
    def get_filter_count(self) -> Dict[str, int]:
        """Get count of vehicle filters"""
        if not self.vehicle_filters:
            self.extract_all_vehicle_filters(active_only=False)
        
        active_count = sum(1 for f in self.vehicle_filters if f.is_active)
        total_count = len(self.vehicle_filters)
        
        return {
            "active": active_count,
            "inactive": total_count - active_count,
            "total": total_count
        }
    
    def refresh_filters(self) -> List[VehicleFilterData]:
        """Force refresh vehicle filters from database"""
        self.vehicle_filters = []
        return self.extract_all_vehicle_filters()
    
    def search_filters(self, search_term: str, active_only: bool = True) -> List[VehicleFilterData]:
        """Search vehicle filters by name or code"""
        if not self.vehicle_filters:
            self.extract_all_vehicle_filters(active_only=active_only)
        
        search_term_lower = search_term.lower()
        matching_filters = []
        
        for filter in self.vehicle_filters:
            if active_only and not filter.is_active:
                continue
            
            if (search_term_lower in filter.name.lower() or 
                (filter.code and search_term_lower in filter.code.lower())):
                matching_filters.append(filter)
        
        return matching_filters

    def get_filter_id_by_name(self, filter_name: str) -> Optional[int]:
        """
        Get vehicle filter ID by name
        
        Args:
            filter_name: Filter name (e.g., "MOTOR CAR", "PURE EV")
            
        Returns:
            Filter ID if found, None otherwise
        """
        from db.session import get_session
        from db.models import VehicleFilter
        
        session = next(get_session())
        try:
            vehicle_filter = session.query(VehicleFilter).filter(
                VehicleFilter.name == filter_name
            ).first()
            
            if vehicle_filter:
                return vehicle_filter.id
            else:
                logger.warning(f"Vehicle filter not found: {filter_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting vehicle filter ID: {e}")
            return None
        finally:
            session.close()



def main():
    """CLI interface for vehicle filter extraction"""
    extractor = VehicleFilterExtractor()
    filters = extractor.extract_all_vehicle_filters()
    
    print(f"\n=== Vehicle Filters ({len(filters)}) ===")
    print(f"{'ID':<5} {'Name':<30} {'Code':<15} {'Active':<8}")
    print("-" * 60)
    
    for filter in filters:
        code = filter.code or ""
        active = "Yes" if filter.is_active else "No"
        print(f"{filter.id:<5} {filter.name:<30} {code:<15} {active:<8}")
    
    # Show counts
    counts = extractor.get_filter_count()
    print(f"\nSummary: {counts['active']} active, {counts['inactive']} inactive, {counts['total']} total")
    
    # Show names list
    names = extractor.get_vehicle_names_list()
    print(f"\nActive filter names: {', '.join(names)}")


if __name__ == "__main__":
    main()