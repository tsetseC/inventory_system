# 🧠 Smart AI-Driven Inventory Management System

> A real-time inventory management system combining RFID hardware, SQL data storage, machine learning forecasting, and live analytics — built to solve real operational business problems.

---

## 🧩 Business Problem

Manual stock tracking leads to:
- Stock-outs and over-stocking
- Weak or non-existent demand forecasting
- Data inconsistency across departments
- No real-time visibility for decision-makers

This system addresses all of these challenges by connecting physical hardware directly to a data and AI pipeline.

---

## 🏗️ System Architecture

```
RFID Scanner → Raspberry Pi → SQL Database → Analytics Dashboard → ML Forecasting
   (Hardware)    (Edge Device)   (Storage)        (Insights)         (Predictions)
```

---

## ✨ Features

- 📡 **RFID-based stock tracking** — real-time IN/OUT stock movement via RFID scanner
- 🖥️ **Raspberry Pi edge device** — captures live operational data at the source
- 🗄️ **Structured SQL storage** — all stock movements logged with full audit trail
- 📊 **Live analytics dashboard** — stock levels, trends, and performance metrics
- 🧠 **ML demand forecasting** — trained on Kaggle datasets, transitioned to live data
- 📦 **Automated reorder calculations** — flags low stock and calculates reorder quantities
- 🗂️ **Full stock movement history** — complete audit trail for every item

---

## 🛠️ Tools & Technologies

| Layer | Technology |
|---|---|
| Hardware | Raspberry Pi, RFID Scanner |
| Language | Python |
| Database | SQL (structured storage & queries) |
| Machine Learning | Scikit-learn, Pandas, Kaggle datasets |
| Analytics | Data visualization, KPI dashboards |
| Automation | Automated reorder logic, data pipelines |

---

## 📊 Data Journey

1. **Kaggle datasets** → used as base for initial ML model training
2. **RFID live data** → transitioned to real operational data from hardware
3. **SQL database** → structured storage of all captured data
4. **Analytics layer** → trends, stock performance, anomaly detection
5. **ML predictions** → demand forecasting and automated reorder triggers

---

## 📸 Screenshots

> *(Add screenshots here — drag and drop images into this README on GitHub)*

- Dashboard overview
- RFID scan in action
- ML forecasting output
- SQL data structure

---

## 🚀 How to Run

1. Clone the repository
```bash
git clone https://github.com/tsetseC/inventory_system.git
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure your database connection in `config.py`

4. Run the main application
```bash
python main.py
```

---

## 📈 Business Impact

This system transforms raw hardware signals into structured data, insights, predictions, and automated business decisions — replacing manual stock tracking with a fully automated, data-driven pipeline.

---

## 👩‍💻 Author

**Cindy Tsetse** — Computer Systems Engineer | Power BI Developer | Data & AI Analytics  
📧 Kefentsecindy@gmail.com  
📍 Midrand, Gauteng, South Africa  
🔗 [LinkedIn](https://www.linkedin.com/in/ctsetse)
