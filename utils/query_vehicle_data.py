"""
Utility functions to query vehicle registration data from database
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from db.models import VehicleRegistrationData, File, State, RTO
from db.session import get_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VehicleDataQuery:
    """Query interface for vehicle registration data"""
    
    def __init__(self):
        self.session = None
    
    def __enter__(self):
        self.session = next(get_session())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
    
    def get_top_makers(self, limit: int = 10, state_code: str = None, 
                       year: int = None) -> List[Dict]:
        """
        Get top makers by total registrations
        
        Args:
            limit: Number of top makers to return
            state_code: Filter by state code
            year: Filter by year
        
        Returns:
            List of dictionaries with maker info and totals
        """
        query = self.session.query(
            VehicleRegistrationData.maker_name,
            func.sum(VehicleRegistrationData.total).label('total_registrations'),
            func.count(VehicleRegistrationData.id).label('record_count')
        )
        
        if state_code:
            query = query.filter(VehicleRegistrationData.state_code == state_code)
        
        if year:
            query = query.filter(VehicleRegistrationData.year == year)
        
        results = query.group_by(VehicleRegistrationData.maker_name)\
                       .order_by(desc('total_registrations'))\
                       .limit(limit)\
                       .all()
        
        return [
            {
                'maker_name': r[0],
                'total_registrations': r[1] or 0,
                'record_count': r[2]
            }
            for r in results
        ]
    
    def get_maker_monthly_breakdown(self, maker_name: str, 
                                    state_code: str = None,
                                    year: int = None) -> Dict:
        """
        Get monthly breakdown for a specific maker
        
        Args:
            maker_name: Name of the maker (partial match)
            state_code: Filter by state code
            year: Filter by year
        
        Returns:
            Dictionary with monthly totals
        """
        query = self.session.query(
            func.sum(VehicleRegistrationData.jan).label('jan'),
            func.sum(VehicleRegistrationData.feb).label('feb'),
            func.sum(VehicleRegistrationData.mar).label('mar'),
            func.sum(VehicleRegistrationData.apr).label('apr'),
            func.sum(VehicleRegistrationData.may).label('may'),
            func.sum(VehicleRegistrationData.jun).label('jun'),
            func.sum(VehicleRegistrationData.jul).label('jul'),
            func.sum(VehicleRegistrationData.aug).label('aug'),
            func.sum(VehicleRegistrationData.sep).label('sep'),
            func.sum(VehicleRegistrationData.oct).label('oct'),
            func.sum(VehicleRegistrationData.nov).label('nov'),
            func.sum(VehicleRegistrationData.dec).label('dec'),
            func.sum(VehicleRegistrationData.total).label('total')
        ).filter(VehicleRegistrationData.maker_name.ilike(f"%{maker_name}%"))
        
        if state_code:
            query = query.filter(VehicleRegistrationData.state_code == state_code)
        
        if year:
            query = query.filter(VehicleRegistrationData.year == year)
        
        result = query.first()
        
        if not result:
            return {}
        
        return {
            'maker_name': maker_name,
            'state_code': state_code,
            'year': year,
            'monthly_data': {
                'jan': result.jan or 0,
                'feb': result.feb or 0,
                'mar': result.mar or 0,
                'apr': result.apr or 0,
                'may': result.may or 0,
                'jun': result.jun or 0,
                'jul': result.jul or 0,
                'aug': result.aug or 0,
                'sep': result.sep or 0,
                'oct': result.oct or 0,
                'nov': result.nov or 0,
                'dec': result.dec or 0
            },
            'total': result.total or 0
        }
    
    def get_state_summary(self, state_code: str, year: int = None) -> Dict:
        """
        Get summary statistics for a state
        
        Args:
            state_code: State code
            year: Filter by year
        
        Returns:
            Dictionary with state summary
        """
        query = self.session.query(
            func.count(func.distinct(VehicleRegistrationData.maker_name)).label('total_makers'),
            func.count(func.distinct(VehicleRegistrationData.rto_code)).label('total_rtos'),
            func.sum(VehicleRegistrationData.total).label('total_registrations'),
            func.count(VehicleRegistrationData.id).label('total_records')
        ).filter(VehicleRegistrationData.state_code == state_code)
        
        if year:
            query = query.filter(VehicleRegistrationData.year == year)
        
        result = query.first()
        
        if not result:
            return {}
        
        return {
            'state_code': state_code,
            'year': year,
            'total_makers': result.total_makers or 0,
            'total_rtos': result.total_rtos or 0,
            'total_registrations': result.total_registrations or 0,
            'total_records': result.total_records or 0
        }
    
    def get_rto_data(self, rto_code: str, year: int = None) -> List[Dict]:
        """
        Get all maker data for a specific RTO
        
        Args:
            rto_code: RTO code
            year: Filter by year
        
        Returns:
            List of maker records for the RTO
        """
        query = self.session.query(VehicleRegistrationData)\
                            .filter(VehicleRegistrationData.rto_code == rto_code)
        
        if year:
            query = query.filter(VehicleRegistrationData.year == year)
        
        results = query.order_by(desc(VehicleRegistrationData.total)).all()
        
        return [
            {
                'maker_name': r.maker_name,
                'monthly_data': {
                    'jan': r.jan, 'feb': r.feb, 'mar': r.mar, 'apr': r.apr,
                    'may': r.may, 'jun': r.jun, 'jul': r.jul, 'aug': r.aug,
                    'sep': r.sep, 'oct': r.oct, 'nov': r.nov, 'dec': r.dec
                },
                'total': r.total,
                'year': r.year
            }
            for r in results
        ]
    
    def search_makers(self, search_term: str, limit: int = 20) -> List[str]:
        """
        Search for makers by name
        
        Args:
            search_term: Search term (partial match)
            limit: Maximum results to return
        
        Returns:
            List of matching maker names
        """
        results = self.session.query(
            VehicleRegistrationData.maker_name
        ).filter(
            VehicleRegistrationData.maker_name.ilike(f"%{search_term}%")
        ).distinct().limit(limit).all()
        
        return [r[0] for r in results]
    
    def get_database_stats(self) -> Dict:
        """Get overall database statistics"""
        
        total_records = self.session.query(VehicleRegistrationData).count()
        total_files = self.session.query(File).count()
        
        total_registrations = self.session.query(
            func.sum(VehicleRegistrationData.total)
        ).scalar() or 0
        
        unique_makers = self.session.query(
            func.count(func.distinct(VehicleRegistrationData.maker_name))
        ).scalar() or 0
        
        unique_states = self.session.query(
            func.count(func.distinct(VehicleRegistrationData.state_code))
        ).scalar() or 0
        
        latest_record = self.session.query(
            VehicleRegistrationData.created_at
        ).order_by(desc(VehicleRegistrationData.created_at)).first()
        
        return {
            'total_records': total_records,
            'total_files': total_files,
            'total_registrations': total_registrations,
            'unique_makers': unique_makers,
            'unique_states': unique_states,
            'latest_data_date': latest_record[0] if latest_record else None
        }
    
    def compare_makers(self, maker_names: List[str], year: int = None) -> Dict:
        """
        Compare multiple makers side by side
        
        Args:
            maker_names: List of maker names to compare
            year: Filter by year
        
        Returns:
            Dictionary with comparison data
        """
        comparison = {}
        
        for maker in maker_names:
            data = self.get_maker_monthly_breakdown(maker, year=year)
            if data:
                comparison[maker] = data
        
        return comparison


# Convenience functions for quick queries

def quick_top_makers(limit: int = 10, state_code: str = None):
    """Quick function to get top makers"""
    with VehicleDataQuery() as query:
        return query.get_top_makers(limit, state_code)


def quick_maker_data(maker_name: str, state_code: str = None):
    """Quick function to get maker data"""
    with VehicleDataQuery() as query:
        return query.get_maker_monthly_breakdown(maker_name, state_code)


def quick_state_summary(state_code: str):
    """Quick function to get state summary"""
    with VehicleDataQuery() as query:
        return query.get_state_summary(state_code)


def quick_database_stats():
    """Quick function to get database stats"""
    with VehicleDataQuery() as query:
        return query.get_database_stats()


# Example usage
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Vehicle Registration Data Query Examples")
    print("="*60 + "\n")
    
    # Get database stats
    print("📊 Database Statistics:")
    stats = quick_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "-"*60 + "\n")
    
    # Get top makers
    print("🏆 Top 5 Makers (All States):")
    top_makers = quick_top_makers(5)
    for idx, maker in enumerate(top_makers, 1):
        print(f"  {idx}. {maker['maker_name']}: {maker['total_registrations']:,} registrations")
    
    print("\n" + "-"*60 + "\n")
    
    # Get specific maker data
    if top_makers:
        maker_name = top_makers[0]['maker_name']
        print(f"📈 Monthly Breakdown for {maker_name}:")
        maker_data = quick_maker_data(maker_name)
        if maker_data:
            for month, count in maker_data['monthly_data'].items():
                print(f"  {month.upper()}: {count:,}")
            print(f"  TOTAL: {maker_data['total']:,}")
