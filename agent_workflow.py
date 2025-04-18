import argparse
import os
import sys
from utils.scraper import AmazonScraper
from utils.material_analyzer import MaterialAnalyzer
from utils.esg_analyzer import ESGAnalyzer
from utils.review_analyzer import ReviewAnalyzer
from utils.db_query import TextileDBQuery
from utils.report_generator import ReportGenerator
from dotenv import load_dotenv

load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='EcoAgent: Analyze sustainability impact of apparel products'
    )
    parser.add_argument('--url', type=str, help='Amazon product URL')
    parser.add_argument('--depth', type=str, choices=['basic', 'standard', 'comprehensive'], 
                        default='standard', help='Depth of sustainability assessment')
    parser.add_argument('--mock-scraping', action='store_true', 
                        help='Use mock data instead of real web scraping')
    parser.add_argument('--mock-llm', action='store_true', 
                        help='Use mock LLM implementation instead of Gemini API')
    parser.add_argument('--mock-data', action='store_true', 
                        help='Use mock data for ESG reports and textile database')
    parser.add_argument('--gemini-api-key', type=str, 
                        help='API key for Google Gemini (defaults to GEMINI_API_KEY env var)')
    parser.add_argument('--oxylabs-username', type=str, 
                        help='Username for Oxylabs API (defaults to OXYLABS_USERNAME env var)')
    parser.add_argument('--oxylabs-password', type=str, 
                        help='Password for Oxylabs API (defaults to OXYLABS_PASSWORD env var)')
    
    args = parser.parse_args()
    
    # Clean URL if provided
    if args.url and '?' in args.url:
        args.url = args.url.split('?')[0]
        print(f"Cleaned URL: {args.url}")
    
    return args

def initialize(args):
    print("\n=== Step 1: Initializing EcoAgent ===")
    print(f"Assessment Depth: {args.depth}")
    
    # Build URL from product ID if needed
    if not args.url and args.product_id:
        args.url = f"https://www.amazon.com/dp/{args.product_id}"
        print(f"Generated URL: {args.url}")
    
    if not args.url:
        print("Error: Either a product URL or product ID is required")
        sys.exit(1)
    
    # Setup scraping mode
    if args.mock_scraping:
        print("Using mock scraping as requested")
    else:
        print("Using real web scraping")

    # Get Oxylabs credentials    
    if not args.oxylabs_username:
        args.oxylabs_username = os.getenv("OXYLABS_USERNAME")
    
    if not args.oxylabs_password:
        args.oxylabs_password = os.getenv("OXYLABS_PASSWORD")
        
    # Check credential format
    if args.oxylabs_username and '_' not in args.oxylabs_username:
        if ':' in args.oxylabs_username:
            print("Detected combined username:password format - splitting into separate credentials")
            username, password = args.oxylabs_username.split(':', 1)
            args.oxylabs_username = username
            if not args.oxylabs_password:
                args.oxylabs_password = password
        
    if args.oxylabs_username and args.oxylabs_password:
        print("Oxylabs credentials provided - will use Oxylabs Web Scraper API")
    else:
        print("No Oxylabs credentials found - falling back to mock data for scraping")
        args.mock_scraping = True
    
    # Setup Gemini API
    if not args.gemini_api_key:
        args.gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if args.mock_llm:
        print("Using mock LLM implementation as requested")
    elif args.gemini_api_key:
        print("Using Gemini API for analysis")
    else:
        print("No Gemini API key found - falling back to mock LLM implementation")
        args.mock_llm = True
    
    # Setup data mode
    if args.mock_data:
        print("Using mock data for ESG reports and textile database")
    else:
        print("Using real data sources for ESG reports and textile database")
    
    return args

