# Prescription Med Dashboard

Interactive dashboard analysing drug prescriptions in France using OpenMedic data, regional health indicators, pharmacy density, and simple trend projections.

---

## Access to the Dashboard

The dashboard is available at the following link:

(Add your Streamlit Cloud link here after deployment)

---

## Authors

Selimane Mahfoudi, Hamza Qureshi, Badis Bensalem, Mohammed Abarkan, Tahar Malaoui
Master Data Science in Health  
Université de Lille  

---

## Project Description

This project presents an interactive data visualization dashboard exploring drug prescription patterns in France between 2014 and 2024.

The dashboard provides insights into:

- Regional disparities in medication consumption  
- Evolution of prescriptions over time  
- Differences across therapeutic classes (ATC1 and ATC2)  
- Healthcare access indicators such as medical and pharmacy density  
- Simple trend projections based on historical data  

The objective is to support a better understanding of territorial inequalities in healthcare usage and medication consumption patterns.

---

## Main Features

### Key Indicators (KPIs)

- Total prescriptions by year  
- Prescriptions per 1000 inhabitants  
- Medical density indicator  
- Automatic identification of the highest consuming region  

---

### Temporal Analysis

- Evolution of prescriptions by ATC1 class  
- Comparison between normalized indicators and raw volumes  
- Interactive filtering by region and therapeutic class  

---

### Geographic Analysis

- Choropleth map of prescription intensity by region  
- Regional pharmacy density visualization  

---

### Healthcare Supply vs Demand

- Comparison between pharmacy availability and prescription levels  
- Correlation analysis between healthcare supply and medication consumption  

---

### Detailed Exploration

- Drill down into ATC2 subclasses  
- Identification of the most prescribed drug categories  

---

### Trend Projection

- Simple linear projections for ATC1 classes  
- Short term forecasting with uncertainty band  

---

## Data Sources

The project relies on multiple official and open data sources.

### OpenMedic (Primary Dataset)

French national database of reimbursed drug prescriptions.

Includes:

- Number of boxes prescribed  
- Therapeutic classification (ATC codes)  
- Regional breakdown  
- Population indicators  

Raw OpenMedic files are not included in the repository due to their large size and must be downloaded separately.

Source:  
https://www.data.gouv.fr/fr/datasets/open-medic-base-complete-sur-les-depenses-de-medicaments-interregimes/

---

### INSEE

Regional population data used for normalization.

---

### CARMF

Data on medical workforce density obtained via web scraping.

---

### OpenStreetMap (Overpass API)

Pharmacy locations extracted using automated queries.

---

## Data Processing

Data processing steps include:

- Cleaning and harmonization of regional identifiers  
- Aggregation by ATC1 and ATC2 levels  
- Calculation of standardized indicators per population  
- Computation of healthcare density metrics  
- Simple linear modeling for short term projections  

---

## How to Run the Dashboard Locally

Install dependencies:

pip install -r requirements.txt

Launch the dashboard:

streamlit run code/dashboard/dashboard_prescription_med.py

---

## Notes on Data Availability

Due to file size limitations, raw OpenMedic datasets are not hosted in this repository.

Users must download them manually and place them in:

data/raw/

before running the full data processing pipeline.

---

## Academic Context

This project was developed as part of a Master’s degree in Data Science for Health, focusing on real world applications of open health data for public health analysis and decision support.
