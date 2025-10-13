# extractor/__init__.py
"""
Extractor package for Vahan data extraction from database
Handles extraction of states, RTOs, axis filters, and vehicle filters
"""

from .extract_states import StateExtractor, StateData
from .extract_axis import AxisExtractor, AxisFilterData, AxisType
from .extract_vehicle_filter import VehicleFilterExtractor, VehicleFilterData
from .extract_all_rto import RTOExtractor, RTOData

__all__ = [
    # Extractors
    'StateExtractor',
    'AxisExtractor', 
    'VehicleFilterExtractor',
    'RTOExtractor',
    
    # Data classes
    'StateData',
    'AxisFilterData',
    'VehicleFilterData',
    'RTOData',
    
    # Enums
    'AxisType'
]

# Package version
__version__ = '1.0.0'


class DataExtractor:
    """
    Main extractor class that combines all extractors
    Provides a unified interface for extracting all required data
    """
    
    def __init__(self):
        self.state_extractor = StateExtractor()
        self.axis_extractor = AxisExtractor()
        self.vehicle_extractor = VehicleFilterExtractor()
        self.rto_extractor = RTOExtractor()
        
        self._extracted_data = {
            'states': False,
            'axis_filters': False,
            'vehicle_filters': False,
            'rtos': False
        }
    
    def extract_all_data(self, force_refresh: bool = False) -> dict:
        """Extract all data from database"""
        if force_refresh:
            self.refresh_all_data()
        
        # Extract states
        if not self._extracted_data['states'] or force_refresh:
            states = self.state_extractor.extract_active_states()
            self._extracted_data['states'] = True
        else:
            states = self.state_extractor.states
        
        # Extract axis filters
        if not self._extracted_data['axis_filters'] or force_refresh:
            axis_filters = self.axis_extractor.extract_all_axis_filters()
            self._extracted_data['axis_filters'] = True
        else:
            axis_filters = self.axis_extractor.get_axis_filters_dict()
        
        # Extract vehicle filters
        if not self._extracted_data['vehicle_filters'] or force_refresh:
            vehicle_filters = self.vehicle_extractor.extract_active_vehicle_filters()
            self._extracted_data['vehicle_filters'] = True
        else:
            vehicle_filters = self.vehicle_extractor.vehicle_filters
        
        # Extract RTOs
        if not self._extracted_data['rtos'] or force_refresh:
            rtos = self.rto_extractor.extract_all_rtos()
            self._extracted_data['rtos'] = True
        else:
            rtos = self.rto_extractor.rtos
        
        return {
            'states': states,
            'axis_filters': axis_filters,
            'vehicle_filters': vehicle_filters,
            'rtos': rtos
        }
    
    def get_states_with_rtos(self):
        """Get only states that have RTOs"""
        if not self._extracted_data['states']:
            self.state_extractor.extract_active_states()
            self._extracted_data['states'] = True
        
        return self.state_extractor.states
    
    def get_rtos_for_state(self, state_code: str):
        """Get RTOs for a specific state"""
        if not self._extracted_data['rtos']:
            self.rto_extractor.extract_all_rtos()
            self._extracted_data['rtos'] = True
        
        return self.rto_extractor.get_rtos_by_state_code(state_code)
    
    def get_axis_filters(self):
        """Get axis filters"""
        if not self._extracted_data['axis_filters']:
            self.axis_extractor.extract_all_axis_filters()
            self._extracted_data['axis_filters'] = True
        
        return {
            'X': self.axis_extractor.x_axis_filters,
            'Y': self.axis_extractor.y_axis_filters
        }
    
    def get_vehicle_filters(self):
        """Get active vehicle filters"""
        if not self._extracted_data['vehicle_filters']:
            self.vehicle_extractor.extract_active_vehicle_filters()
            self._extracted_data['vehicle_filters'] = True
        
        return self.vehicle_extractor.vehicle_filters
    
    def refresh_all_data(self):
        """Force refresh all data from database"""
        self.state_extractor.refresh_states()
        self.axis_extractor.refresh_filters()
        self.vehicle_extractor.refresh_filters()
        self.rto_extractor.refresh_rtos()
        
        # Reset extraction flags
        for key in self._extracted_data:
            self._extracted_data[key] = False
    
    def get_extraction_summary(self) -> dict:
        """Get summary of extracted data"""
        # Ensure data is extracted
        self.extract_all_data()
        
        states_count = len(self.state_extractor.states)
        axis_counts = self.axis_extractor.get_axis_count()
        vehicle_counts = self.vehicle_extractor.get_filter_count()
        rto_summary = self.rto_extractor.get_rtos_summary()
        
        return {
            'states': {
                'total': states_count,
                'with_rtos': states_count  # All extracted states have RTOs
            },
            'axis_filters': axis_counts,
            'vehicle_filters': vehicle_counts,
            'rtos': rto_summary
        }
    
    def validate_data_consistency(self) -> dict:
        """Validate data consistency between extractors"""
        issues = []
        
        # Ensure all data is extracted
        self.extract_all_data()
        
        # Check if all states in RTOs exist in states list
        state_ids_from_states = {state.id for state in self.state_extractor.states}
        state_ids_from_rtos = {rto.state_id for rto in self.rto_extractor.rtos}
        
        missing_states = state_ids_from_rtos - state_ids_from_states
        if missing_states:
            issues.append(f"RTOs reference state IDs not in states list: {missing_states}")
        
        # Check if all states have at least one RTO
        states_without_rtos = state_ids_from_states - state_ids_from_rtos
        if states_without_rtos:
            issues.append(f"States without RTOs found: {states_without_rtos}")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }


# Convenience function for quick data extraction
def extract_all_vahan_data(force_refresh: bool = False) -> dict:
    """
    Convenience function to extract all Vahan data
    Returns dict with states, axis_filters, vehicle_filters, and rtos
    """
    extractor = DataExtractor()
    return extractor.extract_all_data(force_refresh=force_refresh)