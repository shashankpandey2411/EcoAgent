from typing import Dict, Any, List
from utils.gemini_api import GeminiAPI


class ReviewAnalyzer:
    """
    Analyzes customer reviews for sustainability-related mentions and sentiments.
    """
    
    def __init__(self, gemini_api_key=None, use_mock_api=True):
        """Initialize with sustainability keywords and API."""
        # API client
        self.gemini_api = GeminiAPI(api_key=gemini_api_key, use_mock=use_mock_api)
        
        # Sustainability keywords by category
        self.sustainability_keywords = {
            "materials": [
                "organic", "recycled", "sustainable", "synthetic", "plastic", 
                "biodegradable", "eco-friendly", "natural", "chemical", "toxic"
            ],
            "production": [
                "ethical", "factory", "working conditions", "made in", "labor", 
                "sweatshop", "fair trade", "child labor", "workers"
            ],
            "packaging": [
                "packaging", "plastic", "excessive", "waste", "recyclable", 
                "minimal", "unnecessary", "eco-packaging", "paper"
            ],
            "durability": [
                "quality", "durable", "lasted", "falling apart", "wear out", 
                "tear", "long-lasting", "disposable", "fast fashion", "lifetime"
            ],
            "environmental_impact": [
                "carbon", "footprint", "climate", "environmental", "green", 
                "eco", "planet", "earth", "pollution", "sustainable"
            ]
        }
        
        # Sustainability flags
        self.sustainability_flags = [
            "greenwashing",           # Claims vs. reality
            "quality_concerns",       # Durability issues
            "ethical_production",     # Labor and production concerns
            "chemical_concerns",      # Harmful chemicals
            "excessive_packaging",    # Packaging waste
            "microplastics",          # Synthetic fiber shedding
            "false_claims",           # Misleading marketing
            "certifications"          # Mentions of standards/certifications
        ]
    
    def analyze_with_gemini(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze reviews using Gemini API for sustainability insights."""
        return self.gemini_api.analyze_reviews(reviews)
