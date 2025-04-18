import json
import random
from typing import Dict, List, Any


class AmazonScraper:
    
    def __init__(self):
        """Initialize with mock product data."""
        # Mock product database
        self.mock_products = {
            # Cotton t-shirt examples
            "B07C5JHN8Z": {
                "title": "Organic Cotton Classic T-Shirt",
                "brand": "EcoWear",
                "material": "100% Organic Cotton",
                "category": "T-Shirt",
                "price": 24.99
            },
            "B08XYZT123": {
                "title": "Premium Cotton T-Shirt 3-Pack",
                "brand": "BasicThreads",
                "material": "95% Cotton, 5% Elastane",
                "category": "T-Shirt",
                "price": 29.99
            },
            
            # Denim examples
            "B09ABC4567": {
                "title": "Sustainable Slim Fit Jeans",
                "brand": "GreenDenim",
                "material": "98% Organic Cotton, 2% Elastane",
                "category": "Jeans",
                "price": 79.99
            },
            "B07DEF8901": {
                "title": "Vintage Straight Leg Jeans",
                "brand": "DenimCo",
                "material": "100% Cotton",
                "category": "Jeans",
                "price": 59.99
            },
            
            # Synthetic jacket examples
            "B10GHI2345": {
                "title": "Recycled Polyester Puffer Jacket",
                "brand": "EcoOutdoor",
                "material": "100% Recycled Polyester",
                "category": "Jacket",
                "price": 129.99
            },
            "B11JKL6789": {
                "title": "Water-Resistant Fleece Jacket",
                "brand": "NorthStyle",
                "material": "85% Polyester, 15% Nylon",
                "category": "Jacket",
                "price": 89.99
            },
            
            # Mixed/complex examples
            "B12MNO1234": {
                "title": "Performance Sports T-Shirt",
                "brand": "AthleteGear",
                "material": "Dri-Fit Technology Fabric",  # Intentionally vague
                "category": "Athletic Wear",
                "price": 34.99
            },
            "B13PQR5678": {
                "title": "Luxury Blend Sweater",
                "brand": "CashmereElite",
                "material": "70% Merino Wool, 30% Cashmere",
                "category": "Sweater",
                "price": 149.99
            }
        }
        
        # Mock review database
        self.mock_reviews = self._generate_mock_reviews()
    
    def _extract_asin_from_url(self, url: str) -> str:
        """Extract ASIN from Amazon URL."""
        # Check if a known ASIN is in the URL
        for asin in self.mock_products.keys():
            if asin in url:
                return asin
        
        # Return a random product if no match
        return random.choice(list(self.mock_products.keys()))
    
    def scrape_product_page(self, url: str) -> Dict[str, Any]:
        """Scrape Amazon product page for information."""
        # Extract ASIN and return mock data
        asin = self._extract_asin_from_url(url)
        
        if asin in self.mock_products:
            return self.mock_products[asin]
        else:
            # Return random product if ASIN not found
            random_asin = random.choice(list(self.mock_products.keys()))
            return self.mock_products[random_asin]
    
    def _generate_mock_reviews(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate mock reviews for products."""
        reviews = {}
        
        # Sustainability-related phrases
        sustainability_phrases = [
            "eco-friendly",
            "sustainable",
            "organic",
            "ethical production",
            "environmentally conscious",
            "carbon footprint",
            "recycled materials",
            "biodegradable",
            "chemical-free",
            "fair trade"
        ]
        
        # Concern phrases
        concern_phrases = [
            "doesn't seem very sustainable",
            "cheaply made",
            "synthetic smell",
            "probably not eco-friendly",
            "questionable origin",
            "doubt it's actually organic",
            "packaging was excessive",
            "not as green as advertised",
            "disappointed in the environmental claims",
            "microplastics concern"
        ]
        
        # Generate reviews for each product
        for asin in self.mock_products.keys():
            product_reviews = []
            num_reviews = random.randint(5, 15)
            
            for i in range(num_reviews):
                # Determine if review mentions sustainability
                mentions_sustainability = random.random() < 0.4
                is_concern = random.random() < 0.3
                
                rating = random.randint(1, 5)
                
                review_text = f"Review {i+1}: "
                if mentions_sustainability:
                    if is_concern:
                        phrase = random.choice(concern_phrases)
                        review_text += f"I like the product but {phrase}. "
                    else:
                        phrase = random.choice(sustainability_phrases)
                        review_text += f"Really appreciate that this is {phrase}. "
                
                review_text += "Overall good purchase." if rating >= 3 else "Wouldn't buy again."
                
                review = {
                    "rating": rating,
                    "text": review_text,
                    "helpful_votes": random.randint(0, 20),
                    "verified_purchase": random.random() < 0.8
                }
                
                product_reviews.append(review)
            
            reviews[asin] = product_reviews
        
        return reviews
    
    def scrape_reviews(self, url: str) -> List[Dict[str, Any]]:
        """Scrape reviews for a product."""
        # Extract ASIN and return mock reviews
        asin = self._extract_asin_from_url(url)
        
        if asin in self.mock_reviews:
            return self.mock_reviews[asin]
        else:
            # Return empty list if no reviews found
            return []
