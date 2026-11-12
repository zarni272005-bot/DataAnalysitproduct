# Retail Pulse Dashboard

A modern sales analytics dashboard built with Streamlit and Plotly for tracking revenue, product performance, category contribution, and recent transactions.

## Features
- KPI summary cards for revenue, orders, average order value, and top seller
- Monthly revenue trend line chart
- Category contribution donut chart
- Product revenue and units-sold bar charts
- Recent sales table with an add-sale form
- Dark theme UI for a premium dashboard look

## Run locally

1. Clone the repo
2. Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   streamlit run SalesDashboard/app.py
   ```

## Project structure

```text
DataAnalysitproduct/
├── SalesDashboard/
│   ├── app.py
│   ├── .streamlit/
│   ├── data/
│   └── services/
├── README.md
├── requirements.txt
└── .gitignore
```
