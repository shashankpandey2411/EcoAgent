import random
from typing import Dict, Any, List


class ReportGenerator:
    """
    Generates final reports based on synthesized sustainability data.
    Includes methods to interpret data, resolve conflicts, and create
    an overall assessment.
    """
    
    def __init__(self):
        """Initialize the report generator with weighting factors."""
        # Weighting factors for different assessment depths
        self.depth_weights = {
            # Basic assessment - focuses primarily on materials
            "basic": {
                "material_impact": 0.8,
                "brand_assessment": 0.15,
                "consumer_feedback": 0.05
            },
            # Standard assessment - balanced approach
            "standard": {
                "material_impact": 0.5,
                "brand_assessment": 0.3,
                "consumer_feedback": 0.2
            },
            # Comprehensive assessment - considers all factors more equally
            "comprehensive": {
                "material_impact": 0.4,
                "brand_assessment": 0.35,
                "consumer_feedback": 0.25
            }
        }
        
        # Thresholds for rating bands
        self.rating_thresholds = {
            9.0: "Excellent",
            8.0: "Very Good",
            7.0: "Good",
            6.0: "Above Average",
            5.0: "Average",
            4.0: "Below Average",
            3.0: "Poor",
            0.0: "Very Poor"
        }
        
        # Common sustainability trade-offs and conflicts
        self.common_conflicts = {
            "recycled_durability": "Recycled materials may have lower durability, affecting product lifespan",
            "organic_impact": "Organic production can use more land and water than conventional methods",
            "local_vs_certified": "Local production may have lower transport emissions but lack certifications",
            "natural_synthetic": "Natural fibers have better biodegradability but often higher water and land use",
            "brand_vs_material": "A brand may have strong sustainability commitments but use less sustainable materials",
            "consumer_vs_metrics": "Consumer perceptions may conflict with technical sustainability metrics"
        }
        
        # Impact area priorities for different material categories
        self.material_priorities = {
            "Cotton": ["water", "land", "chemistry", "climate", "human_rights"],
            "Synthetic": ["climate", "resource", "chemistry", "water"],
            "Wool": ["animal_welfare", "land", "climate", "biodiversity", "human_rights"],
            "MMCF": ["land", "climate", "water", "chemistry"],
            "Flax": ["land", "biodiversity", "climate", "water"]
        }
    
    def interpret_and_summarize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret synthesized data and generate a final sustainability assessment.
        """
        # Get assessment depth and corresponding weights
        depth = data.get("assessment_depth", "standard")
        weights = self.depth_weights.get(depth, self.depth_weights["standard"])
        
        # Extract component data
        material_impact = data.get("material_impact", {})
        brand_assessment = data.get("brand_assessment", {})
        consumer_feedback = data.get("consumer_feedback", {})
        
        # Calculate material impact score
        material_score = 0.0
        material_insights = []
        
        if material_impact.get("identified", False):
            material_data = material_impact.get("impacts", {})
            if isinstance(material_data, dict) and material_data.get("overall"):
                material_score = material_data.get("overall", 5.0)
                
                # Generate insights based on strongest and weakest categories
                categories = []
                for cat, score in material_data.items():
                    if cat != "overall" and isinstance(score, (int, float)):
                        categories.append((cat, score))
                
                if categories:
                    # Now sort only numeric category scores
                    categories.sort(key=lambda x: x[1], reverse=True)
                    
                    top_category = categories[0]
                    bottom_category = categories[-1]
                    
                    material_insights.append(
                        f"Material strength: {top_category[0].replace('_', ' ')} ({top_category[1]}/10)"
                    )
                    material_insights.append(
                        f"Material concern: {bottom_category[0].replace('_', ' ')} ({bottom_category[1]}/10)"
                    )
                    
                    if "blend_composition" in material_impact:
                        blend = material_impact["blend_composition"]
                        materials_list = ", ".join(f"{int(pct*100)}% {mat}" for mat, pct in blend.items())
                        material_insights.append(f"Material composition: {materials_list}")
                        
                # Add detailed insights from the detailed data if available
                if "detailed_data" in material_data:
                    detailed_insights = self._generate_detailed_material_insights(material_data["detailed_data"])
                    material_insights.extend(detailed_insights)
                
                # Add certification recommendations if available
                if "certifications" in material_data:
                    top_cert = material_data["certifications"][0]["certification"] if material_data["certifications"] else None
                    if top_cert:
                        material_insights.append(f"Recommended certification: {top_cert}")
        else:
            material_score = 5.0  # Default score if materials not identified
            material_insights.append("Unable to identify specific material impacts")
        
        # Calculate brand assessment score
        brand_score = brand_assessment.get("rating", 5.0)
        brand_insights = []
        
        if "summary" in brand_assessment:
            brand_insights.append(brand_assessment["summary"])
        
        if brand_assessment.get("has_specific_targets", False):
            brand_insights.append("Brand has published specific sustainability targets")
        
        if brand_assessment.get("has_certifications", False):
            brand_insights.append("Brand uses recognized sustainability certifications")
        
        if brand_assessment.get("has_criticism", False):
            brand_insights.append("Brand has faced criticism about sustainability claims")
        
        # Calculate consumer feedback score
        consumer_score = consumer_feedback.get("overall_sustainability_sentiment", 5.0)
        consumer_insights = []
        
        if consumer_feedback.get("insights"):
            consumer_insights.extend(consumer_feedback["insights"])
        
        if consumer_feedback.get("flags_triggered", False):
            flags = consumer_feedback.get("sustainability_flags", [])
            formatted_flags = [flag.replace("_", " ").capitalize() for flag in flags]
            consumer_insights.append(f"Consumer concerns: {', '.join(formatted_flags)}")
        
        # Calculate weighted overall score
        overall_score = (
            material_score * weights["material_impact"] +
            brand_score * weights["brand_assessment"] +
            consumer_score * weights["consumer_feedback"]
        )
        
        # Round to one decimal place
        overall_score = round(overall_score, 1)
        
        # Determine rating band
        rating_band = next((label for threshold, label in sorted(
            self.rating_thresholds.items(), 
            key=lambda x: x[0], 
            reverse=True
        ) if overall_score >= threshold), "Not Rated")
        
        # Identify potential conflicts
        conflicts = []
        
        # Check for material vs brand conflicts
        if abs(material_score - brand_score) > 3:
            if material_score > brand_score:
                conflicts.append("Material sustainability appears stronger than brand's overall practices")
            else:
                conflicts.append("Brand's sustainability initiatives outpace the specific materials used")
        
        # Check for perception vs reality conflicts
        if abs(consumer_score - ((material_score + brand_score) / 2)) > 3:
            if consumer_score > ((material_score + brand_score) / 2):
                conflicts.append("Consumer perception is more positive than technical assessment")
            else:
                conflicts.append("Technical assessment is more positive than consumer perception")
        
        # Add a relevant common conflict if appropriate
        if conflicts and random.random() < 0.7:
            conflicts.append(random.choice(list(self.common_conflicts.values())))
        
        # Generate overall summary based on score and insights
        summary_components = []
        
        # Overall assessment
        summary_components.append(f"This product achieves a {rating_band.lower()} sustainability rating ({overall_score}/10).")
        
        # Top material insight
        if material_insights:
            summary_components.append(material_insights[0])
            
        # Primary brand statement
        if brand_insights:
            summary_components.append(brand_insights[0])
            
        # Consumer perception
        if consumer_insights:
            summary_components.append(consumer_insights[0])
            
        # Leading conflict or challenge
        if conflicts:
            summary_components.append(f"Note: {conflicts[0]}.")
        
        # Recommendation based on score
        if overall_score >= 7.0:
            summary_components.append("This product demonstrates strong sustainability credentials.")
        elif overall_score >= 5.0:
            summary_components.append("This product has moderate sustainability features but room for improvement.")
        else:
            summary_components.append("This product has significant sustainability concerns.")
        
        # Join summary components
        summary = " ".join(summary_components)
        
        result = {
            "rating": overall_score,
            "rating_band": rating_band,
            "summary": summary,
            "component_scores": {
                "material": material_score,
                "brand": brand_score,
                "consumer": consumer_score
            },
            "material_insights": material_insights,
            "brand_insights": brand_insights,
            "consumer_insights": consumer_insights,
            "conflicts": conflicts,
            "assessment_depth": depth
        }
        
        # Add detailed sections if assessment depth is comprehensive
        if depth == "comprehensive" and material_impact.get("identified", False):
            material_data = material_impact.get("impacts", {})
            if "detailed_data" in material_data:
                result["detailed_assessment"] = self._generate_detailed_assessment(material_data)
        
        return result
    
    def _generate_detailed_material_insights(self, detailed_data: Dict[str, Any]) -> List[str]:
        """
        Generate insights from detailed material data.
        """
        insights = []
        
        # Extract top certifications
        if "available_certifications" in detailed_data:
            certs = detailed_data["available_certifications"]
            if certs and len(certs) > 0:
                top_cert = certs[0]
                insights.append(f"Top certification standard: {top_cert}")
        
        # Extract performance highlights
        if "performance_scores" in detailed_data:
            perf_scores = detailed_data["performance_scores"]
            # Sort by highest score
            sorted_areas = sorted(perf_scores.items(), key=lambda x: x[1]["average"], reverse=True)
            if sorted_areas:
                top_area = sorted_areas[0]
                area_name = top_area[0].replace('_', ' ').capitalize()
                score = round(top_area[1]["average"], 1)
                insights.append(f"Best performing impact area: {area_name} ({score}/100)")
        
        # Extract highlight from detailed scores
        if "detailed_scores" in detailed_data:
            detail_scores = detailed_data["detailed_scores"]
            for area, subcategories in detail_scores.items():
                area_name = area.replace('_', ' ').capitalize()
                # Find highest scoring subcategory
                if subcategories:
                    sorted_subcats = sorted(subcategories.items(), key=lambda x: x[1]["average"], reverse=True)
                    if sorted_subcats:
                        top_subcat = sorted_subcats[0]
                        subcat_name = top_subcat[0]
                        score = round(top_subcat[1]["average"], 1)
                        if score > 50:  # Only include high scores
                            insights.append(f"Strong {area_name} performance in: {subcat_name} ({score}/100)")
                        break  # Only include one detailed insight to avoid overwhelming
        
        return insights[:3]  # Limit the number of insights
    
    def _generate_detailed_assessment(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a detailed assessment section for comprehensive reports.   
        """
        assessment = {
            "material_category": material_data.get("category", "Unknown"),
            "impact_areas": {},
            "certifications": [],
            "recommendations": []
        }
        
        # Process impact areas
        if "detailed_data" in material_data and "performance_scores" in material_data["detailed_data"]:
            performance = material_data["detailed_data"]["performance_scores"]
            material_category = material_data.get("category", "Unknown")
            
            # Get priority areas for this material type
            priority_areas = self.material_priorities.get(material_category, [])
            
            # Process each area
            for area, scores in performance.items():
                priority = priority_areas.index(area) + 1 if area in priority_areas else len(priority_areas) + 1
                area_data = {
                    "name": area.replace('_', ' ').capitalize(),
                    "average_score": round(scores["average"], 1),
                    "min_score": round(scores["min"], 1),
                    "max_score": round(scores["max"], 1),
                    "priority_for_material": priority
                }
                
                # Add detailed subcategory data if available
                if "detailed_scores" in material_data["detailed_data"] and area in material_data["detailed_data"]["detailed_scores"]:
                    area_data["subcategories"] = []
                    subcats = material_data["detailed_data"]["detailed_scores"][area]
                    
                    for subcat_name, subcat_data in subcats.items():
                        area_data["subcategories"].append({
                            "name": subcat_name,
                            "score": round(subcat_data["average"], 1)
                        })
                    
                    # Sort subcategories by score
                    area_data["subcategories"].sort(key=lambda x: x["score"], reverse=True)
                
                assessment["impact_areas"][area] = area_data
            
            # Sort impact areas by priority for material type
            assessment["sorted_impact_areas"] = sorted(
                assessment["impact_areas"].items(),
                key=lambda x: x[1]["priority_for_material"]
            )
        
        # Add certification data
        if "certifications" in material_data:
            for cert in material_data["certifications"]:
                cert_name = cert["certification"]
                # Calculate average score across impact areas
                scores = [score["score"] for score in cert["impact_scores"].values()]
                avg_score = sum(scores) / len(scores) if scores else 0
                
                assessment["certifications"].append({
                    "name": cert_name,
                    "average_score": round(avg_score, 1),
                    "impact_areas": cert["impact_scores"]
                })
            
            # Sort certifications by score
            assessment["certifications"].sort(key=lambda x: x["average_score"], reverse=True)
        
        # Add recommendations
        if "baseline" in material_data and assessment["certifications"]:
            baseline = material_data["baseline"]
            top_cert = assessment["certifications"][0]
            
            for area, cert_score in top_cert["impact_areas"].items():
                if area in baseline:
                    baseline_score = baseline[area]
                    cert_area_score = cert_score["score"]
                    
                    if cert_area_score > baseline_score + 20:  # Significant improvement
                        area_name = area.replace('_', ' ').capitalize()
                        improvement = round(cert_area_score - baseline_score, 1)
                        assessment["recommendations"].append({
                            "area": area_name,
                            "certification": top_cert["name"],
                            "improvement": improvement,
                            "message": f"Using {top_cert['name']} would improve {area_name} score by {improvement} points"
                        })
            
            # Sort recommendations by improvement magnitude
            assessment["recommendations"].sort(key=lambda x: x["improvement"], reverse=True)
        
        return assessment
    
    def generate_comprehensive_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a more comprehensive report with detailed impact area breakdowns.
        """
        # First get the standard assessment
        assessment = self.interpret_and_summarize(data)
        
        # Add material type-specific insights
        material_impact = data.get("material_impact", {})
        if material_impact.get("identified", False):
            material_data = material_impact.get("impacts", {})
            
            if "category" in material_data:
                material_category = material_data["category"]
                material_priorities = self.material_priorities.get(material_category, [])
                
                # Add category-specific recommendations
                category_specific = self._get_category_specific_insights(material_category, material_data)
                assessment["category_specific_insights"] = category_specific
                
                # Add priority impact areas
                if material_priorities:
                    assessment["priority_impact_areas"] = [area.replace('_', ' ').capitalize() for area in material_priorities[:3]]
                
                # Add key environmental indicators
                if "detailed_data" in material_data:
                    indicators = self._extract_key_environmental_indicators(material_category, material_data["detailed_data"])
                    if indicators:
                        assessment["key_environmental_indicators"] = indicators
        
        # Add detailed certification analysis if available
        if material_impact.get("identified", False) and "certifications" in material_impact.get("impacts", {}):
            material_data = material_impact["impacts"]
            cert_analysis = self._analyze_certifications(material_data)
            if cert_analysis:
                assessment["certification_analysis"] = cert_analysis
        
        return assessment
    
    def _get_category_specific_insights(self, category: str, material_data: Dict[str, Any]) -> List[str]:
        """
        Get insights specific to a material category.
        """
        insights = []
        
        if category == "Cotton":
            insights.append("Cotton is a water-intensive crop; certified organic and recycled options reduce impact")
            
            # Add water use insights if available
            if "detailed_data" in material_data and "detailed_scores" in material_data["detailed_data"]:
                if "water" in material_data["detailed_data"]["detailed_scores"]:
                    water_data = material_data["detailed_data"]["detailed_scores"]["water"]
                    if "Water Risk Management" in water_data:
                        score = water_data["Water Risk Management"]["average"]
                        if score < 40:
                            insights.append("Water management practices for this cotton product show significant room for improvement")
                        elif score > 60:
                            insights.append("This cotton product demonstrates strong water management practices")
        
        elif category == "Synthetic":
            insights.append("Synthetic fibers are derived from fossil fuels; recycled alternatives reduce carbon impact")
            
            # Add resource use insights if available
            if "detailed_data" in material_data and "detailed_scores" in material_data["detailed_data"]:
                if "resource" in material_data["detailed_data"]["detailed_scores"]:
                    resource_data = material_data["detailed_data"]["detailed_scores"]["resource"]
                    if "Consumption Through Feedstock Selection" in resource_data:
                        score = resource_data["Consumption Through Feedstock Selection"]["average"]
                        if score < 30:
                            insights.append("This product uses virgin synthetic materials with high environmental impact")
                        elif score > 60:
                            insights.append("This product uses recycled synthetic materials, significantly reducing impact")
        
        elif category == "Wool":
            insights.append("Wool production impacts include animal welfare, land use, and methane emissions")
            
            # Add animal welfare insights if available
            if "detailed_data" in material_data and "detailed_scores" in material_data["detailed_data"]:
                if "animal_welfare" in material_data["detailed_data"]["detailed_scores"]:
                    welfare_data = material_data["detailed_data"]["detailed_scores"]["animal_welfare"]
                    if "Animal Welfare Management" in welfare_data:
                        score = welfare_data["Animal Welfare Management"]["average"]
                        if score < 40:
                            insights.append("Animal welfare practices for this wool product show significant room for improvement")
                        elif score > 60:
                            insights.append("This wool product demonstrates strong animal welfare practices")
        
        elif category == "MMCF":
            insights.append("Man-made cellulosic fibers (like viscose) carry deforestation risks if not properly sourced")
            
            # Add land use insights if available
            if "detailed_data" in material_data and "detailed_scores" in material_data["detailed_data"]:
                if "land" in material_data["detailed_data"]["detailed_scores"]:
                    land_data = material_data["detailed_data"]["detailed_scores"]["land"]
                    if "Deforestation" in land_data:
                        score = land_data["Deforestation"]["average"]
                        if score < 40:
                            insights.append("This MMCF product shows significant deforestation risk")
                        elif score > 60:
                            insights.append("This MMCF product demonstrates strong forest protection practices")
        
        elif category == "Flax":
            insights.append("Flax (linen) typically requires fewer pesticides and less water than cotton")
            
            # Add chemistry insights if available
            if "detailed_data" in material_data and "detailed_scores" in material_data["detailed_data"]:
                if "chemistry" in material_data["detailed_data"]["detailed_scores"]:
                    chem_data = material_data["detailed_data"]["detailed_scores"]["chemistry"]
                    if "Chemical Management Practices" in chem_data:
                        score = chem_data["Chemical Management Practices"]["average"]
                        if score < 30:
                            insights.append("Chemical management for this flax product shows room for improvement")
                        elif score > 60:
                            insights.append("This flax product demonstrates strong chemical management practices")
        
        return insights
    
    def _extract_key_environmental_indicators(self, category: str, detailed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key environmental indicators from detailed data.
        """
        indicators = {}
        
        # Define key indicators by material category
        key_indicator_map = {
            "Cotton": {
                "water": ["Water Risk Management", "Water Monitoring (Withdrawal and Consumption)"],
                "chemistry": ["Chemical Management Practices"],
                "land": ["Soil Health Management"]
            },
            "Synthetic": {
                "climate": ["Emission Management", "Climate Mitigation"],
                "resource": ["Consumption Through Feedstock Selection"],
                "chemistry": ["Chemical Management Practices"]
            },
            "Wool": {
                "animal_welfare": ["Animal Welfare Management", "Living Environment"],
                "land": ["Soil Health Management", "Rangeland Management for animal fibers"],
                "climate": ["Emission Management"]
            },
            "MMCF": {
                "land": ["Deforestation", "Land Management Planning"],
                "water": ["Water Risk Management"],
                "chemistry": ["Chemical Management Procedures"]
            },
            "Flax": {
                "land": ["Soil Health Management"],
                "biodiversity": ["Biodiversity Management Planning"],
                "chemistry": ["Chemical Management Practices"]
            }
        }
        
        # Get indicators for this category
        category_indicators = key_indicator_map.get(category, {})
        
        if "detailed_scores" in detailed_data:
            scores = detailed_data["detailed_scores"]
            
            for area, subcategories in category_indicators.items():
                if area in scores:
                    area_data = scores[area]
                    area_indicators = {}
                    
                    for subcat in subcategories:
                        if subcat in area_data:
                            area_indicators[subcat] = {
                                "score": round(area_data[subcat]["average"], 1),
                                "min": round(area_data[subcat]["min"], 1),
                                "max": round(area_data[subcat]["max"], 1)
                            }
                    
                    if area_indicators:
                        indicators[area] = area_indicators
        
        return indicators
    
    def _analyze_certifications(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze certifications for a material.
        """
        if "certifications" not in material_data or not material_data["certifications"]:
            return None
        
        analysis = {
            "top_certification": material_data["certifications"][0]["certification"],
            "certification_count": len(material_data["certifications"]),
            "certification_comparison": []
        }
        
        # Get baseline data for comparison
        baseline_data = material_data.get("baseline", {})
        
        # Compare top certifications to baseline
        top_certs = material_data["certifications"][:3]  # Top 3 certifications
        
        for cert in top_certs:
            cert_name = cert["certification"]
            improvements = {}
            
            for area, score_data in cert["impact_scores"].items():
                if area in baseline_data:
                    baseline_score = baseline_data[area]
                    cert_score = score_data["score"]
                    improvement = cert_score - baseline_score
                    
                    if abs(improvement) > 5:  # Only include significant differences
                        improvements[area] = round(improvement, 1)
            
            if improvements:
                analysis["certification_comparison"].append({
                    "certification": cert_name,
                    "improvements": improvements
                })
        
        return analysis
