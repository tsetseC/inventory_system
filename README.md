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


<img width="1920" height="1024" alt="Screenshot (253)" src="https://github.com/user-attachments/assets/b83f485d-3aef-4efc-8a2c-e5c3ff9439f8" />

<img width="1920" height="1024" alt="Screenshot (255)" src="https://github.com/user-attachments/assets/43adf1a1-290e-4b48-af24-92264a4f75b9" />

<img width="1920" height="1031" alt="Screenshot (269)" src="https://github.com/user-attachments/assets/1e038693-24f0-462b-b076-f67f6ea7b01e" />


<img width="1920" height="1024" alt="Screenshot (261)" src="https://github.com/user-attachments/assets/dbfe598a-ecec-4453-85a9-3410a5bfc0db" />

<img width="1920" height="1031" alt="Screenshot (265)" src="https://github.com/user-attachments/assets/0807ca9c-c5a9-48ea-97da-6c6d626d9384" />

<img width="1920" height="1028" alt="Screenshot (273)" src="https://github.com/user-attachments/assets/2b0a22d3-7140-4b87-9c42-b84359316740" />

<img width="1920" height="1035" alt="Screenshot (234)" src="https://github.com/user-attachments/assets/86cb8803-0a9a-4e2a-a568-2ce890fe2de0" />

<img width="1920" height="1038" alt="Screenshot (272)" src="https://github.com/user-attachments/assets/97d653f5-2f52-4999-83a0-78ef1c82ea6e" />



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
