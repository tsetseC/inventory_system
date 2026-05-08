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
<img width="1920" height="1080" alt="Screenshot (276)" src="https://github.com/user-attachments/assets/32f5d5c7-8b8a-4313-9168-718e96945007" />
<img width="1920" height="1080" alt="Screenshot (273)" src="https://github.com/user-attachments/assets/b766fde8-425b-401f-9605-2053b1126768" />
<img width="1920" height="1080" alt="Screenshot (234)" src="https://github.com/user-attachments/assets/4cdb9459-b73f-4177-a6ee-67d8fbbc62d8" />
<img width="1920" height="1080" alt="Screenshot (269)" src="https://github.com/user-attachments/assets/557727f7-5570-41db-bebe-d49c6ef396c6" />
<img width="1920" height="1080" alt="Screenshot (268)" src="https://github.com/user-attachments/assets/b6abe9fa-ae12-4672-bec9-f5203fe1df78" />
<img width="1920" height="1080" alt="Screenshot (272)" src="https://github.com/user-attachments/assets/3053737d-1dff-4944-9aa7-0fa88437a036" />


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
