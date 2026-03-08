# Large Language Model-Generated Dietary Metabolite Biomarker Database (DMBDB)

This repository contains the supplementary materials, code, and data for the research paper **"Large Language Model-Generated Dietary Metabolite Biomarker Database Drives Deep Annotation of the Human Diet Metabolome"**.

## Overview

This project presents a comprehensive AI-powered workflow that combines:
- **Automated literature mining** using Large Language Models (LLMs) to extract dietary biomarker information from thousands of scientific publications
- **Construction of DMBDB** - a comprehensive Dietary Metabolite Biomarker Database with chemical structures, food sources, and analytical methods
- **Metabolomics data analysis** with rigorous quality control and normalization
- **Multi-dimensional visualization** of metabolic patterns and temporal dynamics after food intake

## Repository Structure

```
.
├── Text mining code/              # AI-powered literature mining pipeline (10 steps)
│   ├── 1.Download PMCID.py
│   ├── 2.Find the FTP download address by using PMCID.R
│   ├── 3.1Download Literature by PMC.py
│   ├── 3.2Download Literature by NCBI_Direct.py
│   ├── 4.code tar.gz.py
│   ├── 5.Text cleaning.py
│   ├── 6.Find biomarker.py
│   ├── 7.Summary of Markers.py
│   ├── 8.Extract  section.py
│   ├── 9.Extract specific information.py
│   └── 10.Transfer format.py
├── Quality Control Correction/    # LC-MS data normalization using MetNormalizer
│   └── metnormalizer.R
├── Drawing code/                  # Data visualization scripts
│   ├── Time heatmap/             # Time-series heatmaps
│   ├── Circular Time Heatmap/    # Polar coordinate heatmaps
│   ├── Metabolic trend chart/    # Individual metabolite trends
│   ├── Bubble score chart/       # Scoring visualizations
│   └── Dietary biomarker categories/ # Phylogenetic tree-style classification
├── Supplementary Tables/          # Research datasets and DMBDB (9 tables)
└── README.md                      # This file
```

## 1. Text Mining Pipeline

The text mining pipeline uses Large Language Models (DeepSeek API) to automatically extract dietary biomarker information from scientific literature. The complete workflow includes **10 sequential steps**:

### 1.1 Literature Retrieval & Preprocessing

**Step 1: 1.Download PMCID.py**
- **Function**: Web scraping to download PMCID from PubMed
- Searches PubMed with article titles
- Extracts PMID, PMCID, and DOI identifiers
- Saves results to Excel file
- **Requirements**: `requests`, `beautifulsoup4`, `pandas`

**Step 2: 2.Find the FTP download address by using PMCID.R**
- **Function**: Find literature download addresses based on PMCID
- Converts PMCID to FTP download URLs for full-text articles
- **Requirements**: R packages for PMC data access

**Step 3.1: 3.1Download Literature by PMC.py**
- **Function**: Download literature based on download addresses, including main text and supplementary materials
- Downloads articles in tar.gz format from FTP URLs
- Uses PMCID as filename for tracking
- **Requirements**: `requests`, `pandas`

**Step 3.2: 3.2Download Literature by NCBI_Direct.py**
- **Function**: For literature with PMCID but cannot be downloaded via PMC, use NCBI Direct method (main text only)
- Direct download from NCBI PMC website as PDF
- Uses concurrent processing (5 workers) for efficiency
- **Requirements**: `requests`, `pandas`, `concurrent.futures`

**Step 4: 4.code tar.gz.py**
- **Function**: Extract downloaded tar.gz compressed files
- Extracts compressed archives
- Prepares articles for text processing

