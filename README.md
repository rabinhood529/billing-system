Billing and Inventory Management System
A web-based Billing and Inventory Management System developed using Python and Django as part of my BIM internship/project work.

The system is designed to simplify product management, customer records, sales transactions, billing, and inventory tracking.
Project Overview
This project provides a centralized platform for managing everyday billing and inventory operations. It includes product and customer management, a Point of Sale (POS) interface, invoice generation, and payment tracking.
Technologies Used
- Backend: Python, Django
- Frontend: HTML, CSS, Bootstrap 5
- Database: SQLite
- Environment Configuration: python-dotenv
- Version Control: Git and GitHub
Features Implemented
1. Dashboard
- Dashboard interface with navigation sidebar
- Overview of sales, products, customers, and invoices
- Recent sales section
2. Product Management
- Add, view, edit, and delete products
- Product code validation and duplicate checking
- Product search
- Purchase price and selling price validation
- Stock quantity tracking
- Low-stock and out-of-stock indicators
3. Customer Management
- Add, view, edit, and delete customer records
- Customer phone number validation
- Duplicate phone number prevention
- Optional email and address fields
4. Point of Sale (POS) and Billing
- Select customers or use Walk-in Customer
- Add products to the cart
- Update quantities and remove cart items
- Validate product stock availability
- Apply discounts
- Calculate subtotal and final total
5. Invoice and Payment Management
- Automatic invoice number generation
- Invoice details and itemized billing
- Record payment methods:
  - Cash
  - QR
  - Bank Transfer
  - Card
- Track paid, unpaid, and partially paid invoices
- Calculate outstanding payment amounts
- Print-friendly invoice layout for saving as PDF through the browser's print function
Project Structure
billing-system/
│
├── billing/
├── config/
├── core/
├── customers/
├── products/
│
├── manage.py
├── requirements.txt
├── package.json
├── package-lock.json
├── .gitignore
└── README.md

Installation and Setup

Follow these steps to run the project locally.
1. Clone the repository
git clone https://github.com/rabinhood529/billing-system.git
2. Navigate to the project directory
cd billing-system
3. Create a virtual environment
python -m venv venv
4. Activate the virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
5. Install dependencies
python -m pip install -r requirements.txt
6. Create the environment file
Create a .env file in the main project directory and add:
SECRET_KEY=your_own_django_secret_key
Generate your own secret key. Do not use or publish another developer's secret key.
7. Apply database migrations
python manage.py migrate
8. Run the development server
python manage.py runserver
Open your browser and visit:

http://127.0.0.1:8000/
Development Status
This project is under active development. Additional modules, testing, improvements, and documentation will be added as development progresses.
Developer
Rabin Sthapit
BIM Student
Prime College, Kathmandu, Nepal
Repository
GitHub: https://github.com/rabinhood529/billing-system