# EcoAgent: Apparel Sustainability Assessment

EcoAgent is a Python-based agent that evaluates the sustainability impact of consumer apparel products by dynamically collecting and synthesizing information from multiple sources.

## Overview

The agent follows a workflow that:

1. Takes an Amazon product URL as input
2. Scrapes product information (brand, materials, etc.)
3. Analyzes material sustainability using the Textile Exchange database
4. Searches for and analyzes company ESG reports
5. Analyzes consumer reviews for sustainability perceptions
6. Synthesizes all data to generate a comprehensive sustainability assessment

## Features

- Multi-source data integration (materials, brand policies, consumer feedback)
- Adaptive analysis based on available information
- Configurable assessment depth (basic, standard, comprehensive)
- Conflict identification between different sustainability indicators
- Detailed report generation with actionable insights

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ecoagent.git
cd ecoagent

python -m venv venv
source venv/bin/activate  

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python agent_workflow.py --url https://www.amazon.com/dp/B07C5JHN8Z
python agent_workflow.py --url https://www.amazon.com/dp/B07C5JHN8Z --depth comprehensive

```

## Example Output

```
python agent_workflow.py --url "https://www.amazon.in/Allen-Solly-Regular-AMKP317G04249_Jet-Black_Large/dp/B06Y2FG6R7"

=== Step 1: Initializing EcoAgent ===
Product Type: None
Assessment Depth: standard
Using real web scraping
Oxylabs credentials provided - will use Oxylabs Web Scraper API
Using Gemini API for analysis
Using real data sources for ESG reports and textile database

=== Step 2: Scraping Amazon Product Page ===
Oxylabs Web Scraper API credentials detected and will be used for scraping
Requesting data for ASIN: B06Y2FG6R7 with domain: in
Successfully retrieved product data:
  - Title: Allen Solly Men's Solid Regular Fit Polo
  - Brand: AllenSolly
  - Material: 60% Cotton and 40% Polyester
  - Category: Polos

=== Analyzing Material Information ===
Material information is clear and can be directly processed
Identified materials: cotton, polyester, spandex

=== Step 3: Querying Textile Database for material impact. ===
Successfully loaded textile database with 71 entries
Successfully loaded Cotton data with 44 rows
Successfully loaded Synthetic data with 27 rows
Successfully loaded Flax data with 27 rows
Successfully loaded MMCF data with 68 rows
Successfully loaded Wool data with 21 rows
Using Textile Database Scorecard PFMM data and detailed material CSV files
Looking up material: cotton (0.6%)
Found impact data for cotton
  - Category: Cotton
  - Impact areas:
    - Climate: 13.0/100
    - Water: 20.0/100
    - Chemistry: 22.0/100
    - Land: 35.0/100
    - Biodiversity: 31.0/100
    - Resource: 33.0/100
    - Human_rights: 47.0/100
    - Integrity: 88.0/100
  - Found 1 certification options
  - Top certification: Better Cotton {F, IP} {MB, CoC}
  - Detailed data available:
    - Found 41 certification standards in detailed data
Looking up material: polyester (0.4%)
Found impact data for polyester
  - Category: Synthetic
  - Impact areas:
    - Climate: 39.0/100
    - Water: 39.0/100
    - Chemistry: 30.0/100
    - Resource: 64.0/100
    - Human_rights: 10.0/100
    - Integrity: 77.0/100
  - Found 1 certification options
  - Top certification: Chemically Recycled Polyester – GRS Certified
(Recycled materials & Chain of Custody)
  - Detailed data available:
    - Found 24 certification standards in detailed data
Looking up material: spandex (0.4%)
Found impact data for spandex
  - Category: Synthetic
  - Impact areas:
    - Climate: 39.0/100
    - Water: 39.0/100
    - Chemistry: 30.0/100
    - Resource: 64.0/100
    - Human_rights: 10.0/100
    - Integrity: 77.0/100
  - Found 1 certification options
  - Top certification: Chemically Recycled Polyester – GRS Certified
