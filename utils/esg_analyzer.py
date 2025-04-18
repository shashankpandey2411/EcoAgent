"""
ESG analyzer for finding, retrieving, and analyzing sustainability reports and news.
"""
import random
from typing import Dict, Any, List
from utils.gemini_api import GeminiAPI


class ESGAnalyzer:
    """
    Analyzes Environmental, Social, and Governance (ESG) reports and sustainability news.
    Includes methods to find and access reports and to summarize news articles.
    """
    
    def __init__(self, gemini_api_key=None, use_mock_api=True):
        """
        Initialize the ESG analyzer with mock data and Gemini API.
        """
        # Initialize Gemini API client
        self.gemini_api = GeminiAPI(api_key=gemini_api_key, use_mock=use_mock_api)
        
        # Mock ESG report database
        self.mock_esg_data = {
            "ecowear": {
                "found": True,
                "accessible": True,
                "url": "https://example.com/ecowear-sustainability-report-2023.pdf",
                "year": 2023,
                "content": """
                EcoWear Sustainability Report 2023
                
                Our Commitments:
                - 100% organic cotton by 2025
                - Carbon neutral operations by 2030
                - Zero waste to landfill by 2024
                - Fair labor practices across all manufacturing facilities
                
                Material Sourcing:
                We have increased our use of organic cotton to 78% this year,
                up from 65% last year. Our goal is to reach 100% by 2025.
                
                Supply Chain:
                We audit 100% of our tier 1 suppliers annually for compliance with 
                our fair labor and environmental standards.
                
                Carbon Footprint:
                We have reduced our carbon emissions by 15% since our 2019 baseline,
                through renewable energy adoption and efficiency improvements.
                
                Water Usage:
                Water consumption in our manufacturing process has decreased by 22%
                through closed-loop water systems and efficiency improvements.
                """
            },
            "greendenim": {
                "found": True,
                "accessible": True,
                "url": "https://example.com/greendenim-esg-report-2023.pdf",
                "year": 2023,
                "content": """
                GreenDenim Sustainability Report 2023
                
                Our Vision:
                To be the world's most environmentally responsible denim brand.
                
                Achievements:
                - 85% reduction in water usage per pair of jeans since 2018
                - 50% of cotton sourced is organic or recycled
                - 100% of factories audited for social compliance
                
                Materials:
                Our denim now uses 35% recycled cotton and 15% hemp on average,
                reducing our reliance on virgin materials.
                
                Chemical Management:
                We have eliminated hazardous chemicals from our production process,
                exceeding ZDHC (Zero Discharge of Hazardous Chemicals) requirements.
                
                Worker Welfare:
                All workers in our supply chain earn at least a living wage as
                defined by regional benchmarks.
                
                Circular Economy:
                We have implemented a takeback program that has collected and
                recycled over 50,000 pairs of jeans in the past year.
                """
            },
            "basicthreads": {
                "found": True,
                "accessible": False,
                "url": "https://example.com/basicthreads-sustainability.pdf",
                "year": 2022
            },
            "denimco": {
                "found": False
            },
            "ecooutdoor": {
                "found": True,
                "accessible": True,
                "url": "https://example.com/ecooutdoor-impact-report-2023.pdf",
                "year": 2023,
                "content": """
                EcoOutdoor Impact Report 2023
                
                Environmental Impact:
                - 100% of our polyester is now recycled from post-consumer plastic bottles
                - PFC-free DWR treatments across all water-resistant products
                - Renewable energy powers 75% of our operations
                
                Product Longevity:
                We design products for durability and repairability, backed by our
                lifetime repair guarantee.
                
                Packaging:
                All packaging is plastic-free and made from recycled or FSC-certified materials.
                
                Climate Action:
                We are certified carbon neutral across our entire value chain through
                reduction initiatives and verified carbon offset projects.
                
                Community:
                We donate 1% of annual sales to environmental conservation initiatives
                through our partnership with 1% for the Planet.
                """
            },
            "northstyle": {
                "found": True,
                "accessible": False,
                "url": "https://example.com/northstyle-csr-report.pdf",
                "year": 2022
            },
            "athletegear": {
                "found": False
            },
            "cashmereelite": {
                "found": True,
                "accessible": True,
                "url": "https://example.com/cashmereelite-responsibility-report.pdf",
                "year": 2023,
                "content": """
                CashmereElite Responsibility Report 2023
                
                Material Traceability:
                100% of our cashmere is fully traceable to the source herding communities
                in Mongolia and China.
                
                Animal Welfare:
                We adhere to the Responsible Wool Standard (RWS) and Good Cashmere Standard
                for all wool and cashmere sourcing.
                
                Grassland Management:
                Working with herding communities to implement sustainable grazing practices
                to prevent overgrazing and desertification.
                
                Economic Impact:
                Direct trade relationships with herding communities ensure fair prices
                and community development initiatives.
                
                Product End-of-Life:
                Our new recycling program accepts used cashmere items for fiber
                recycling into new products.
                """
            }
        }
        
        # Mock sustainability news database
        self.mock_news_data = {
            "denimco": [
                {
                    "title": "DenimCo Launches New 'Low Impact' Denim Collection",
                    "source": "Fashion Daily",
                    "date": "2023-09-15",
                    "summary": "DenimCo has announced a new collection using 30% less water and energy in production. The 'Low Impact' line features organic cotton and natural indigo dyes, marking the company's first major sustainability initiative."
                },
                {
                    "title": "Industry Analysis: Mid-Size Denim Brands Sustainability Rankings",
                    "source": "Apparel Insight",
                    "date": "2023-07-22",
                    "summary": "DenimCo ranked in the middle tier of denim brands for sustainability practices. The report noted a lack of transparency in supply chain and no published sustainability goals."
                }
            ],
            "basicthreads": [
                {
                    "title": "BasicThreads Commits to Better Cotton Initiative",
                    "source": "Textile Update",
                    "date": "2023-08-10",
                    "summary": "BasicThreads announced it will source 50% of its cotton through the Better Cotton Initiative by 2025, addressing concerns from environmental groups about its sourcing practices."
                },
                {
                    "title": "Labor Rights Groups Flag Issues at BasicThreads Suppliers",
                    "source": "Supply Chain Monitor",
                    "date": "2023-04-18",
                    "summary": "A coalition of labor rights organizations has identified concerns regarding working conditions and wage levels at several factories supplying BasicThreads in Southeast Asia."
                }
            ],
            "northstyle": [
                {
                    "title": "NorthStyle Eliminates PFAS from Product Line",
                    "source": "Outdoor Industry News",
                    "date": "2023-11-05",
                    "summary": "NorthStyle announced the complete elimination of PFAS (per- and polyfluoroalkyl substances) from its outdoor apparel, ahead of upcoming regulations on these 'forever chemicals'."
                },
                {
                    "title": "NorthStyle Partners with Textile Recycling Firm",
                    "source": "Circular Economy Weekly",
                    "date": "2023-10-12",
                    "summary": "NorthStyle has partnered with RecycleWear to implement a take-back program for used garments, with the goal of recycling 100 tons of textiles in the first year."
                }
            ],
            "athletegear": [
                {
                    "title": "AthleteGear Faces Greenwashing Accusations",
                    "source": "Consumer Watch",
                    "date": "2023-09-30",
                    "summary": "Consumer advocacy groups have challenged AthleteGear's 'eco-friendly' claims, citing a lack of verifiable data and third-party certification for their supposedly sustainable product lines."
                },
                {
                    "title": "Sports Apparel Industry Sustainability Report",
                    "source": "Retail Analysis",
                    "date": "2023-06-15",
                    "summary": "AthleteGear scored below industry average on sustainability metrics in a new report, particularly in areas of supply chain transparency and chemical management in manufacturing."
                }
            ]
        }
    
    def find_esg_report(self, brand: str) -> Dict[str, Any]:
        """
        Search for ESG or sustainability reports for a given brand.
        """
        # In real implementation, this would use web search APIs or databases
        # For mock purposes, check our predefined data
        brand_key = brand.lower().replace(' ', '')
        
        if brand_key in self.mock_esg_data:
            return self.mock_esg_data[brand_key]
        
        # If not in database, randomly decide if report exists (30% chance)
        # This simulates the incomplete nature of real-world data
        found = random.random() < 0.3
        
        if found:
            accessible = random.random() < 0.6  # 60% chance it's accessible
            if accessible:
                return {
                    "found": True,
                    "accessible": True,
                    "url": f"https://example.com/{brand_key}-sustainability-report.pdf",
                    "year": random.choice([2021, 2022, 2023]),
                    "content": f"Generic sustainability report for {brand}."
                }
            else:
                return {
                    "found": True,
                    "accessible": False,
                    "url": f"https://example.com/{brand_key}-sustainability-report.pdf",
                    "year": random.choice([2021, 2022, 2023])
                }
        else:
            return {"found": False}
    
    def analyze_report_with_gemini(self, report_content: str) -> Dict[str, Any]:
        """
        Analyze ESG report content using Gemini API.
        """
        # Use the GeminiAPI client to analyze ESG report
        return self.gemini_api.analyze_esg_report(report_content)
    
    def search_and_summarize_sustainability_news(self, brand: str) -> Dict[str, Any]:
        """
        Search for and summarize recent sustainability news about a brand.
        """
        try:
            # In real implementation, this would use web search APIs to find news
            # For mock purposes, check our predefined news data
            brand_key = brand.lower().replace(' ', '')
            
            # Initialize news_items as an empty list to avoid 'bool' object is not iterable error
            news_items = []
            
            # Check if we have mock news for this brand
            if brand_key in self.mock_news_data:
                news_items = self.mock_news_data[brand_key]
            else:
                # If not in database, we'll have a 40% chance of finding generic news
                if random.random() < 0.4:
                    # Generate generic news items
                    news_items = [
                        {
                            "title": f"{brand} Mentioned in Industry Sustainability Report",
                            "source": "Industry Today",
                            "date": "2023-08-20",
                            "summary": f"{brand} was mentioned in an industry report on sustainability practices, though specific details about their initiatives were limited."
                        }
                    ]
                    
                    # 50% chance of a second generic item
                    if random.random() < 0.5:
                        news_items.append({
                            "title": f"Market Analysis: {brand}'s Position on Sustainability",
                            "source": "Market Insider",
                            "date": "2023-06-05",
                            "summary": f"Analysts note that {brand} has room for improvement in sustainability practices compared to industry leaders, but is making incremental progress."
                        })
            
            # Ensure news_items is a list
            if not isinstance(news_items, list):
                print(f"Warning: news_items is not a list: {type(news_items)}. Converting to empty list.")
                news_items = []
            
            # If we have news, use Gemini API to analyze it
            if news_items:
                # In a real implementation, we would use the Gemini API here
                # For now, we'll continue with the mock implementation
                
                # Format articles for analysis
                articles_text = "\n\n".join([
                    f"Article: {item['title']}\nSource: {item['source']}\nDate: {item['date']}\nSummary: {item['summary']}"
                    for item in news_items if isinstance(item, dict) and "summary" in item
                ])
                
                prompt = f"""
                Analyze the following news articles about {brand}'s sustainability practices:
                
                {articles_text}
                
                Based on these articles:
                1) Rate the company's sustainability efforts on a scale of 0-10
                2) Summarize the key sustainability initiatives or concerns
                3) Identify whether there are any greenwashing allegations
                4) Note any significant environmental or social impact mentioned
                """
                
                # Use the Gemini API to analyze the news articles
                return self.gemini_api.analyze_sustainability_news(
                    brand=brand,
                    news_items=news_items,
                    prompt=prompt
                )
            
            # Mock Gemini analysis of news articles
            sentiment_score = 0
            
            for item in news_items:
                # Check if item is a dictionary with required keys
                if not isinstance(item, dict) or "summary" not in item:
                    print(f"Warning: Invalid news item format: {item}. Skipping.")
                    continue
                    
                text = item["summary"].lower()
                
                # Simple sentiment analysis
                positive_words = ["improve", "reduce", "achieve", "increase", "goal", "initiative", "success"]
                negative_words = ["concern", "issue", "problem", "fail", "accus", "question", "greenwash"]
                
                pos_count = sum(1 for word in positive_words if word in text)
                neg_count = sum(1 for word in negative_words if word in text)
                
                # Adjust sentiment score based on this article
                sentiment_score += (pos_count - neg_count) / max(1, len(news_items))
            
            # Scale sentiment to 0-10
            scaled_sentiment = max(0, min(10, (sentiment_score + 2) * 2.5))
            
            # Generate summary based on news items
            if not news_items:
                summary = f"No significant sustainability news found for {brand}."
            else:
                topics = []
                for item in news_items:
                    if not isinstance(item, dict) or "summary" not in item:
                        continue
                        
                    item_summary = item["summary"].lower()
                    if "water" in item_summary:
                        topics.append("water usage")
                    if "energy" in item_summary:
                        topics.append("energy consumption")
                    if "labor" in item_summary or "worker" in item_summary:
                        topics.append("labor practices")
                    if "material" in item_summary or "sourc" in item_summary:
                        topics.append("material sourcing")
                
                if topics:
                    topics = list(set(topics))  # Remove duplicates
                    topics_str = ", ".join(topics)
                    summary = f"Recent news about {brand} focuses on {topics_str}. "
                else:
                    summary = f"Recent news mentions {brand}'s sustainability efforts. "
                    
                if scaled_sentiment > 7:
                    summary += "Coverage is generally positive, highlighting progress and commitments."
                elif scaled_sentiment > 4:
                    summary += "Coverage is mixed, noting both achievements and areas for improvement."
                else:
                    summary += "Coverage raises concerns about the effectiveness or authenticity of initiatives."
            
            # Check for initiatives and criticisms safely
            has_initiatives = False
            has_criticism = False
            
            for item in news_items:
                if not isinstance(item, dict) or "summary" not in item:
                    continue
                item_summary = item["summary"].lower()
                if "announce" in item_summary:
                    has_initiatives = True
                if "concern" in item_summary or "accus" in item_summary:
                    has_criticism = True
            
            # Create and return the analysis result
            return {
                "rating": round(scaled_sentiment, 1),
                "news_items": news_items,
                "summary": summary,
                "has_recent_initiatives": has_initiatives,
                "has_criticism": has_criticism
            }
            
        except Exception as e:
            print(f"Error in news summarization: {e}")
            # Return a fallback response
            return {
                "rating": 5.0,
                "news_items": [],
                "summary": f"Unable to retrieve sustainability news for {brand}.",
                "has_recent_initiatives": False,
                "has_criticism": False
            }
