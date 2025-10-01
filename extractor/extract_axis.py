# extractor/extract_axis.py
"""
Extract axis filters from database
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from db.session import SessionLocal
from db.models import AxisFilter

logger = logging.getLogger("app.extractor.axis")


class AxisType(Enum):
    """Axis types"""
    X = "X"
    Y = "Y"


@dataclass
class AxisFilterData:
    """Represents an axis filter"""
    id: int
    axis: str
    filter: str


class AxisExtractor:
    """Extracts axis filters from database"""
    
    def __init__(self):
        self.x_axis_filters = []
        self.y_axis_filters = []
    
    def extract_all_axis_filters(self) -> Dict[str, List[AxisFilterData]]:
        """Extract all axis filters from database"""
        try:
            with SessionLocal() as db:
                axis_filters = db.query(AxisFilter).order_by(
                    AxisFilter.axis, AxisFilter.filter
                ).all()
                
                x_filters = []
                y_filters = []
                
                for axis_filter in axis_filters:
                    filter_data = AxisFilterData(
                        id=axis_filter.id,
                        axis=axis_filter.axis,
                        filter=axis_filter.filter
                    )
                    
                    if axis_filter.axis == "X":
                        x_filters.append(filter_data)
                    elif axis_filter.axis == "Y":
                        y_filters.append(filter_data)
                
                self.x_axis_filters = x_filters
                self.y_axis_filters = y_filters
                
                logger.info(f"Extracted {len(x_filters)} X-axis and {len(y_filters)} Y-axis filters")
                
                return {
                    "X": x_filters,
                    "Y": y_filters
                }
                
        except Exception as e:
            logger.error(f"Failed to extract axis filters: {e}")
            return {"X": [], "Y": []}
    
    def extract_x_axis_filters(self) -> List[AxisFilterData]:
        """Extract X-axis filters only"""
        try:
            with SessionLocal() as db:
                x_filters = db.query(AxisFilter).filter(
                    AxisFilter.axis == "X"
                ).order_by(AxisFilter.filter).all()
                
                self.x_axis_filters = [
                    AxisFilterData(
                        id=filter.id,
                        axis=filter.axis,
                        filter=filter.filter
                    )
                    for filter in x_filters
                ]
                
                logger.info(f"Extracted {len(self.x_axis_filters)} X-axis filters")
                return self.x_axis_filters
                
        except Exception as e:
            logger.error(f"Failed to extract X-axis filters: {e}")
            return []
    
    def extract_y_axis_filters(self) -> List[AxisFilterData]:
        """Extract Y-axis filters only"""
        try:
            with SessionLocal() as db:
                y_filters = db.query(AxisFilter).filter(
                    AxisFilter.axis == "Y"
                ).order_by(AxisFilter.filter).all()
                
                self.y_axis_filters = [
                    AxisFilterData(
                        id=filter.id,
                        axis=filter.axis,
                        filter=filter.filter
                    )
                    for filter in y_filters
                ]
                
                logger.info(f"Extracted {len(self.y_axis_filters)} Y-axis filters")
                return self.y_axis_filters
                
        except Exception as e:
            logger.error(f"Failed to extract Y-axis filters: {e}")
            return []
    
    def get_axis_filters_dict(self) -> Dict[str, List[str]]:
        """Get axis filters as dictionary with filter names only"""
        if not self.x_axis_filters and not self.y_axis_filters:
            self.extract_all_axis_filters()
        
        return {
            "X": [filter.filter for filter in self.x_axis_filters],
            "Y": [filter.filter for filter in self.y_axis_filters]
        }
    
    def get_filter_by_name(self, filter_name: str) -> List[AxisFilterData]:
        """Get filters by name (could be in both X and Y)"""
        if not self.x_axis_filters and not self.y_axis_filters:
            self.extract_all_axis_filters()
        
        matching_filters = []
        
        for filter in self.x_axis_filters + self.y_axis_filters:
            if filter.filter.lower() == filter_name.lower():
                matching_filters.append(filter)
        
        return matching_filters
    
    def get_axis_count(self) -> Dict[str, int]:
        """Get count of filters by axis"""
        if not self.x_axis_filters and not self.y_axis_filters:
            self.extract_all_axis_filters()
        
        return {
            "X": len(self.x_axis_filters),
            "Y": len(self.y_axis_filters),
            "total": len(self.x_axis_filters) + len(self.y_axis_filters)
        }
    
    def refresh_filters(self) -> Dict[str, List[AxisFilterData]]:
        """Force refresh axis filters from database"""
        self.x_axis_filters = []
        self.y_axis_filters = []
        return self.extract_all_axis_filters()
    
    def get_current_axis_labels(self) -> Dict[str, str]:
        """
        Source of truth for the currently selected axis labels from DB.
        We pick one label per axis. Adjust the selection rule as you prefer:
        - If you have a 'current' flag/setting table later, switch to that.
        - For now: return the first row alphabetically per axis.
        """
        try:
            with SessionLocal() as db:
                # Fetch all filters grouped by axis
                rows = db.query(AxisFilter).all()
                x = sorted([r.filter for r in rows if r.axis == "X"])
                y = sorted([r.filter for r in rows if r.axis == "Y"])

                if not x or not y:
                    raise ValueError("AxisFilter table missing X or Y entries")

                return {"X": x[0], "Y": y[0]}
        except Exception as e:
            logger.error(f"Failed to get current axis labels from DB: {e}")
            raise

    def get_axis_id_by_label(self, label: str) -> Optional[int]:
        """
        Get axis ID by label text
        
        Args:
            label: Axis label (e.g., "Maker", "Month Wise")
            
        Returns:
            Axis ID if found, None otherwise
        """
        from db.session import get_session
        from db.models import AxisFilter
        
        session = next(get_session())
        try:
            axis = session.query(AxisFilter).filter(
                AxisFilter.filter == label
            ).first()
            
            if axis:
                return axis.id
            else:
                logger.warning(f"Axis not found for label: {label}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting axis ID: {e}")
            return None
        finally:
            session.close()
    
def main():
    """CLI interface for axis extraction"""
    extractor = AxisExtractor()
    filters = extractor.extract_all_axis_filters()
    
    print("\n=== X-Axis Filters ===")
    for filter in filters["X"]:
        print(f"  {filter.id}: {filter.filter}")
    
    print("\n=== Y-Axis Filters ===")
    for filter in filters["Y"]:
        print(f"  {filter.id}: {filter.filter}")
    
    counts = extractor.get_axis_count()
    print(f"\nTotal: {counts['X']} X-axis, {counts['Y']} Y-axis filters")


if __name__ == "__main__":
    main()