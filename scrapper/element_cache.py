# scrapper/element_cache.py
"""
Element selector caching system
Stores and retrieves element selectors from database
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from db.session import SessionLocal
from db.models import PortalSite, PortalField, PortalFieldOption

logger = logging.getLogger("app.element_cache")


@dataclass
class ElementSelector:
    """Represents a cached element selector"""
    field_name: str
    selector: str
    ui_type: str
    version_tag: Optional[str] = None
    last_seen_at: Optional[datetime] = None


@dataclass
class FieldOption:
    """Represents a field option (dropdown values, etc.)"""
    value_code: str
    label: str
    parent_code: Optional[str] = None
    is_active: bool = True


class ElementCache:
    """Manages element selectors and field options in database"""
    
    def __init__(self, site_name: str = "vahan"):
        self.site_name = site_name
        self._site_id = None
    
    def _get_site_id(self) -> int:
        """Get or create site ID"""
        if self._site_id:
            return self._site_id
            
        with SessionLocal() as db:
            site = db.query(PortalSite).filter(
                PortalSite.name == self.site_name
            ).first()
            
            if not site:
                # Create new site
                site = PortalSite(
                    name=self.site_name,
                    base_url="https://vahan.parivahan.gov.in",
                    is_active=True
                )
                db.add(site)
                db.commit()
                db.refresh(site)
                logger.info(f"Created new portal site: {self.site_name}")
            
            self._site_id = site.id
            return self._site_id
    
    def store_selector(
        self, 
        field_name: str, 
        selector: str, 
        ui_type: str = "select",
        version_tag: Optional[str] = None,
        depends_on: Optional[str] = None
    ) -> bool:
        """Store or update element selector"""
        try:
            with SessionLocal() as db:
                site_id = self._get_site_id()
                
                # Check if field exists
                field = db.query(PortalField).filter(
                    PortalField.site_id == site_id,
                    PortalField.field_name == field_name
                ).first()
                
                if field:
                    # Update existing field
                    field.selector = selector
                    field.ui_type = ui_type
                    field.version_tag = version_tag
                    field.last_seen_at = datetime.now()
                    logger.debug(f"Updated selector for field '{field_name}'")
                else:
                    # Create new field
                    depends_on_id = None
                    if depends_on:
                        parent_field = db.query(PortalField).filter(
                            PortalField.site_id == site_id,
                            PortalField.field_name == depends_on
                        ).first()
                        if parent_field:
                            depends_on_id = parent_field.id
                    
                    field = PortalField(
                        site_id=site_id,
                        field_name=field_name,
                        selector=selector,
                        ui_type=ui_type,
                        depends_on_id=depends_on_id,
                        version_tag=version_tag,
                        last_seen_at=datetime.now()
                    )
                    db.add(field)
                    logger.debug(f"Created new selector for field '{field_name}'")
                
                db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to store selector for '{field_name}': {e}")
            return False
    
    def get_selector(self, field_name: str) -> Optional[ElementSelector]:
        """Get cached element selector"""
        try:
            with SessionLocal() as db:
                site_id = self._get_site_id()
                
                field = db.query(PortalField).filter(
                    PortalField.site_id == site_id,
                    PortalField.field_name == field_name
                ).first()
                
                if field and field.selector:
                    return ElementSelector(
                        field_name=field.field_name,
                        selector=field.selector,
                        ui_type=field.ui_type,
                        version_tag=field.version_tag,
                        last_seen_at=field.last_seen_at
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get selector for '{field_name}': {e}")
            return None
    
    def store_field_options(
        self, 
        field_name: str, 
        options: List[FieldOption]
    ) -> bool:
        """Store field options (dropdown values, etc.)"""
        try:
            with SessionLocal() as db:
                site_id = self._get_site_id()
                
                # Get field ID
                field = db.query(PortalField).filter(
                    PortalField.site_id == site_id,
                    PortalField.field_name == field_name
                ).first()
                
                if not field:
                    logger.warning(f"Field '{field_name}' not found, cannot store options")
                    return False
                
                # Clear existing options
                db.query(PortalFieldOption).filter(
                    PortalFieldOption.field_id == field.id
                ).delete()
                
                # Add new options
                now = datetime.now()
                for option in options:
                    db_option = PortalFieldOption(
                        field_id=field.id,
                        value_code=option.value_code,
                        label=option.label,
                        parent_code=option.parent_code,
                        is_active=option.is_active,
                        first_seen_at=now,
                        last_seen_at=now
                    )
                    db.add(db_option)
                
                db.commit()
                logger.info(f"Stored {len(options)} options for field '{field_name}'")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store options for '{field_name}': {e}")
            return False
    
    def get_field_options(
        self, 
        field_name: str, 
        parent_code: Optional[str] = None,
        active_only: bool = True
    ) -> List[FieldOption]:
        """Get field options"""
        try:
            with SessionLocal() as db:
                site_id = self._get_site_id()
                
                # Get field
                field = db.query(PortalField).filter(
                    PortalField.site_id == site_id,
                    PortalField.field_name == field_name
                ).first()
                
                if not field:
                    return []
                
                # Build query
                query = db.query(PortalFieldOption).filter(
                    PortalFieldOption.field_id == field.id
                )
                
                if parent_code is not None:
                    query = query.filter(PortalFieldOption.parent_code == parent_code)
                
                if active_only:
                    query = query.filter(PortalFieldOption.is_active == True)
                
                options = query.all()
                
                return [
                    FieldOption(
                        value_code=opt.value_code,
                        label=opt.label,
                        parent_code=opt.parent_code,
                        is_active=opt.is_active
                    )
                    for opt in options
                ]
                
        except Exception as e:
            logger.error(f"Failed to get options for '{field_name}': {e}")
            return []
    
    def is_selector_stale(self, field_name: str, max_age_hours: int = 24) -> bool:
        """Check if selector is stale and needs refresh"""
        selector = self.get_selector(field_name)
        if not selector or not selector.last_seen_at:
            return True
        
        age = datetime.now() - selector.last_seen_at
        return age > timedelta(hours=max_age_hours)
    
    def get_all_selectors(self) -> Dict[str, ElementSelector]:
        """Get all cached selectors for the site"""
        try:
            with SessionLocal() as db:
                site_id = self._get_site_id()
                
                fields = db.query(PortalField).filter(
                    PortalField.site_id == site_id,
                    PortalField.selector.isnot(None)
                ).all()
                
                return {
                    field.field_name: ElementSelector(
                        field_name=field.field_name,
                        selector=field.selector,
                        ui_type=field.ui_type,
                        version_tag=field.version_tag,
                        last_seen_at=field.last_seen_at
                    )
                    for field in fields
                }
                
        except Exception as e:
            logger.error(f"Failed to get all selectors: {e}")
            return {}
    
    def mark_selector_invalid(self, field_name: str) -> bool:
        """Mark a selector as invalid (clear it)"""
        try:
            with SessionLocal() as db:
                site_id = self._get_site_id()
                
                field = db.query(PortalField).filter(
                    PortalField.site_id == site_id,
                    PortalField.field_name == field_name
                ).first()
                
                if field:
                    field.selector = None
                    field.last_seen_at = None
                    db.commit()
                    logger.info(f"Marked selector for '{field_name}' as invalid")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to mark selector invalid for '{field_name}': {e}")
            return False
    
    def cleanup_stale_selectors(self, max_age_days: int = 7) -> int:
        """Remove selectors that haven't been seen for too long"""
        try:
            with SessionLocal() as db:
                site_id = self._get_site_id()
                cutoff_date = datetime.now() - timedelta(days=max_age_days)
                
                count = db.query(PortalField).filter(
                    PortalField.site_id == site_id,
                    PortalField.last_seen_at < cutoff_date
                ).update({
                    PortalField.selector: None,
                    PortalField.last_seen_at: None
                })
                
                db.commit()
                logger.info(f"Cleaned up {count} stale selectors")
                return count
                
        except Exception as e:
            logger.error(f"Failed to cleanup stale selectors: {e}")
            return 0