def scrape_product(url, use_mock=False, oxylabs_username=None, oxylabs_password=None):
    print("\n=== Step 2: Scraping Amazon Product Page ===")
    
    # Clean URL if needed
    if url and '?' in url:
        url = url.split('?')[0]
        print(f"Using cleaned URL: {url}")
    
    try:
        scraper = AmazonScraper(
            use_real_scraping=not use_mock,
            oxylabs_username=oxylabs_username,
            oxylabs_password=oxylabs_password
        )
        product_data = scraper.scrape_product_page(url)
        print(f"Successfully retrieved product data:")
        print(f"  - Title: {product_data['title']}")
        print(f"  - Brand: {product_data['brand']}")
        print(f"  - Material: {product_data['material']}")
        print(f"  - Category: {product_data['category']}")
        return product_data
    except Exception as e:
        print(f"Error scraping product: {e}")
        sys.exit(1)

def analyze_material(product_data, gemini_api_key=None, use_mock=False):
    """Analyze material information extracted from the product."""
    print("\n=== Analyzing Material Information ===")
    material_analyzer = MaterialAnalyzer(gemini_api_key=gemini_api_key, use_mock_api=use_mock)
    
    if material_analyzer.is_material_clear(product_data['material']):
        print("Material information is clear and can be directly processed")
        materials = material_analyzer.parse_material(product_data['material'])
    else:
        print("Material information is unclear, using Gemini API to infer materials")
        materials = material_analyzer.infer_material_with_gemini(product_data)
        
    print(f"Identified materials: {', '.join(materials.keys())}")
    return materials

def search_esg_report(brand, gemini_api_key=None, use_mock=False, use_mock_data=False):
    print(f"\n=== Step 4: Searching ESG Report for {brand} ===")
    esg_analyzer = ESGAnalyzer(gemini_api_key=gemini_api_key, use_mock_api=use_mock)
    
    try:
        if use_mock_data:
            print("Using mock ESG data")
            report_info = esg_analyzer.find_esg_report(brand)
        else:
            # Real APIs not yet integrated
            print("Note: Using mock ESG data (real APIs not yet integrated)")
            report_info = esg_analyzer.find_esg_report(brand)
        
        if report_info['found']:
            print(f"ESG report found for {brand}")
            if report_info['accessible']:
                print(f"Report is accessible and can be analyzed")
                report_analysis = esg_analyzer.analyze_report_with_gemini(report_info['content'])
                return report_analysis
            else:
                print(f"Report found but is not accessible")
                news_summary = esg_analyzer.search_and_summarize_sustainability_news(brand)
                return news_summary
        else:
            print(f"No ESG report found for {brand}")
            news_summary = esg_analyzer.search_and_summarize_sustainability_news(brand)
            return news_summary
    except Exception as e:
        print(f"Error analyzing ESG data: {e}")
        return {"rating": 0, "summary": f"Error analyzing sustainability data for {brand}. {str(e)}"}

