LogiFlow 🚀
A Stateful Logistics Data Pipeline Simulation

LogiFlow is a data engineering project designed to simulate a real-world logistics environment. It generates synthetic order data and tracks their lifecycle through various stages (Pending, Processing, Shipped, Delivered, or Cancelled) using a persistent state management system.

🛠️ Current Status: Ingestion Phase
We have successfully implemented the Data Ingestion layer. Unlike simple static generators, LogiFlow maintains a "memory" of existing orders to simulate a realistic flow of goods over time.

Key Features Implemented:
- Stateful Simulation: Uses SQLite and SQLAlchemy to store the current status of every order, allowing the generator to "resume" and update old orders in subsequent runs.
- Realistic Timestamps: Implements randomized delays (hours, minutes, and seconds) between status updates to mimic real-world logistical "beeps" or scans.
- Data Versioning: Generates timestamped CSV files in the data/raw directory, simulating an incremental data arrival pattern.
- Modern Python Tooling: Managed with Poetry for dependency control and Faker for realistic customer/city data.

📂 Project Structure
Plaintext

├── data/               # Git-ignored raw data storage
│   └── raw/            # Incremental CSV files (orders & updates)
├── src/
│   └── ingestion/      # Data generation & state management
│       └── data_generator.py
├── ingestion_state.db  # SQLite DB tracking order lifecycles
├── pyproject.toml      # Poetry dependencies
└── README.md

🚀 Getting Started
Clone the repository:

Bash

git clone <your-repository-url>
cd LogiFlow
Install dependencies:

Bash

poetry install
Run the Data Generator:

Bash

poetry run python src/ingestion/data_generator.py

⏭️ Roadmap: What's Next?
The project is evolving into a full ETL/ELT pipeline. The next steps are:

Data Transformation (Bronze to Silver):

- Using Pandas to consolidate multiple incremental CSV files.
- Calculating KPIs like Lead Time (Sale to Delivery) and Order Status Distribution.
- Data cleaning and schema validation.

Data Loading (Silver to Gold):

- Moving processed data into a final Analytical Database (PostgreSQL or similar).

Visualization:

- Building a dashboard to visualize logistics performance.
