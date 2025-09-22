# scrapper/__init__.py
"""
Scrapper package for Vahan RTO data extraction
Handles browser management, element discovery, and web scraping
"""

from .browser import BrowserManager
from .element_cache import ElementCache, ElementSelector, FieldOption
from .element_discovery import ElementDiscoverer

__all__ = [
    'BrowserManager',
    'ElementCache',
    'ElementSelector', 
    'FieldOption',
    'ElementDiscoverer'
]

# Package version
__version__ = '1.0.0'

# Default configuration
DEFAULT_VAHAN_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"