def query_textile_db(materials, use_mock_data=False):
    print("\n=== Step 3: Querying Textile Database for material impact. ===")
    db_query = TextileDBQuery()
    
    print("Using Textile Database Scorecard PFMM data and detailed material CSV files")
    
    material_impacts = {}
    materials_identified = False
    
    for material, percentage in materials.items():
        print(f"Looking up material: {material} ({percentage}%)")
        impact_data = db_query.query_material(material)
        if impact_data:
            materials_identified = True
            material_impacts[material] = impact_data
            print(f"Found impact data for {material}")
            
            # Show category and sustainability metrics
            category = impact_data.get('category', 'Unknown')
            print(f"  - Category: {category}")
            
            # Show impact scores
            if 'overall_impact' in impact_data:
                overall = impact_data['overall_impact']
                print(f"  - Impact areas:")
                for area, score in overall.items():
                    print(f"    - {area.capitalize()}: {score:.1f}/100")
                
            # Show certification info
            cert_count = len(impact_data.get('certifications', []))
            print(f"  - Found {cert_count} certification options")
            
            if cert_count > 0:
                top_cert = impact_data['certifications'][0]['certification']
                print(f"  - Top certification: {top_cert}")
            
            # Show detailed data if available
            if 'detailed_data' in impact_data:
                print(f"  - Detailed data available:")
                
                if 'available_certifications' in impact_data['detailed_data']:
                    cert_count = len(impact_data['detailed_data']['available_certifications'])
                    print(f"    - Found {cert_count} certification standards in detailed data")
                
                if 'performance_scores' in impact_data['detailed_data']:
                    perf_scores = impact_data['detailed_data']['performance_scores']
                    if perf_scores:
                        print("    - Detailed performance scores:")
                        for area, scores in perf_scores.items():
                            print(f"      - {area.capitalize()}: {scores['average']:.1f}/100")
                
                if 'detailed_scores' in impact_data['detailed_data']:
                    detailed_scores = impact_data['detailed_data']['detailed_scores']
                    if detailed_scores:
                        print("    - Key subcategory performance:")
                        # Get a few key areas to display
                        key_areas = []
                        for area, subcats in detailed_scores.items():
                            if subcats:
                                # Sort subcategories by highest score
                                sorted_subcats = sorted(subcats.items(), key=lambda x: x[1]['average'], reverse=True)
                                if sorted_subcats:
                                    key_areas.append((area, sorted_subcats[0]))
                        
                        # Display top 3 key areas
                        for area, (subcat, data) in key_areas[:3]:
                            print(f"      - {area.capitalize()}: {subcat} ({data['average']:.1f}/100)")
        else:
            print(f"No impact data found for {material}")
    
    if materials_identified:
        # Handle blends if multiple materials
        if len(materials) > 1:
            print("Product contains a blend of materials")
            blend_data = db_query.process_blend(materials, material_impacts)
            
            print("Blend composition:")
            for material, pct in materials.items():
                print(f"  - {material}: {pct:.1f}")
            
            # Show weighted impact scores
            if 'overall_weighted_impact' in blend_data:
                weighted = blend_data['overall_weighted_impact']
                print("Weighted impact scores:")
                for area, score in weighted.items():
                    print(f"  - {area.capitalize()}: {score:.1f}/100")
            
            # Show sustainability rating
            if 'sustainability_rating' in blend_data:
                rating = blend_data['sustainability_rating']
                level = blend_data.get('sustainability_level', '')
                print(f"Sustainability rating: {rating:.1f}/10 ({level})")
            
            # Show blend detailed data if available
            if 'detailed_weighted_data' in blend_data:
                print("Detailed weighted data available for blend")
                detailed = blend_data['detailed_weighted_data']
                if detailed:
                    area = next(iter(detailed))
                    print(f"Sample data for {area}:")
                    subcats = list(detailed[area].items())[:3]  # Show top 3 subcategories
                    for subcat, score in subcats:
                        print(f"  - {subcat}: {score:.1f}/100")
            
            return {
                "identified": True,
                "is_blend": True,
                "blend_composition": materials,
                "impacts": {
                    **blend_data,
                    "materials": material_impacts,
                    "overall": blend_data.get("sustainability_rating", 5.0)
                }
            }
        else:
            # Single material
            material = next(iter(materials.keys()))
            impact_data = material_impacts[material]
            
            # Calculate overall sustainability score
            if 'overall_impact' in impact_data:
                scores = list(impact_data['overall_impact'].values())
                if scores:
                    avg_score = sum(scores) / len(scores)
                    sustainability_score = avg_score / 10.0  # Convert from 0-100 to 0-10 scale
                else:
                    sustainability_score = 5.0
            else:
                sustainability_score = 5.0
                
            print(f"Overall sustainability score: {sustainability_score:.1f}/10")
            
            return {
                "identified": True,
                "is_blend": False,
                "material": material,
                "impacts": {
                    **impact_data,
                    "overall": sustainability_score
                }
            }
    else:
        print("Unable to identify material impacts")
        return {
            "identified": False,
            "error": "No material impacts found in database"
        }

