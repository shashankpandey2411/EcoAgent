import os
import random
from typing import Dict, Any, List
import re 
import json
import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class GeminiAPI:
    """
    Wrapper for Google's Gemini API to perform sustainability analysis.
    Includes mock implementation for testing.
    """
    
    def __init__(self, api_key=None, use_mock=True):
        """
        Initialize the Gemini API wrapper.
        
        Args:
            api_key: Google API key for Gemini
            use_mock: Whether to use mock implementation (True) or real API (False)
        """
        self.use_mock = use_mock
        self.api_initialized = False
        
        # Try to initialize the real API if needed
        if not use_mock and GEMINI_AVAILABLE:
            # Use API key from parameters or environment variable
            api_key = api_key or os.environ.get("GEMINI_API_KEY")
            
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-1.0-pro')
                    self.api_initialized = True
                except Exception as e:
                    self.use_mock = True
    
    def infer_material(self, product_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Infer materials from product data using Gemini and mapping material names to their percentage (0-1.0)
        """
        if not self.use_mock and self.api_initialized:
            start_time = datetime.datetime.now()
            result = self._real_infer_material(product_data)
            end_time = datetime.datetime.now()
            return result
        
        # Mock implementation
        title = product_data.get('title', '').lower()
        category = product_data.get('category', '').lower()
        
        # Mock inference based on product category and title
        if 't-shirt' in category or 't-shirt' in title:
            return {"cotton": 0.95, "elastane": 0.05}
            
        elif 'jeans' in category or 'denim' in title:
            return {"cotton": 0.98, "elastane": 0.02}
            
        elif 'jacket' in category or 'jacket' in title:
            if 'fleece' in title:
                return {"polyester": 1.0}
            elif 'puffer' in title:
                return {"polyester": 0.9, "nylon": 0.1}
            else:
                return {"polyester": 0.7, "cotton": 0.3}
                
        elif 'sweater' in category or 'sweater' in title:
            if 'wool' in title:
                return {"wool": 0.8, "acrylic": 0.2}
            else:
                return {"cotton": 0.6, "polyester": 0.4}
        
        # Default fallback
        return {"cotton": 0.5, "polyester": 0.5}
    
    def _real_infer_material(self, product_data: Dict[str, Any]) -> Dict[str, float]:
        """Real implementation using Gemini API."""
        # Construct prompt
        prompt = f"""
        Analyze this product information and infer its material composition with percentages:
        
        Title: {product_data.get('title')}
        Description: {product_data.get('description', 'Not available')}
        Category: {product_data.get('category')}
        
        Provide ONLY a JSON response with materials as keys and percentages as decimal values (0.0-1.0).
        For example: {{"cotton": 0.95, "elastane": 0.05}}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON response
            response_text = response.text
            # Find and extract JSON object

            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                materials = json.loads(json_str)
                return materials
        except Exception as e:
            print(f"Error using Gemini API for material inference: {e}")
        
        # Fallback to mock implementation
        return self.infer_material(product_data)
    
    def analyze_esg_report(self, report_content: str) -> Dict[str, Any]:
        """
        Analyze ESG report content using Gemini API.
        """
        if not self.use_mock and self.api_initialized:
            start_time = datetime.datetime.now()
            result = self._real_analyze_esg_report(report_content)
            end_time = datetime.datetime.now()
            return result
        
        # Mock implementation - simplified from esg_analyzer.py
        # Identify keywords for scoring different aspects
        water_keywords = ["water", "h2o", "hydro", "aqua", "moisture"]
        carbon_keywords = ["carbon", "co2", "greenhouse", "climate", "emission"]
        waste_keywords = ["waste", "recycl", "circular", "landfill", "dispos"]
        labor_keywords = ["labor", "worker", "wage", "social", "ethic", "fair"]
        chemical_keywords = ["chemical", "toxin", "dye", "pfas", "solvent"]
        
        report_lower = report_content.lower()
        
        # Simple scoring based on keyword presence and context
        water_score = sum(1 for word in water_keywords if word in report_lower) / len(water_keywords)
        carbon_score = sum(1 for word in carbon_keywords if word in report_lower) / len(carbon_keywords)
        waste_score = sum(1 for word in waste_keywords if word in report_lower) / len(waste_keywords)
        labor_score = sum(1 for word in labor_keywords if word in report_lower) / len(labor_keywords)
        chemical_score = sum(1 for word in chemical_keywords if word in report_lower) / len(chemical_keywords)
        
        # Add randomness to simulate more nuanced analysis
        water_score = min(1.0, water_score + random.uniform(-0.2, 0.2))
        carbon_score = min(1.0, carbon_score + random.uniform(-0.2, 0.2))
        waste_score = min(1.0, waste_score + random.uniform(-0.2, 0.2))
        labor_score = min(1.0, labor_score + random.uniform(-0.2, 0.2))
        chemical_score = min(1.0, chemical_score + random.uniform(-0.2, 0.2))
        
        # Calculate overall score (scale 0-10)
        overall_score = (water_score + carbon_score + waste_score + labor_score + chemical_score) * 2
        
        result = {
            "rating": round(overall_score, 1),
            "water_impact": round(water_score * 10, 1),
            "carbon_impact": round(carbon_score * 10, 1),
            "waste_management": round(waste_score * 10, 1),
            "labor_practices": round(labor_score * 10, 1),
            "chemical_usage": round(chemical_score * 10, 1),
            "summary": "The report details several sustainability initiatives.",
            "has_specific_targets": "goal" in report_lower or "target" in report_lower or "by 20" in report_lower,
            "has_certifications": "certif" in report_lower or "standard" in report_lower
        }
        
        return result
    
    def _real_analyze_esg_report(self, report_content: str) -> Dict[str, Any]:
        """Real implementation using Gemini API."""
        # Construct prompt
        prompt = f"""
        Analyze this ESG/sustainability report for a clothing/apparel company and provide ratings (0-10 scale) 
        for the following aspects, where higher scores are better:
        
        Report Content:
        {report_content[:8000]}  # Limit to avoid token issues
        
        Provide ONLY a JSON response with:
        - rating: overall score (0-10)
        - water_impact: score for water usage and conservation (0-10)
        - carbon_impact: score for carbon emissions and climate (0-10)
        - waste_management: score for waste reduction and circular economy (0-10)
        - labor_practices: score for worker welfare and ethical production (0-10)
        - chemical_usage: score for chemical management and toxicity (0-10)
        - summary: brief 1-2 sentence summary of key findings
        - has_specific_targets: boolean for whether they have numerical targets with deadlines
        - has_certifications: boolean for whether they mention recognized certifications
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON response
            response_text = response.text
            # Find and extract JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                analysis = json.loads(json_str)
                return analysis
        except Exception as e:
            print(f"Error using Gemini API for ESG analysis: {e}")
        
        # Fallback to mock implementation
        return self.analyze_esg_report(report_content)
    
    def analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze reviews using Gemini API to extract sustainability insights.
        """
        if not self.use_mock and self.api_initialized:
            start_time = datetime.datetime.now()
            result = self._real_analyze_reviews(reviews)
            end_time = datetime.datetime.now()
            return result
        
        # Mock implementation - simplified from review_analyzer.py
        # Sustainability keywords by category
        sustainability_keywords = {
            "materials": ["organic", "recycled", "sustainable", "synthetic", "plastic"],
            "production": ["ethical", "factory", "working conditions", "labor"],
            "packaging": ["packaging", "plastic", "excessive", "waste"],
            "durability": ["quality", "durable", "lasted", "falling apart"],
            "environmental_impact": ["carbon", "footprint", "climate", "environmental"]
        }
        
        # Flags to identify in reviews
        sustainability_flags = [
            "greenwashing", "quality_concerns", "ethical_production", "chemical_concerns",
            "excessive_packaging", "microplastics", "false_claims", "certifications"
        ]
        
        # Mock analysis results
        flags_triggered = random.random() < 0.4
        selected_flags = random.sample(sustainability_flags, k=min(3, len(sustainability_flags))) if flags_triggered else []
        sentiment = random.uniform(4.0, 7.0)
        
        result = {
            "total_reviews_analyzed": len(reviews),
            "flags_triggered": flags_triggered,
            "sustainability_flags": selected_flags,
            "insights": ["Consumers frequently mention materials in their reviews."],
            "overall_sustainability_sentiment": sentiment
        }
        
        return result
    
    def _real_analyze_reviews(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Real implementation using Gemini API."""
        # Format reviews for analysis
        reviews_text = []
        for i, review in enumerate(reviews[:50]):  # Limit to 50 reviews to avoid token issues
            text = review.get("text", "").strip()
            if text:
                rating = review.get("rating", "unknown")
                reviews_text.append(f"Review {i+1} (Rating: {rating}/5): {text[:200]}...")
        
        reviews_formatted = "\n\n".join(reviews_text)
        
        # Construct prompt
        prompt = f"""
        Analyze these product reviews to extract sustainability-related insights:
        
        {reviews_formatted}
        
        Provide ONLY a JSON response with:
        - overall_sustainability_sentiment: score from 0-10 representing how positively consumers view the product's sustainability
        - insights: list of 3-5 key insights about sustainability perceptions
        - flags_triggered: boolean indicating if any sustainability concerns were raised
        - sustainability_flags: list of concerns from these options: greenwashing, quality_concerns, ethical_production, chemical_concerns, excessive_packaging, microplastics, false_claims, certifications
        - total_reviews_analyzed: the number of reviews that were analyzed
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON response
            response_text = response.text
            # Find and extract JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                analysis = json.loads(json_str)
                return analysis
        except Exception as e:
            print(f"Error using Gemini API for reviews analysis: {e}")
        
        # Fallback to mock implementation
        return self.analyze_reviews(reviews)
    
    def analyze_sustainability_news(self, brand: str, news_items: List[Dict[str, Any]], prompt: str) -> Dict[str, Any]:
        """
        Analyze sustainability news about a brand.
        """
        if not self.use_mock and self.api_initialized:
            start_time = datetime.datetime.now()
            result = self._real_analyze_sustainability_news(brand, news_items, prompt)
            end_time = datetime.datetime.now()
            return result
        
        # Mock implementation (simplified version)
        sentiment_score = 0
        
        # Set default values
        for item in news_items:
            if not isinstance(item, dict) or "summary" not in item:
                continue
                
            summary = item["summary"].lower()
            
            # Check for positive keywords
            if any(word in summary for word in ["announce", "commit", "launch", "improve", "success"]):
                sentiment_score += 1
            
            # Check for negative keywords
            if any(word in summary for word in ["criticism", "concern", "fail", "greenwash", "accus"]):
                sentiment_score -= 1
        
        # Normalize sentiment score to 0-10 scale
        num_articles = len([item for item in news_items if isinstance(item, dict) and "summary" in item])
        if num_articles > 0:
            scaled_sentiment = 5 + (sentiment_score / num_articles) * 2.5
            scaled_sentiment = max(1, min(10, scaled_sentiment))  # Ensure it's between 1-10
        else:
            scaled_sentiment = 5.0  # Default neutral score
        
        # Generate a summary based on the news items
        if num_articles > 0:
            has_initiatives = any("announce" in item["summary"].lower() for item in news_items if isinstance(item, dict) and "summary" in item)
            has_criticism = any("concern" in item["summary"].lower() or "accus" in item["summary"].lower() for item in news_items if isinstance(item, dict) and "summary" in item)
            
            if has_initiatives and has_criticism:
                summary = f"{brand} has some sustainability initiatives but also faces criticism."
            elif has_initiatives:
                summary = f"{brand} has announced sustainability initiatives recently."
            elif has_criticism:
                summary = f"{brand} has faced criticism regarding its sustainability practices."
            else:
                summary = f"Limited sustainability information is available for {brand}."
        else:
            summary = f"No recent sustainability news found for {brand}."
            has_initiatives = False
            has_criticism = False
        
        result = {
            "rating": round(scaled_sentiment, 1),
            "news_items": news_items,
            "summary": summary,
            "has_recent_initiatives": has_initiatives,
            "has_criticism": has_criticism
        }
        
        return result
    
    def _real_analyze_sustainability_news(self, brand: str, news_items: List[Dict[str, Any]], prompt: str) -> Dict[str, Any]:
        """Real implementation using Gemini API."""
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON response
            response_text = response.text
            # Find and extract JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                analysis = json.loads(json_str)
                
                # Ensure expected fields are present
                if "rating" not in analysis:
                    analysis["rating"] = 5.0
                if "summary" not in analysis:
                    analysis["summary"] = f"Analysis of sustainability news for {brand}."
                    
                # Add news items to the response
                analysis["news_items"] = news_items
                
                # Analyze if there are initiatives or criticism
                has_initiatives = False
                has_criticism = False
                
                if "initiatives" in analysis:
                    has_initiatives = len(analysis["initiatives"]) > 0
                elif "insights" in analysis and any("initiative" in insight.lower() for insight in analysis["insights"]):
                    has_initiatives = True
                
                if "criticism" in analysis:
                    has_criticism = len(analysis["criticism"]) > 0
                elif "concerns" in analysis and len(analysis["concerns"]) > 0:
                    has_criticism = True
                elif "insights" in analysis and any("criticism" in insight.lower() or "concern" in insight.lower() for insight in analysis["insights"]):
                    has_criticism = True
                
                analysis["has_recent_initiatives"] = has_initiatives
                analysis["has_criticism"] = has_criticism
                
                return analysis
                
        except Exception as e:
            print(f"Error using Gemini API for sustainability news analysis: {e}")
        
        # Fallback to mock implementation
        return self.analyze_sustainability_news(brand, news_items, prompt) 