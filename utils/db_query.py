"""
Database query utilities for accessing the Textile Database Scorecard data.
Provides methods to query material sustainability data based on the 
Preferred Fiber and Material Matrix (PFMM).
"""
import os
import pandas as pd
import re
from typing import Dict, List, Any, Optional

class TextileDBQuery:
    """
    Query interface for the Textile Database Scorecard.
    Provides methods to look up sustainability data for materials and certifications.
    """
    
    def __init__(self, db_path=None):
        """
        Initialize the TextileDBQuery with the scorecard data.
        """
        # Use provided path or default to TextileDataScorecard.csv
        self.project_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Assumes script is nested (e.g., project/src/script.py or project/src/utils/script.py)
        self.data_dir = os.path.join(self.project_root_dir, 'data')
        self.db_path = db_path or os.path.join(self.data_dir, 'TextileDataScorecard.csv')
        self.textile_data = self._load_textile_data()
        
        # Load detailed data for each textile category
        self.detailed_data = {}
        self._load_detailed_data()
        
        # Material mapping from common names to categories in the database
        self.material_map = {
            "cotton": "Cotton",
            "polyester": "Synthetic",
            "nylon": "Synthetic",
            "polyamide": "Synthetic",
            "acrylic": "Synthetic",
            "elastane": "Synthetic",
            "spandex": "Synthetic",
            "wool": "Wool",
            "cashmere": "Wool",
            "mohair": "Wool",
            "alpaca": "Wool",
            "viscose": "MMCF",
            "rayon": "MMCF",
            "modal": "MMCF",
            "lyocell": "MMCF",
            "tencel": "MMCF",
            "acetate": "MMCF",
            "bamboo": "MMCF",
            "linen": "Flax",
            "flax": "Flax"
        }
        
        # Impact area mapping for better readability
        self.impact_areas = {
            "climate": {"col_level": 2, "col_score": 3},
            "water": {"col_level": 4, "col_score": 5},
            "chemistry": {"col_level": 6, "col_score": 7},
            "land": {"col_level": 8, "col_score": 9},
            "biodiversity": {"col_level": 10, "col_score": 11},
            "resource": {"col_level": 12, "col_score": 13},
            "human_rights": {"col_level": 14, "col_score": 15},
            "animal_welfare": {"col_level": 16, "col_score": 17},
            "integrity": {"col_level": 18, "col_score": 19}
        }
        
        # Detailed impact categories for each area
        self.detailed_impact_categories = {
            "climate": ["Emission Management", "Emission Monitoring", "Ambitiousness of Emission Strategy", 
                       "Climate Mitigation", "Climate Adaptation", "Protection of Peat Soils and Below-Ground Carbon Stocks", 
                       "Protection of Above-Ground Carbon Stocks", "Evidence of Soil Carbon Sequestration"],
            "water": ["Water Risk Management", "Water Monitoring (Withdrawal and Consumption)", 
                     "Water Monitoring (Contamination)", "Ambitiousness of Water Strategy (Withdrawal and Consumption)", 
                     "Ambitiousness of Water Strategy (Contamination)", "Comprehensiveness of Water Strategy (Withdrawal and Consumption)", 
                     "Comprehensiveness of Water Strategy (Contamination)", "Impacts of Oil and Gas Extraction on Surface and Groundwater"],
            "chemistry": ["Chemical Management Procedures", "Chemical Management Practices", 
                         "Chemical Monitoring", "Ambitiousness of Chemical Strategy", "Comprehensiveness of Chemical Strategy"],
            "land": ["Soil Health Management", "Soil Health Monitoring", "Ambitiousness of Soil Health Strategy", 
                    "Comprehensiveness of Soil Health Strategy", "Land Management Planning", 
                    "Ambitiousness of Land Strategy", "Deforestation", "Land Conversion"],
            "biodiversity": ["Biodiversity Management Planning", "Biodiversity Monitoring", 
                            "Ambitiousness of Biodiversity Strategy", "Habitat and Ecosystem Diversity", 
                            "Habitat Protection and Restoration", "Species and Genetic Diversity", "Attention to Invasive Species"],
            "resource": ["Reducing Waste in Production Processes", "Maximizing Values of Waste Streams", 
                        "Consumption Through Feedstock Selection"],
            "human_rights": ["Wages and working conditions", "Forced Labor", "Child Labor", 
                            "Non-discrimination", "Freedom of Association", "Occupational Health and Safety", 
                            "Livelihoods: predictability and stability of income", "Indigenous peoples and customary land rights", 
                            "Land rights", "Community consultation and engagement", "Enabling environment for human rights realization", 
                            "Grievance and remedy", "Prevention of gender-based discrimination, violence and harassment"],
            "animal_welfare": ["Animal Welfare Management", "Animal Welfare Monitoring", 
                              "Ambitiousness of Animal Welfare Strategy", "Nutrition", "Living Environment", 
                              "Animal Health", "Handling and Transport", "Intensity of Farming System"],
            "integrity": ["Theory of Change", "Standard-setting procedures", "Governance", 
                         "Claims management", "Assurance oversight", "Enforcement mechanism", 
                         "Risk management", "Feedback, Complaints & Grievances", "Monitoring, Evaluation & Learning system"]
        }
        
    def _load_textile_data(self):
        """
        Load the textile database from CSV.
        
        Returns:
            DataFrame containing the textile scorecard data
        """
        try:
            # print(f"Loading textile database from: {self.db_path}")
            df = pd.read_csv(self.db_path)
            # Clean up the dataframe
            # Skip the header rows (first 3 rows are headers)
            df = df.iloc[3:].reset_index(drop=True)
            # Remove any completely empty rows
            df = df.dropna(how='all')
            print(f"Successfully loaded textile database with {len(df)} entries")
            return df
        except Exception as e:
            print(f"Error loading textile database: {e}")
            # Return an empty DataFrame as fallback
            return pd.DataFrame()
    
    def _load_detailed_data(self):
        """
        Load detailed CSV files for each textile category
        """
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_map = {
            "Cotton": "CottonData.csv",
            "Synthetic": "SyntheticData.csv",
            "Flax": "FlaxData.csv",
            "MMCF": "MMCFData.csv",
            "Wool": "WoolData.csv"
        }
        
        for category, filename in file_map.items():
            file_path = os.path.join(self.data_dir, filename)
            try:
                if os.path.exists(file_path):
                    # print(f"Loading detailed data for {category} from: {file_path}")
                    df = pd.read_csv(file_path)
                    # Skip the header rows (2nd and 3rd rows contain descriptions)
                    # Keep the first row since it contains column headers
                    self.detailed_data[category] = df
                    print(f"Successfully loaded {category} data with {len(df)} rows")
                else:
                    print(f"Detailed data file not found for {category}: {file_path}")
            except Exception as e:
                print(f"Error loading detailed data for {category}: {e}")
                # Continue with other categories if one fails
    
    def _normalize_material_name(self, material_name: str) -> str:
        """
        Normalize a material name to match database categories.
        """
        material_lower = material_name.lower()
        
        # First check for exact matches
        for key, value in self.material_map.items():
            if key == material_lower:
                return value
                
        # Then check for partial matches
        for key, value in self.material_map.items():
            if key in material_lower:
                return value
        
        return None
    
    def _extract_certification_data(self, row) -> Dict[str, Any]:
        """
        Extract certification data from a dataframe row.
        """
        certification = row.iloc[1]
        
        # Skip rows that don't have a certification name
        if pd.isna(certification):
            return None
            
        cert_data = {
            "certification": certification,
            "impact_scores": {}
        }
        
        # Extract impact area scores
        for area, cols in self.impact_areas.items():
            level = row.iloc[cols["col_level"]]
            score = row.iloc[cols["col_score"]]
            
            # Only include areas that have data
            if not pd.isna(level) and not pd.isna(score):
                try:
                    level_num = int(level) if not pd.isna(level) else 0
                    score_num = float(score) if not pd.isna(score) else 0.0
                    cert_data["impact_scores"][area] = {
                        "level": level_num,
                        "score": score_num
                    }
                except (ValueError, TypeError):
                    # If conversion fails, use the original value
                    cert_data["impact_scores"][area] = {
                        "level": level if not pd.isna(level) else 0,
                        "score": score if not pd.isna(score) else 0.0
                    }
        
        return cert_data
    
    def query_material(self, material_name: str) -> Dict[str, Any]:
        """
        Query the textile database for a specific material.
        """
        if self.textile_data.empty:
            print("Textile database not loaded, returning None")
            return None
            
        # Normalize the material name
        category = self._normalize_material_name(material_name)
        
        if not category:
            print(f"Material '{material_name}' does not match any known category")
            return None
            
        # Get rows for this material category
        material_rows = self.textile_data[self.textile_data.iloc[:, 0] == category]
        
        if material_rows.empty:
            print(f"No data found for material category '{category}'")
            return None
            
        # Get all certifications for this material
        certifications = []
        for _, row in material_rows.iterrows():
            cert_data = self._extract_certification_data(row)
            if cert_data:
                certifications.append(cert_data)
        
        # Build the result structure
        result = {
            "material": material_name,
            "category": category,
            "certifications": certifications,
            "overall_impact": self._calculate_overall_impact(material_rows)
        }
        
        # Add baseline data (material with no standard system)
        baseline_data = self._get_baseline_impact(category)
        if baseline_data:
            result["baseline"] = baseline_data
        
        # Add detailed data if available
        detailed_data = self._get_detailed_data(category, material_name)
        if detailed_data:
            result["detailed_data"] = detailed_data
        
        return result
    
    def _calculate_overall_impact(self, material_rows) -> Dict[str, float]:
        """
        Calculate the overall impact score across all certifications for a material.
        """
        impact_sums = {}
        impact_counts = {}
        
        # Iterate through rows and collect scores
        for _, row in material_rows.iterrows():
            for area, cols in self.impact_areas.items():
                score = row.iloc[cols["col_score"]]
                
                if not pd.isna(score):
                    try:
                        score_num = float(score)
                        impact_sums[area] = impact_sums.get(area, 0) + score_num
                        impact_counts[area] = impact_counts.get(area, 0) + 1
                    except (ValueError, TypeError):
                        # Skip if conversion fails
                        continue
        
        # Calculate averages
        impact_avgs = {}
        for area in impact_sums:
            if impact_counts[area] > 0:
                impact_avgs[area] = impact_sums[area] / impact_counts[area]
        
        return impact_avgs
    
    def _get_baseline_impact(self, material_category: str) -> Dict[str, Any]:
        """
        Get baseline impact data for uncertified materials.
        """
        # Look for rows that mention "no standard system"
        baseline_pattern = f"{material_category} with no standard system"
        baseline_rows = self.textile_data[self.textile_data.iloc[:, 1].str.contains(baseline_pattern, na=False)]
        
        if baseline_rows.empty:
            return None
            
        # Extract impact scores
        baseline_impacts = {}
        for area, cols in self.impact_areas.items():
            scores = []
            
            for _, row in baseline_rows.iterrows():
                score = row.iloc[cols["col_score"]]
                if not pd.isna(score):
                    try:
                        score_num = float(score)
                        scores.append(score_num)
                    except (ValueError, TypeError):
                        continue
            
            if scores:
                baseline_impacts[area] = sum(scores) / len(scores)
        
        return baseline_impacts
    
    def _get_detailed_data(self, category: str, material_name: str) -> Dict[str, Any]:
        """
        Get detailed sustainability data for a material from the category-specific CSV files.
        """
        if category not in self.detailed_data:
            print(f"No detailed data available for category: {category}")
            return None
        
        # Find certifications for this material
        material_df = self.detailed_data[category]
        
        # Extract certification names from Reference column
        cert_data = {}
        cert_data["detailed_scores"] = {}
        
        # For each impact area, extract detailed subcategory scores
        for area, subcategories in self.detailed_impact_categories.items():
            area_data = {}
            
            for subcategory in subcategories:
                # Look for subcategory in columns
                if subcategory in material_df.columns:
                    # Get values for this subcategory
                    values = material_df[subcategory].dropna().tolist()
                    if values:
                        # Convert to float where possible
                        values = [float(v) if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()) else v for v in values]
                        # Only include numerical values
                        numeric_values = [v for v in values if isinstance(v, (int, float))]
                        if numeric_values:
                            area_data[subcategory] = {
                                "average": sum(numeric_values) / len(numeric_values),
                                "min": min(numeric_values),
                                "max": max(numeric_values),
                                "values": numeric_values
                            }
            
            if area_data:
                cert_data["detailed_scores"][area] = area_data
        
        # Get certification details by name
        cert_names = material_df["Reference"].dropna().tolist()
        cert_data["available_certifications"] = cert_names
        
        # Try to find average performance for each impact area
        for area in self.impact_areas.keys():
            area_column = f"Impact area performance %"
            area_cols = [col for col in material_df.columns if area.lower() in col.lower() and "impact area performance" in col.lower()]
            
            if area_cols:
                values = material_df[area_cols[0]].dropna().tolist()
                numeric_values = [float(v) for v in values if isinstance(v, (int, float)) or (isinstance(v, str) and v.replace('.', '', 1).isdigit())]
                
                if numeric_values:
                    if "performance_scores" not in cert_data:
                        cert_data["performance_scores"] = {}
                    
                    cert_data["performance_scores"][area] = {
                        "average": sum(numeric_values) / len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values)
                    }
        
        return cert_data
    
    def process_blend(self, materials_dict: Dict[str, float], material_impacts: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Process a blend of materials to calculate overall impact.
        """
        # Normalize percentages to ensure they sum to 1.0
        total_pct = sum(materials_dict.values())
        if total_pct == 0:
            return {"error": "No valid materials found"}
            
        normalized_pcts = {mat: pct / total_pct for mat, pct in materials_dict.items()}
        
        # Calculate weighted impact scores
        weighted_impacts = {}
        for area in self.impact_areas.keys():
            area_sum = 0.0
            area_count = 0
            
            for material, pct in normalized_pcts.items():
                if material in material_impacts:
                    impact_data = material_impacts[material]
                    if "overall_impact" in impact_data and area in impact_data["overall_impact"]:
                        area_sum += impact_data["overall_impact"][area] * pct
                        area_count += 1
            
            if area_count > 0:
                weighted_impacts[area] = area_sum
        
        # Calculate overall sustainability score (0-10 scale)
        sustainability_score = 0.0
        score_count = 0
        
        # Weights for different impact areas
        area_weights = {
            "climate": 0.20,
            "water": 0.15,
            "chemistry": 0.15,
            "land": 0.10,
            "biodiversity": 0.10,
            "resource": 0.10,
            "human_rights": 0.15,
            "animal_welfare": 0.05
            # integrity not included in sustainability score
        }
        
        for area, weight in area_weights.items():
            if area in weighted_impacts:
                # Convert percentage scores (0-100) to 0-10 scale
                area_score = weighted_impacts[area] / 10.0
                sustainability_score += area_score * weight
                score_count += 1
        
        # If we have no scores, default to 5.0 (medium)
        if score_count == 0:
            sustainability_score = 5.0
            
        # Calculate detailed weighted scores if available
        detailed_weighted_data = self._calculate_detailed_weighted_data(materials_dict, material_impacts)
        
        result = {
            "blend_composition": normalized_pcts,
            "overall_weighted_impact": weighted_impacts,
            "sustainability_rating": sustainability_score,
            "sustainability_level": self._get_sustainability_level(sustainability_score)
        }
        
        if detailed_weighted_data:
            result["detailed_weighted_data"] = detailed_weighted_data
        
        return result
    
    def _calculate_detailed_weighted_data(self, materials_dict: Dict[str, float], material_impacts: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Calculate detailed weighted data for a blend of materials.
        """
        # Normalize percentages to ensure they sum to 1.0
        total_pct = sum(materials_dict.values())
        if total_pct == 0:
            return None
            
        normalized_pcts = {mat: pct / total_pct for mat, pct in materials_dict.items()}
        
        # Collect detailed data from each material
        detailed_data = {}
        
        for material, pct in normalized_pcts.items():
            if material in material_impacts:
                impact_data = material_impacts[material]
                if "detailed_data" in impact_data and "detailed_scores" in impact_data["detailed_data"]:
                    for area, subcategories in impact_data["detailed_data"]["detailed_scores"].items():
                        if area not in detailed_data:
                            detailed_data[area] = {}
                            
                        for subcategory, values in subcategories.items():
                            if subcategory not in detailed_data[area]:
                                detailed_data[area][subcategory] = {
                                    "weighted_sum": 0.0,
                                    "count": 0
                                }
                            
                            if "average" in values:
                                detailed_data[area][subcategory]["weighted_sum"] += values["average"] * pct
                                detailed_data[area][subcategory]["count"] += 1
        
        # Calculate weighted averages
        weighted_results = {}
        
        for area, subcategories in detailed_data.items():
            weighted_results[area] = {}
            
            for subcategory, data in subcategories.items():
                if data["count"] > 0:
                    weighted_results[area][subcategory] = data["weighted_sum"]
        
        return weighted_results
    
    def _get_sustainability_level(self, score: float) -> str:
        """
        Convert a numerical sustainability score to a descriptive level.
        """
        if score >= 8.5:
            return "Excellent"
        elif score >= 7.5:
            return "Very Good"
        elif score >= 6.5:
            return "Good"
        elif score >= 5.5:
            return "Above Average"
        elif score >= 4.5:
            return "Average"
        elif score >= 3.5:
            return "Below Average"
        elif score >= 2.5:
            return "Poor"
        else:
            return "Very Poor"
    
    def parse_material_string(self, material_string: str) -> Dict[str, float]:
        """
        Parse a material composition string into a dictionary of materials and percentages.
        """
        if not material_string:
            return {}
            
        # Clean up the string
        material_string = material_string.lower().strip()
        
        # Try to extract percentages and materials
        materials = {}
        
        # Pattern: percentage followed by material name
        pattern = r'(\d+)%?\s*([a-zA-Z-]+)'
        matches = re.findall(pattern, material_string)
        
        if matches:
            for match in matches:
                percentage = float(match[0]) / 100.0
                material = match[1].strip()
                
                materials[material] = percentage
        else:
            # If no percentages found, try to extract just material names
            material_names = re.findall(r'([a-zA-Z-]+)', material_string)
            if material_names:
                # If only one material, assume 100%
                if len(material_names) == 1:
                    materials[material_names[0].strip()] = 1.0
                else:
                    # If multiple materials but no percentages, distribute evenly
                    equal_pct = 1.0 / len(material_names)
                    for material in material_names:
                        materials[material.strip()] = equal_pct
        
        return materials
    
    def get_recommended_alternatives(self, material: str) -> List[Dict[str, Any]]:
        """
        Get recommended more sustainable alternatives for a material.
        """
        category = self._normalize_material_name(material)
        if not category:
            return []
            
        # Get rows for this material category
        material_rows = self.textile_data[self.textile_data.iloc[:, 0] == category]
        
        if material_rows.empty:
            return []
            
        # Get all certifications for this material
        certifications = []
        for _, row in material_rows.iterrows():
            cert_data = self._extract_certification_data(row)
            if cert_data:
                # Calculate average impact score
                scores = []
                for area_data in cert_data["impact_scores"].values():
                    if "score" in area_data:
                        scores.append(area_data["score"])
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    cert_data["average_score"] = avg_score
                    certifications.append(cert_data)
        
        # Sort by average score, highest first
        certifications.sort(key=lambda x: x.get("average_score", 0), reverse=True)
        
        # Return top 3 recommendations
        recommendations = []
        for cert in certifications[:3]:
            recommendations.append({
                "name": cert["certification"],
                "category": category,
                "average_score": cert.get("average_score", 0),
                "impact_scores": cert["impact_scores"]
            })
            
        return recommendations
    
    def get_detailed_impact_explanation(self, material: str, impact_area: str) -> str:
        """
        Get a detailed explanation of a specific impact area for a material.
        """
        category = self._normalize_material_name(material)
        if not category or impact_area not in self.impact_areas:
            return f"No detailed explanation available for {material} in area: {impact_area}"
        
        # Check if we have detailed data
        if category in self.detailed_data:
            df = self.detailed_data[category]
            
            # Find columns for this impact area
            area_cols = [col for col in df.columns if impact_area.lower() in col.lower() and "description" in col.lower()]
            
            if area_cols:
                descriptions = df[area_cols[0]].dropna().tolist()
                if descriptions:
                    return descriptions[0]
            
            # If we don't have a specific description column, return subcategory data
            if impact_area in self.detailed_impact_categories:
                subcats = self.detailed_impact_categories[impact_area]
                available_subcats = [s for s in subcats if s in df.columns]
                
                if available_subcats:
                    return f"Key factors for {impact_area} in {material}: {', '.join(available_subcats)}"
        
        return f"No detailed explanation available for {material} in area: {impact_area}"