def scrape_reviews(url, use_mock=False, oxylabs_username=None, oxylabs_password=None):
    print("\n=== Step 5: Scraping Consumer Reviews ===")
    
    try:
        scraper = AmazonScraper(
            use_real_scraping=not use_mock,
            oxylabs_username=oxylabs_username,
            oxylabs_password=oxylabs_password
        )
        
        reviews = scraper.scrape_reviews(url)
        print(f"Successfully retrieved {len(reviews)} reviews")
        return reviews
    except Exception as e:
        print(f"Error scraping reviews: {e}")
        return []

def analyze_reviews(reviews, gemini_api_key=None, use_mock=False):
    print("\n=== Step 6: Analyzing Consumer Reviews for sustainability insights. ===")
    
    if not reviews:
        print("No reviews to analyze")
        return {
            "overall_sustainability_sentiment": 5.0,
            "insights": ["No consumer reviews available for analysis"]
        }
    
    try:
        analyzer = ReviewAnalyzer(gemini_api_key=gemini_api_key, use_mock_api=use_mock)
        analysis = analyzer.analyze_with_gemini(reviews)
        
        print(f"Overall sustainability sentiment: {analysis['overall_sustainability_sentiment']}/10")
        print("Key insights:")
        for insight in analysis["insights"]:
            print(f"  - {insight}")
            
        if analysis.get("flags_triggered", False):
            print("Sustainability flags triggered:")
            for flag in analysis.get("sustainability_flags", []):
                print(f"  - {flag}")
        
        return analysis
    except Exception as e:
        print(f"Error analyzing reviews: {e}")
        return {
            "overall_sustainability_sentiment": 5.0,
            "insights": [f"Error analyzing reviews: {str(e)}"]
        }

def synthesize_data(material_data, brand_assessment, consumer_feedback, depth):
    print("\n=== Step 7: Synthesizing Data ===")
    
    # Collect all data sources
    synthesized_data = {
        "material_impact": material_data,
        "brand_assessment": brand_assessment,
        "consumer_feedback": consumer_feedback,
        "assessment_depth": depth
    }
    
    # Log key information
    if material_data.get("identified", False):
        if material_data.get("is_blend", False):
            materials_str = ", ".join([f"{int(pct*100)}% {mat}" for mat, pct in material_data.get("blend_composition", {}).items()])
            print(f"Material: Blend of {materials_str}")
        else:
            print(f"Material: {material_data.get('material', 'Unknown')}")
            
        if "impacts" in material_data and "overall" in material_data["impacts"]:
            print(f"Material sustainability score: {material_data['impacts']['overall']:.1f}/10")
    else:
        print("Material: Unable to identify material impacts")
    
    print(f"Brand sustainability rating: {brand_assessment.get('rating', 0.0):.1f}/10")
    print(f"Consumer sentiment rating: {consumer_feedback.get('overall_sustainability_sentiment', 0.0):.1f}/10")
    
    # Set weights based on assessment depth
    weights = {
        "basic": {
            "material_impact": 0.8,
            "brand_assessment": 0.15,
            "consumer_feedback": 0.05
        },
        "standard": {
            "material_impact": 0.5,
            "brand_assessment": 0.3,
            "consumer_feedback": 0.2
        },
        "comprehensive": {
            "material_impact": 0.4,
            "brand_assessment": 0.35,
            "consumer_feedback": 0.25
        }
    }
    
    current_weights = weights.get(depth, weights["standard"])
    print(f"Using assessment weights for '{depth}' depth:")
    for component, weight in current_weights.items():
        print(f"  - {component}: {weight*100:.0f}%")
        
    # Calculate weighted score
    material_score = material_data["impacts"]["overall"] if material_data.get("identified", False) and "impacts" in material_data else 5.0
    brand_score = brand_assessment.get("rating", 5.0)
    consumer_score = consumer_feedback.get("overall_sustainability_sentiment", 5.0)
    
    overall_score = (
        material_score * current_weights["material_impact"] +
        brand_score * current_weights["brand_assessment"] +
        consumer_score * current_weights["consumer_feedback"]
    )
    
    print(f"Overall weighted sustainability score: {overall_score:.1f}/10")
    
    synthesized_data["overall_score"] = overall_score
    
    return synthesized_data

