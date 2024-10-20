# Order Management System

## Description
This Order Management System is a Flask-based web application designed to help businesses manage their product inventory, customer orders, and wholesaler relationships. It provides functionalities for creating and tracking orders, managing products and wholesalers, and viewing analytics.

## Features
- User authentication
- Product management (add, edit, delete, bulk upload)
- Wholesaler management
- Customer order creation and tracking
- Daily and monthly order management
- Order history and analytics
- Search functionality for products

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/order-management-system.git
   cd order-management-system
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database_url
   ```

5. Initialize the database:
   ```
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

## Usage
After starting the application, navigate to `http://localhost:5000` in your web browser. Log in or register a new account to access the system.

### Key Pages
- `/products`: Manage products
- `/wholesalers`: Manage wholesalers
- `/create_order_list`: Create new orders
- `/customer_orders`: Manage customer orders
- `/analytics`: View system analytics

## Deployment
This application is configured for deployment on Heroku. Ensure you have the Heroku CLI installed and are logged in.

1. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```

2. Set up the Heroku PostgreSQL addon:
   ```
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. Set the necessary environment variables:
   ```
   heroku config:set SECRET_KEY=your_secret_key
   ```

4. Deploy the application:
   ```
   git push heroku main
   ```

5. Run database migrations:
   ```
   heroku run flask db upgrade
   ```

## Contributing
Contributions to the Order Management System are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
vgoutamram@gmail.com

Project Link: https://github.com/gramv/order-management-system
