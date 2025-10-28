"""
XML service utility for IriusRisk Library Editor API
"""

import logging
from pathlib import Path
from typing import List, Optional
from xml.etree.ElementTree import Element

import xmlschema

logger = logging.getLogger(__name__)


class XMLService:
    """Utility class for XML operations"""
    
    @staticmethod
    def get_nodes(node_list) -> List[Element]:
        """Get element nodes from node list"""
        elements = []
        for node in node_list:
            if hasattr(node, 'tag'):  # Element node
                elements.append(node)
        return elements
    
    @staticmethod
    def get_element_by_name(parent: Element, name: str) -> Optional[Element]:
        """Get element by name from parent"""
        for child in parent:
            if child.tag == name:
                return child
        return None
    
    @staticmethod
    def validate_xml_schema(xml_path: str) -> bool:
        """Validate XML against schema"""
        try:
            # Get the schema path relative to the project
            schema_path = Path(__file__).parent.parent.parent / "resources" / "XSD_Schema" / "library.xsd"
            
            if not schema_path.exists():
                logger.warning(f"Schema file not found at {schema_path}")
                return True  # Skip validation if schema not found
            
            # Load and validate schema
            schema = xmlschema.XMLSchema(str(schema_path))
            schema.validate(xml_path)
            return True
            
        except Exception as e:
            logger.error(f"XML validation error: {e}")
            return False