def generate_final_report(synthesized_data):
    print("\n=== Step 8: Generating Final Report ===")
    
    report_generator = ReportGenerator()
    
    # Choose report type based on assessment depth
    assessment_depth = synthesized_data.get("assessment_depth", "standard")
    if assessment_depth == "comprehensive":
        print("Generating comprehensive report with detailed impact breakdowns")
        report = report_generator.generate_comprehensive_report(synthesized_data)
    else:
        print(f"Generating {assessment_depth} report")
        report = report_generator.interpret_and_summarize(synthesized_data)
    
    # Display report summary
    print("\n=== Final Sustainability Assessment ===")
    print(f"Overall Rating: {report['rating']}/10 ({report['rating_band']})")
    print(f"Summary: {report['summary']}")
    
    # Display component scores
    if "component_scores" in report:
        print("\nComponent Scores:")
        for component, score in report["component_scores"].items():
            print(f"- {component.capitalize()}: {score:.1f}/10")
    
    # Display key insights
    print("\nKey Material Insights:")
    for insight in report.get("material_insights", [])[:3]:
        print(f"- {insight}")
        
    print("\nKey Brand Insights:")
    for insight in report.get("brand_insights", [])[:2]:
        print(f"- {insight}")
        
    print("\nKey Consumer Insights:")
    for insight in report.get("consumer_insights", [])[:2]:
        print(f"- {insight}")
    
    # Show certification recommendations
    if "detailed_assessment" in report and "certifications" in report["detailed_assessment"]:
        print("\nRecommended Certifications:")
        for cert in report["detailed_assessment"]["certifications"][:2]:
            print(f"- {cert['name']} (Score: {cert['average_score']}/100)")
    
    # Display category-specific insights for comprehensive reports
    if "category_specific_insights" in report:
        print("\nMaterial-Specific Insights:")
        for insight in report["category_specific_insights"]:
            print(f"- {insight}")
    
    # Show identified conflicts
    if "conflicts" in report and report["conflicts"]:
        print("\nSustainability Conflicts/Tradeoffs:")
        for conflict in report["conflicts"]:
            print(f"- {conflict}")
    
    return report

def main():
    """Main workflow function."""
    args = parse_args()
    args = initialize(args)
    
    # Step 2: Product scraping
    product_data = scrape_product(
        args.url, 
        use_mock=args.mock_scraping,
        oxylabs_username=args.oxylabs_username,
        oxylabs_password=args.oxylabs_password
    )
    
    # Step 3: Material analysis
    materials = analyze_material(
        product_data, 
        gemini_api_key=args.gemini_api_key,
        use_mock=args.mock_llm
    )
    
    # Step 4: Textile database lookup
    material_impact = query_textile_db(
        materials,
        use_mock_data=args.mock_data
    )
    
    # Step 5: Brand ESG analysis
    brand_assessment = search_esg_report(
        product_data["brand"],
        gemini_api_key=args.gemini_api_key,
        use_mock=args.mock_llm,
        use_mock_data=args.mock_data
    )
    
    # Step 6: Review analysis
    reviews = scrape_reviews(
        args.url,
        use_mock=args.mock_scraping,
        oxylabs_username=args.oxylabs_username,
        oxylabs_password=args.oxylabs_password
    )
    
    consumer_feedback = analyze_reviews(
        reviews,
        gemini_api_key=args.gemini_api_key,
        use_mock=args.mock_llm
    )
    
    # Step 7: Data synthesis
    synthesized_data = synthesize_data(
        material_impact,
        brand_assessment,
        consumer_feedback,
        args.depth
    )
    
    # Step 8: Report generation
    final_report = generate_final_report(synthesized_data)
    
    return final_report

if __name__ == "__main__":
    main() 