**Step 5: 5.Text cleaning.py**
- **Function**: Clean text converted by Mineru, remove references, images, acknowledgements
- Use **Mineru** tool to convert PDF files into Markdown format (external tool, see: https://mineru.net/)
- Removes reference sections (References, Literature Cited, Bibliography)
- Removes acknowledgements sections
- Removes image references
- Converts .md files to .txt format
- Keeps minimal required text for biomarker extraction
- **Output**: Cleaned .txt files

### 1.2 AI-Powered Biomarker Extraction

**Step 6: 6.Find biomarker.py**
- **Function**: Use Large Language Model to mine dietary biomarker names from literature
- Uses DeepSeek LLM to extract dietary biomarker names from literature
- Processes each .txt file with specialized prompt engineering
- **Key Features**:
  - Excludes disease-related markers
  - Excludes inflammatory, immune, or signaling molecules
  - Excludes hormones and hormone-like regulators
  - Requires full chemical names (not abbreviations)
  - Temperature=0 for consistent results
  - Concurrent processing with ThreadPoolExecutor
- **Output**: `Biomarker Name` table format

**Step 7: 7.Summary of Markers.py**
- **Function**: Create dictionary mapping dietary biomarker names to literature titles
- Aggregates biomarkers from all processed files
- Creates a consolidated list with file source tracking
- **Output format**: `filename: biomarker_name`

**Step 8: 8.Extract section.py**
- **Function**: Find text fragments describing each dietary biomarker
- Extracts text sections describing each specific biomarker
- Uses concurrent processing (5 workers) for efficiency
- Saves individual files per biomarker-paper combination
- **Output**: `{biomarker_name}_{paper_name}.txt`

**Step 9: 9.Extract specific information.py**
- **Function**: Extract specific structured information from description fragments
- Extracts detailed structured information for each biomarker:
  - Biomarker Name
  - Food Source (e.g., coffee, beef, protein intake)
  - Sample Size (number of participants)
  - Biological Sample (e.g., urine 24hr, plasma)
  - Analytic Procedure (e.g., HPLC, FT-ICR-MS)
  - Literature Name (PMCID)
- **Output**: Markdown table format

**Step 10: 10.Transfer format.py**
- **Function**: Convert extracted information from Markdown format to CSV format
- Converts Markdown tables to CSV format
- Standardizes data structure for downstream analysis
- **Final Output**: `Supplementary Table 3 Text mining results of dietary biomarkers.csv`

### 1.3 Installation & Setup

```bash
# Python dependencies
pip install openai pandas requests beautifulsoup4 tqdm

# R packages (for Step 2)
# Install required R packages for PMC access
```

**Important**:
- You must provide your own DeepSeek API key in the scripts
- Replace `api_key="Please replace your API key."` with your actual key
- Base URL: `https://api.deepseek.com`
- Comply with PubMed's terms of service for literature access

### 1.4 External Tools

**Mineru** (Required for Step 5)
- **Purpose**: Convert PDF files to Markdown format
- **Website**: https://mineru.net/
- **Options**: Use online service or deploy locally
- **Input**: PDF files from Step 3/4
- **Output**: Markdown (.md) files

## 2. Quality Control and Data Normalization

### 2.1 Metabolomics Data Processing

**Script**: `metnormalizer.R`

Uses the **MetNormalizer** package for comprehensive quality control and normalization of LC-MS metabolomics data.

**Features**:
- QC sample-based signal correction
- Missing value handling with customizable thresholds
- Parameter optimization (with `optimization = TRUE`)
- Parallel processing support (`threads = 4`)

**Input Files**:
- `data.csv` - Raw metabolite intensity matrix
- `sample.info.csv` - Sample metadata (QC/Sample labels, batch info, injection order)

**Key Parameters**:
```r
minfrac.qc = 0        # QC retention threshold
minfrac.sample = 0    # Sample retention threshold
optimization = TRUE   # Enable parameter optimization
multiple = 5          # Optimization fold
threads = 4           # Parallel threads
```

### 2.2 Installation

```r
if(!require(devtools)){
install.packages("devtools")
}
devtools::install_github("jaspershen/MetNormalizer")
```

### 2.3 Output

**`QC correction results.xlsx`** - Normalized and quality-controlled metabolomics data ready for downstream analysis

**Reference**: [MetNormalizer on GitHub](https://github.com/jaspershen/MetNormalizer)

## 3. Data Visualization

All visualization scripts use Arial font and produce high-resolution (300 dpi) publication-quality figures.

### 3.1 Time Series Heatmap

**Script**: `Drawing code/Time heatmap/Time heatmap.py`

Creates comprehensive heatmaps showing metabolite intensity changes across time points.

**Input**:
- `N_matched_out.xlsx` - Metabolite data with time-stamped columns (format: `Month.Day-HH:MM`)

**Key Features**:
- **Data transformation**: Log1p transformation followed by Z-score normalization
- **Time parsing**: Automatically extracts and sorts datetime from column names
- **Day labeling**: Groups time points by day (Day1, Day2, etc.)
- **Color scheme**: `vlag` colormap with centered scaling (vmin=-2, vmax=2)
- **Output format**: PNG with metabolite names hidden (for large datasets)

**Technical Details**:
```python
# Normalization pipeline
df_log = np.log1p(df_sorted)
df_scaled = StandardScaler().fit_transform(df_log.T).T
```

### 3.2 Circular Time Heatmap

**Script**: `Drawing code/Circular Time Heatmap/Circular Time Heatmap.py`

Generates polar coordinate circular heatmaps for visualizing metabolite patterns after food consumption.

**Input Files**:
- `n.csv` (or `z.csv`) - Metabolite intensity data with time columns
- `metabolites.csv` - Metabolite-to-food mapping (columns: Name, food)

**Key Features**:
- **Food grouping**: Automatically groups metabolites by food source (coffee, chocolate, banana)
- **Keyword-based classification**: Uses chemical name patterns to assign unlabeled metabolites
  - Coffee: caffeine, methylxanthine, chlorogenic, quinic, ferulic
  - Chocolate: catechin, epicatechin, theobromine, cianidanol
  - Banana: dopamine, serotonin, tryptophan, tryptamine
- **Polar layout**: Circular arrangement with color-coded food group boundaries
- **Z-score normalization**: Centered color mapping (vmin=-3, vcenter=0, vmax=3)
- **Visual separation**: Adjustable gaps between food groups (`gap_size = 3`)

**Output**: Circular heatmap with radial time labels and food-specific color borders

### 3.3 Metabolic Trend Chart

**Script**: `Drawing code/Metabolic trend chart/Metabolic trend chart.py`

Plots individual metabolite concentration trends over time with food intake event markers.

**Input**:
- `cretaine_sgmns_results.xlsx` (or `Z_matched_out.xlsx`) - Time-series metabolite data

**Key Features**:
- **Food event markers**: Vertical dashed lines indicating consumption times
  - Coffee (9:00) - Gray dashed line
  - Dark Chocolate (15:00) - Pink dashed line
  - Banana (20:00) - Yellow dashed line
- **Multi-day tracking**: Focuses on last 7 days of data
- **Automated plotting**: Generates individual plots for each metabolite
- **Time axis**: Formatted as `Day1-HH:MM` for clarity

**Output**: PNG files for each metabolite saved to specified directory

### 3.4 Bubble Score Chart

**Script**: `Drawing code/Bubble score chart/Bubble score chart.py`

Visualizes biomarker scoring results with bubble size and color representing score magnitude.

**Input**:
- `score.xlsx` - Contains columns: `Biomarker Name`, `score`

**Key Features**:
- **Top N selection**: Displays top 50 biomarkers by score (customizable)
- **Dual encoding**: Bubble size and color both represent score
- **Color gradient**: Blue-white-red gradient (low to high scores)
- **Score labels**: Numeric values displayed next to each bubble
- **Ranked display**: Biomarkers sorted by score in descending order

**Customization**:
```python
plot_labeled_bubble(df, output_folder='output', top_n=50)
```

### 3.5 Dietary Biomarker Categories

**Script**: `Drawing code/Dietary biomarker categories/Dietary biomarker categories.R`

Creates phylogenetic tree-style circular classification diagrams using ggtree.

**Input**:
- `Dietary biomarker categories.csv` - Must contain columns: `class`, `superclass`, `number`

**Key Features**:
- **Circular layout**: Tree visualization with circular arrangement
- **Hierarchical structure**: Two-level hierarchy (superclass → class)
- **Size mapping**: Bubble size represents the number of biomarkers in each category
- **Color coding**: Different colors for each superclass
- **Custom labels**: Class names displayed at tips with appropriate offsets

**R Packages Required**:
```r
library(treeio)
library(ggplot2)
library(ggtree)
```

**Output**: Circular dendrogram showing hierarchical classification of dietary biomarkers

### 3.6 Visualization Dependencies

```bash
# Python packages
pip install pandas numpy matplotlib seaborn scikit-learn openpyxl

# R packages
BiocManager::install("treeio")
BiocManager::install("ggtree")
install.packages("ggplot2")
```

## 4. Supplementary Tables

The `Supplementary Tables/` folder contains all research datasets and database files (**9 tables**):

| Table | File Name | Description | Content |
|-------|-----------|-------------|---------|
| **S1** | Supplementary Table 1 RT model training dataset.xlsx | RT Model Training Dataset | Training data for retention time prediction models |
| **S2** | Supplementary Table 2 DMBDB Information.xlsx | DMBDB Information | **Core Database**: Dietary Metabolite Biomarker Database with chemical structures, food sources, and analytical methods |
| **S3** | Supplementary Table 3 Text mining results of dietary biomarkers.csv | Text Mining Results | Extracted dietary biomarkers with metadata from literature analysis (**Step 10 Output**) |
| **S4** | Supplementary Table 4 List of Title and Number Correspondence of Literature.xlsx | Literature Mapping | Mapping between literature titles and their assigned numbers |
| **S5** | Supplementary Table 5 Dietary biomarker LC-MS database (Only Open Source Data).xlsx | LC-MS Database | Extended dietary biomarker LC-MS database (open source data only) |
| **S6** | Supplementary Table 6 The performance of text mining.xlsx | Text Mining Performance | Performance metrics and quality scores for biomarker extraction |
| **S7** | Supplementary Table 7 Annotation results.xlsx | Annotation Results | Metabolomics annotation results from experimental data |
| **S8** | Supplementary Table 8 Statistical analysis.xlsx | Statistical Analysis | Statistical analysis results comparing metabolite levels |
| **S9** | Supplementary Table 9 Metabolites and metadata of Coffee_Chocolate_Banana.xlsx | Validation Data | Metabolites and metadata from Coffee/Chocolate/Banana validation experiment |

### 4.1 DMBDB - Dietary Metabolite Biomarker Database

The core database (`Supplementary Table 2 DMBDB Information.xlsx`) contains comprehensive information for each dietary biomarker:

**Database Fields**:
- **Biomarker ID & Name**: Unique identifier and standardized name
- **Chemical Identifiers**: SMILES, InChI, InChIKey for computational applications
- **Molecular Properties**: Molecular formula, exact mass, molecular weight
- **Food Sources**: Specific foods associated with each biomarker
- **Biological Context**:
  - Sample types (e.g., urine, plasma, serum)
  - Sample collection protocols (e.g., 24-hour urine, fasting samples)
  - Sample sizes from validation studies
- **Analytical Methods**: LC-MS techniques used for detection (e.g., HPLC, UPLC-MS/MS, FT-ICR-MS)
- **Literature References**: PMCIDs linking to source publications

**Applications**:
- Metabolomics data annotation
- Dietary intake assessment
- Biomarker discovery and validation
- Mass spectrometry database matching

## 5. Complete Workflow Diagram

### 5.1 Text Mining Pipeline (10 Steps)

```mermaid
graph TD
    A[Step 1<br/>Download PMCID.py<br/>Get PMID/PMCID/DOI] --> B[Step 2<br/>Find FTP URLs.R<br/>Get Download Links]
    B --> C{Download Method}
    C -->|PMC Available| D[Step 3.1<br/>Download by PMC.py<br/>Full Text + Supplements]
    C -->|PMC Not Available| E[Step 3.2<br/>Download by NCBI_Direct.py<br/>Main Text Only]
    D --> F[Step 4<br/>code tar.gz.py<br/>Extract Archives]
    E --> F
    F --> G[External Tool<br/>Mineru<br/>PDF to Markdown]
    G --> H[Step 5<br/>Text cleaning.py<br/>Remove Refs/Images/Ack]
    H --> I[Step 6<br/>Find biomarker.py<br/>LLM Extract Names]
    I --> J[Step 7<br/>Summary of Markers.py<br/>Create Dictionary]
    J --> K[Step 8<br/>Extract section.py<br/>Get Descriptions]
    K --> L[Step 9<br/>Extract specific info.py<br/>Get Detailed Data]
    L --> M[Step 10<br/>Transfer format.py<br/>MD to CSV]
    M --> N[Supplementary Table 3<br/>Text Mining Results]
    N --> O[DMBDB Construction<br/>Supplementary Table 2]

    style O fill:#ff9999
    style G fill:#ffff99
```

### 5.2 Complete Analysis Workflow

```mermaid
graph TD
    subgraph "Text Mining Pipeline"
    T1[Steps 1-10] --> T2[Supplementary Table 3]
    end

    T2 --> D[DMBDB<br/>Supplementary Table 2]

    subgraph "Metabolomics Data Processing"
    M1[LC-MS Raw Data] --> M2[Quality Control<br/>metnormalizer.R]
    M2 --> M3[QC Corrected Data]
    end

    D --> A[Data Annotation<br/>Using DMBDB]
    M3 --> A
    A --> S1[Annotation Results<br/>Supplementary Table 7]
    S1 --> S2[Statistical Analysis<br/>Supplementary Table 8]

    S2 --> V[Visualizations]
    V --> V1[Time Heatmap]
    V --> V2[Circular Heatmap]
    V --> V3[Trend Charts]
    V --> V4[Bubble Chart]
    V --> V5[Category Tree]

    style D fill:#ff9999
    style M3 fill:#99ccff
    style S2 fill:#99ff99
```

**Workflow Summary**:
1. **Literature Mining** (Steps 1-10): AI-powered extraction of dietary biomarkers from PubMed literature
2. **Database Construction**: Building DMBDB (Supplementary Table 2) from extracted information
3. **Data Processing**: Quality control and normalization of metabolomics data using MetNormalizer
4. **Data Annotation**: Matching experimental data with DMBDB
5. **Statistical Analysis**: Differential analysis and scoring
6. **Visualization**: Multi-dimensional data visualization

## 6. Key Features

- **10-Step Automated Literature Mining**: Systematic AI-powered workflow using Large Language Models (DeepSeek) to extract dietary biomarkers from scientific papers with high precision
  - Steps 1-2: Literature retrieval (PMCID/DOI extraction)
  - Steps 3-5: Document acquisition and preprocessing (PDF → Markdown → Clean Text)
  - Steps 6-10: AI extraction and structured data generation
- **Dual Download Strategy**: Supports both PMC (full text + supplements) and NCBI Direct (main text) methods for comprehensive literature coverage
- **Comprehensive Database**: DMBDB (Supplementary Table 2) contains detailed chemical, biological, and analytical information for dietary biomarkers
- **Rigorous Quality Control**: MetNormalizer-based QC with parameter optimization ensures metabolomics data reliability
- **Multi-Dimensional Visualization**: Five complementary visualization approaches for exploring temporal metabolic patterns:
  - Time-series heatmaps for overview
  - Circular polar plots for food-specific patterns
  - Individual trend charts for detailed tracking
  - Bubble charts for scoring visualization
  - Phylogenetic-style trees for classification
- **Reproducible Research**: All code, data (9 supplementary tables), and workflows provided for full reproducibility
- **Food Intake Validation**: Experimental validation with controlled food consumption (coffee, chocolate, banana) - Supplementary Table 9

## 7. Usage Examples

### 7.1 Running the Text Mining Pipeline

```bash
# Step 1: Get PMCIDs from article titles
python "Text mining code/1.Download PMCID.py"

# Step 2: Get FTP download URLs (R script)
Rscript "Text mining code/2.Find the FTP download address by using PMCID.R"

# Step 3: Download literature (choose based on availability)
# Option 3.1: PMC method (recommended, includes supplements)
python "Text mining code/3.1Download Literature by PMC.py"
# Option 3.2: NCBI Direct method (main text only, for PMC-restricted articles)
python "Text mining code/3.2Download Literature by NCBI_Direct.py"

# Step 4: Extract compressed archives
python "Text mining code/4.code tar.gz.py"

# Step 5: Convert PDF to Markdown using Mineru, then clean text
# External tool: https://mineru.net/ (online or local deployment)
python "Text mining code/5.Text cleaning.py"

# Step 6-10: Extract biomarker information using LLM
python "Text mining code/6.Find biomarker.py"
python "Text mining code/7.Summary of Markers.py"
python "Text mining code/8.Extract section.py"
python "Text mining code/9.Extract specific information.py"
python "Text mining code/10.Transfer format.py"
```

**Output**: `Supplementary Table 3 Text mining results of dietary biomarkers.csv`

**Note**: Remember to configure your DeepSeek API key in scripts 6, 8, and 9 that use the LLM.

### 7.2 Quality Control and Normalization

```r
# Set working directory
setwd("Quality Control Correction")

# Run MetNormalizer for QC correction
source("metnormalizer.R")
```

### 7.3 Generating Visualizations

```bash
# Time-series heatmap
python "Drawing code/Time heatmap/Time heatmap.py"

# Circular polar heatmap
python "Drawing code/Circular Time Heatmap/Circular Time Heatmap.py"

# Individual metabolite trends
python "Drawing code/Metabolic trend chart/Metabolic trend chart.py"

# Bubble score chart
python "Drawing code/Bubble score chart/Bubble score chart.py"
```

```r
# Biomarker classification tree (R)
Rscript "Drawing code/Dietary biomarker categories/Dietary biomarker categories.R"
```

**Important**: Update file paths in each script to match your local environment before running.

## 8. Citation

If you use DMBDB, this code, or data in your research, please cite our paper:

```
[Citation to be added upon publication]

Title: Large Language Model-Generated Dietary Metabolite Biomarker Database
       Drives Deep Annotation of the Human Diet Metabolome
```

## 9. System Requirements

### 9.1 Python Environment

**Version**: Python 3.7 or higher

**Required Packages**:
```bash
pip install openai>=1.0.0
pip install pandas>=1.3.0
pip install numpy>=1.21.0
pip install matplotlib>=3.4.0
pip install seaborn>=0.11.0
pip install scikit-learn>=1.0.0
pip install requests>=2.26.0
pip install beautifulsoup4>=4.10.0
pip install openpyxl>=3.0.0
pip install tqdm>=4.62.0
```

### 9.2 R Environment

**Version**: R 4.0 or higher

**Required Packages**:
```r
devtools::install_github("jaspershen/MetNormalizer")
BiocManager::install("treeio")
install.packages("ggplot2")
BiocManager::install("ggtree")
```

### 9.3 API Requirements

**DeepSeek API**:
- Register at [https://www.deepseek.com/](https://www.deepseek.com/)
- Obtain API key
- Configure in scripts: `api_key="YOUR_API_KEY_HERE"`
- Base URL: `https://api.deepseek.com`

### 9.4 Computational Resources

- **Minimum**: 8GB RAM, 4-core CPU
- **Recommended**: 16GB+ RAM, 8-core+ CPU for parallel processing
- **Storage**: ~10GB for literature downloads and intermediate files

## 10. Data Availability

All supplementary data files are included in the `Supplementary Tables/` folder:

| Table | Format | Description |
|-------|--------|-------------|
| ✅ S1: RT Model Training Dataset | Excel (.xlsx) | Retention time prediction training data |
| ✅ S2: DMBDB Information | Excel (.xlsx) | Core dietary biomarker database |
| ✅ S3: Text Mining Results | CSV (.csv) | Extracted biomarkers from literature |
| ✅ S4: Literature Correspondence | Excel (.xlsx) | Title-number mapping |
| ✅ S5: LC-MS Database | Excel (.xlsx) | Open source LC-MS data |
| ✅ S6: Text Mining Performance | Excel (.xlsx) | Quality metrics and scores |
| ✅ S7: Annotation Results | Excel (.xlsx) | Metabolomics annotation output |
| ✅ S8: Statistical Analysis | Excel (.xlsx) | Statistical comparison results |
| ✅ S9: Coffee/Chocolate/Banana Data | Excel (.xlsx) | Validation experiment data |

**Note**: Some intermediate files (downloaded literature, extracted text) are not included due to size constraints but can be regenerated using the provided scripts (Steps 1-10).

## 11. Important Notes Before Running

1. **API Keys**: Configure your DeepSeek API key in all LLM-based scripts (Steps 6, 8, 9)
2. **External Tools**: Install and configure Mineru for PDF-to-Markdown conversion (Step 5)
3. **File Paths**: Update all file paths in scripts to match your local directory structure
4. **PubMed Compliance**: Ensure compliance with PubMed's terms of service for literature mining
5. **Data Privacy**: Do not commit API keys or sensitive data to version control
6. **Sequential Execution**: Text mining pipeline steps must be run in order (Steps 1-10)
7. **Download Methods**: Choose between Step 3.1 (PMC, recommended) or 3.2 (NCBI Direct) based on article availability
8. **Large Files**: Some scripts generate many output files; ensure sufficient disk space (~10GB recommended)

## 12. Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError` for packages
- **Solution**: Install all required dependencies using pip/conda

**Issue**: API timeout errors
- **Solution**: Increase timeout parameter in scripts (default: 120s)

**Issue**: Empty output from LLM extraction
- **Solution**: Check API key validity and network connectivity

**Issue**: File path errors
- **Solution**: Use raw strings (r'path') for Windows paths with backslashes

**Issue**: Encoding errors when reading files
- **Solution**: Scripts use `utf-8-sig` encoding to handle BOM; ensure input files are UTF-8

## 13. Contributing

We welcome contributions to improve DMBDB and the analysis pipeline:
- Report bugs via GitHub Issues
- Suggest new features or enhancements
- Submit pull requests for code improvements
- Share additional dietary biomarker data

## 14. License

MIT License

## 15. Contact

For questions, collaborations, or support:
- [Contact information to be added]
- Open an issue on GitHub for technical questions

## 16. Acknowledgments

- **DeepSeek API** for Large Language Model capabilities
- **MetNormalizer** package developers for quality control tools
- **PubMed Central** for open access to scientific literature
- All researchers whose publications contributed to DMBDB
- Study participants who contributed metabolomics data

---

**Last Updated**: 2025-03-08

**Repository Maintainers**: Fujian Zheng; Zijun Nie
