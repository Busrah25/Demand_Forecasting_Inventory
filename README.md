# Inventory Optimization and Reorder Planning Dashboard

An interactive inventory analytics dashboard built with Python and Streamlit that supports demand forecasting, safety stock modeling, and reorder point planning for operational inventory decisions.

## Overview
This project simulates real world inventory planning scenarios using historical demand data and standard supply chain analytics methods. The dashboard is designed to resemble a decision support tool used by operations and supply chain teams to balance service level targets with inventory holding costs.

The application provides both executive level KPIs and SKU level reorder recommendations to support data driven replenishment planning.


## Live Demo
https://demandforecastinginventory-bushra.streamlit.app/

## Business Problem
Organizations must balance two competing risks:
- Stockouts that reduce customer satisfaction and revenue  
- Overstocking that increases holding costs and ties up working capital  

This project addresses the core inventory planning question:

**How much inventory should be stocked and when should a reorder be placed to meet target service levels?**

## Solution Approach
The dashboard follows a standard industry inventory planning workflow:

1. Aggregate historical demand data  
2. Calculate average demand and demand variability  
3. Apply service level based safety stock modeling  
4. Compute reorder points using lead time assumptions  
5. Identify SKUs requiring immediate replenishment  
6. Generate recommended order quantities  

All calculations align with textbook supply chain analytics methods commonly implemented in ERP and planning systems.

## Key Metrics
- Average daily demand  
- Demand variability (standard deviation)  
- Safety stock  
- Reorder point  
- Recommended order quantity per SKU  

## Technologies Used
- Python  
- Pandas  
- NumPy  
- SciPy  
- Streamlit  

## Data and Logic
Historical demand data is loaded from a CSV file and processed to calculate demand patterns and variability. On hand inventory values are simulated for demonstration purposes. Reorder logic reflects real world inventory planning techniques based on lead time demand and service level targets.

## How to Run Locally
1. Clone the repository  
2. Install dependencies  
3. Launch the Streamlit application  

git clone https://github.com/Busrah25/Demand_Forecasting_Inventory.git

cd Demand_Forecasting_Inventory
streamlit run app.py


## Future Improvements
- Integration with real ERP inventory data  
- Support for multiple service level scenarios  
- EOQ based order quantity optimization  
- Exportable replenishment reports for planners  