(Recycled materials & Chain of Custody)
  - Detailed data available:
    - Found 24 certification standards in detailed data
Product contains a blend of materials
Blend composition:
  - cotton: 0.6
  - polyester: 0.4
  - spandex: 0.4
Weighted impact scores:
  - Climate: 27.9/100
  - Water: 30.9/100
  - Chemistry: 26.6/100
  - Land: 15.0/100
  - Biodiversity: 13.3/100
  - Resource: 50.7/100
  - Human_rights: 25.9/100
  - Integrity: 81.7/100
Sustainability rating: 2.6/10 (Poor)

=== Step 4: Searching ESG Report for AllenSolly ===
Note: Using mock ESG data (real APIs not yet integrated)
No ESG report found for AllenSolly

=== Step 5: Scraping Consumer Reviews ===
Oxylabs Web Scraper API credentials detected and will be used for scraping
Attempting to scrape reviews using Oxylabs API for ASIN: B06Y2FG6R7
Successfully retrieved 8 reviews from Oxylabs
Successfully retrieved 8 reviews

=== Step 6: Analyzing Consumer Reviews for sustainability insights. ===
Overall sustainability sentiment: 5.034545714599524/10
Key insights:
  - Consumers frequently mention materials in their reviews.

=== Step 7: Synthesizing Data ===
Material: Blend of 60% cotton, 40% polyester, 40% spandex
Material sustainability score: 2.6/10
Brand sustainability rating: 5.0/10
Consumer sentiment rating: 5.0/10
Using assessment weights for 'standard' depth:
  - material_impact: 50%
  - brand_assessment: 30%
  - consumer_feedback: 20%
Overall weighted sustainability score: 3.8/10

=== Step 8: Generating Final Report ===
Generating standard report

=== Final Sustainability Assessment ===
Overall Rating: 3.8/10 (Poor)
Summary: This product achieves a poor sustainability rating (3.8/10). Material strength: sustainability rating (2.596428571428572/10) No significant sustainability news found for AllenSolly. Consumers frequently mention materials in their reviews. This product has significant sustainability concerns.

Component Scores:
- Material: 2.6/10
- Brand: 5.0/10
- Consumer: 5.0/10

Key Material Insights:
- Material strength: sustainability rating (2.596428571428572/10)
- Material concern: sustainability rating (2.596428571428572/10)
- Material composition: 60% cotton, 40% polyester, 40% spandex

Key Brand Insights:
- No significant sustainability news found for AllenSolly.

Key Consumer Insights:
- Consumers frequently mention materials in their reviews.
```

## Project Structure

```
ecoagent/
├── agent_workflow.py       # Main script
├── utils/
│   ├── __init__.py
│   ├── scraper.py          # Amazon product scraper
│   ├── material_analyzer.py # Material analysis
│   ├── esg_analyzer.py     # ESG report analysis
│   ├── review_analyzer.py  # Consumer review analysis
│   ├── db_query.py         # Textile database query
│   ├── report_generator.py # Final report generation
|   └── gemini_api.key      # For LLM purpose
├── data/   # Material sustainability database
└── README.md
```

## Implementation Details

### Decision Making Logic

The agent makes several key decisions during the workflow:

1. **Material Clarity**: Determines if material information is clear or needs inference
2. **ESG Report Availability**: Checks if a brand's sustainability report exists and is accessible
3. **Material Identification**: Verifies if materials can be found in the sustainability database
4. **Consumer Review Flags**: Identifies if sustainability concerns appear in consumer reviews

### Data Integration Strategy

Data from different sources is prioritized based on:

1. **Assessment Depth**: Different weights applied to each data source depending on depth level
2. **Data Quality**: Sources with more specific metrics are weighted higher
3. **Conflict Resolution**: When sources disagree, the agent identifies the conflict and favors technical data in the final score

## Notes

- This implementation uses mock data for demonstration purposes
- In a production environment, you would replace mock implementations with real APIs
- For the Gemini API integration, you would need to add your API key