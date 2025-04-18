import re
from typing import Dict, Any, List
from utils.gemini_api import GeminiAPI


class MaterialAnalyzer:
    """
    Analyzes material information from product descriptions.
    """
    
    def __init__(self, gemini_api_key=None, use_mock_api=True):
        """Initialize with known material types."""
        # Initialize API client
        self.gemini_api = GeminiAPI(api_key=gemini_api_key, use_mock=use_mock_api)
        
        # Common material types
        self.known_materials = {
            # Natural fibers
            "cotton": {"type": "natural", "renewable": True, "sub_types": ["organic cotton", "recycled cotton"]},
            "wool": {"type": "natural", "renewable": True, "sub_types": ["merino wool", "recycled wool"]},
            "silk": {"type": "natural", "renewable": True},
            "linen": {"type": "natural", "renewable": True},
            "cashmere": {"type": "natural", "renewable": True},
            "hemp": {"type": "natural", "renewable": True},
            "jute": {"type": "natural", "renewable": True},
            
            # Synthetic fibers
            "polyester": {"type": "synthetic", "renewable": False, "sub_types": ["recycled polyester"]},
            "nylon": {"type": "synthetic", "renewable": False, "sub_types": ["recycled nylon"]},
            "acrylic": {"type": "synthetic", "renewable": False},
            "elastane": {"type": "synthetic", "renewable": False, "synonyms": ["spandex", "lycra"]},
            "spandex": {"type": "synthetic", "renewable": False, "synonyms": ["elastane", "lycra"]},
            "polyurethane": {"type": "synthetic", "renewable": False},
            
            # Semi-synthetic/Man-made cellulosic fibers (MMCF)
            "rayon": {"type": "mmcf", "renewable": True, "synonyms": ["viscose"]},
            "viscose": {"type": "mmcf", "renewable": True, "synonyms": ["rayon"]},
            "modal": {"type": "mmcf", "renewable": True},
            "lyocell": {"type": "mmcf", "renewable": True, "synonyms": ["tencel"]},
            "tencel": {"type": "mmcf", "renewable": True, "synonyms": ["lyocell"]}
        }
        
        # Patterns for extraction
        self.material_patterns = [
            r'(\d+)%\s+([A-Za-z]+)',  # e.g., "95% Cotton"
            r'([A-Za-z]+)\s+(\d+)%',  # e.g., "Cotton 95%"
            r'100%\s+([A-Za-z]+)',    # e.g., "100% Cotton"
            r'([A-Za-z]+)(?:-|\s)blend'  # e.g., "Cotton-blend" or "Cotton blend"
        ]
    
    def is_material_clear(self, material_text: str) -> bool:
        """Check if material information is clear and parseable."""
        if not material_text or material_text.lower() == 'unknown':
            return False
        
        # Check for percentages
        if re.search(r'\d+%', material_text):
            return True
        
        # Check for known materials
        for material in self.known_materials:
            if re.search(rf'\b{material}\b', material_text.lower()):
                return True
        
        # Check for "100%" pattern
        if re.search(r'100%\s+[A-Za-z]+', material_text):
            return True
            
        return False
    
    def parse_material(self, material_text: str) -> Dict[str, float]:
        """Parse material description into components with percentages."""
        result = {}
        material_text = material_text.lower()
        
        # Match percentage patterns
        percentage_matches = re.findall(r'(\d+)%\s+([A-Za-z]+)', material_text)
        percentage_matches.extend(re.findall(r'([A-Za-z]+)\s+(\d+)%', material_text))
        
        if percentage_matches:
            for match in percentage_matches:
                if len(match) == 2:
                    # Get consistent order: percentage, material
                    if match[0].isdigit():
                        percentage, material = match
                    else:
                        material, percentage = match
                    
                    percentage = float(percentage) / 100
                    material = material.lower()
                    
                    # Find material matches
                    for known_material in self.known_materials:
                        if known_material in material or material in known_material:
                            result[known_material] = percentage
                            break
                    else:
                        # Use original if no match
                        result[material] = percentage
        
        # Handle "100%" pattern
        elif "100%" in material_text:
            match = re.search(r'100%\s+([A-Za-z]+)', material_text)
            if match:
                material = match.group(1).lower()
                result[material] = 1.0
        
        # Estimate from material words if no percentages
        if not result:
            for material in self.known_materials:
                if material in material_text:
                    # Equal percentages for multiple materials
                    result[material] = 1.0 / len([m for m in self.known_materials if m in material_text])
        
        # Default to unknown
        if not result and material_text:
            result["unknown"] = 1.0
        
        return result
    
    def infer_material_with_gemini(self, product_data: Dict[str, Any]) -> Dict[str, float]:
        """Use Gemini API to infer materials when description is unclear."""
        return self.gemini_api.infer_material(product_data)
