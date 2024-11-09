# Store Management System

## Overview
A comprehensive store management system designed specifically for retail operations. Built with Flask, this system handles daily store operations including sales tracking, inventory management, employee time tracking, and detailed analytics.

## Features

### 1. User Management
- **Multi-Role System**
  - Owner (Full administrative access)
  - Manager (Supervisory access)
  - Employee (Basic access)
- Secure authentication and authorization
- Role-based access control
- User profile management

### 2. Sales Management
- **Daily Sales Recording**
  - Multiple payment methods support
    * Front/Back cash registers
    * Credit card transactions
    * OTC payments
  - Automated discrepancy detection
  - Daily sales reconciliation
- **Document Management**
  - Sales receipt uploads
  - Digital record keeping
  - Cloud storage integration

### 3. Order Management
- **Dual Ordering System**
  - Daily orders (regular suppliers)
  - Monthly bulk orders
- **Order Processing**
  - Automated order generation
  - Order status tracking
  - Delivery management
- **Customer Orders**
  - Custom order creation
  - Status tracking
  - Payment processing

### 4. Inventory Management
- **Product Management**
  - Catalog maintenance
  - Price management
  - Stock tracking
- **Wholesaler Management**
  - Supplier profiles
  - Contact information
  - Order history
- **Bulk Operations**
  - Excel-based product uploads
  - Bulk price updates
  - Inventory audits

### 5. Employee Time Management
- **Time Tracking**
  - Clock In/Out functionality
  - Break time management
  - Overtime tracking
- **Approval Workflow**
  - Manager initial review
  - Owner final approval
  - Status tracking
- **Break Management**
  - Multiple break types
  - Break duration tracking
  - Paid/unpaid break designation
- **Payroll Integration**
  - Hourly rate management
  - Overtime calculations
  - Payment processing
  - Payment history

### 6. Analytics & Reporting
- **Sales Analytics**
  - Daily/Weekly/Monthly sales trends
  - Payment method distribution
  - Discrepancy analysis
  - Peak hours identification
  - Day-of-week performance analysis
- **Order Analytics**
  - Order value trends
  - Supplier performance
  - Product popularity
  - Profit margin analysis
- **Employee Analytics**
  - Working hours analysis
  - Break pattern analysis
  - Overtime trends
  - Labor cost analysis
- **Custom Reports**
  - Excel export functionality
  - Custom date ranges
  - Multiple report formats

## Technical Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Migration**: Flask-Migrate

### Frontend
- **Templates**: Jinja2
- **CSS Framework**: Bootstrap 5
- **JavaScript Libraries**
  - Chart.js (Analytics)
  - DataTables (Data display)
  - jQuery (DOM manipulation)

### Storage
- **Cloud Storage**: Cloudinary
- **File Types Supported**
  - Images (JPG, PNG)
  - Documents (PDF)
  - Spreadsheets (XLSX)

### Security Features
- Password hashing
- Role-based access control
- Secure file upload handling
- Form validation
- SQL injection protection

## Installation

```bash
# Clone the repository
git clone [repository-url]

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db upgrade

# Create owner account
flask create-owner [username] [email] [password]

# Run the application
flask run
```

## Environment Variables
```
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

## Database Schema
```plaintext
- users
- products
- wholesalers
- order_lists
- order_list_items
- customer_orders
- customer_order_items
- daily_sales
- sales_documents
- time_sheets
- breaks
- payroll_entries
```

## Project Structure
```
app/
├── __init__.py
├── models.py
├── auth/
│   ├── routes.py
│   └── forms.py
├── main/
│   ├── routes.py
│   └── forms.py
├── templates/
│   ├── auth/
│   ├── main/
│   └── analytics/
├── static/
└── utils/
```

# Contributing to store Management System

## Getting Started

Thank you for considering contributing to the Store Management System! This document outlines the process for contributing to the project.

### Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

1. Be respectful of differing viewpoints and experiences
2. Accept constructive criticism gracefully
3. Focus on what's best for the community
4. Show empathy towards other community members

### How Can I Contribute?

#### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

1. **Clear Title and Description**
   - Use a clear and descriptive title
   - Provide detailed steps to reproduce the issue

2. **Environment Details**
   - Your operating system
   - Python version
   - Browser (if applicable)
   - Any relevant package versions

3. **Screenshots**
   - If applicable, add screenshots to help explain the problem

4. **Code Samples**
   - Include code that demonstrates the issue
   - Use markdown code blocks for formatting

#### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

1. **Use a clear and descriptive title**
2. **Provide detailed description**
   - Explain why this enhancement would be useful
   - Suggest an implementation approach if possible
3. **Consider the scope**
   - How would this affect existing features?
   - What are potential drawbacks?

### Development Process

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/pharmacy-management.git
   cd pharmacy-management
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/your-bugfix-name
   ```

3. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

4. **Make Your Changes**
   - Follow the coding style guide
   - Add tests if applicable
   - Update documentation as needed

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Submit a Pull Request**
   - Fill in the provided PR template
   - Reference any related issues

### Coding Style Guidelines

1. **Python Code**
   - Follow PEP 8 guidelines
   - Use meaningful variable and function names
   - Add docstrings to functions and classes
   - Keep functions focused and concise

2. **HTML/Templates**
   - Use consistent indentation
   - Keep templates organized and modular
   - Follow Bootstrap conventions

3. **JavaScript**
   - Use ES6+ features when possible
   - Follow consistent naming conventions
   - Document complex functions

4. **CSS**
   - Use consistent naming conventions
   - Organize styles logically
   - Minimize use of !important

### Testing

1. **Writing Tests**
   - Add tests for new features
   - Update tests for modified features
   - Ensure all tests pass before submitting PR

2. **Running Tests**
   ```bash
   python -m pytest
   ```

### Documentation

1. **Code Documentation**
   - Add docstrings to all functions/classes
   - Include type hints where appropriate
   - Document complex algorithms

2. **README Updates**
   - Update feature list if needed
   - Keep installation instructions current
   - Document new environment variables

### Review Process

1. **Initial Review**
   - Code style compliance
   - Test coverage
   - Documentation completeness

2. **Technical Review**
   - Code quality and efficiency
   - Security considerations
   - Performance impact

3. **Final Review**
   - Integration testing
   - User experience
   - Documentation accuracy

---
## License
This software is proprietary and intended for single-store use only. All rights reserved.

### Permitted Uses:
- Single store deployment
- Code review and study
- Portfolio display (with attribution)

### Not Permitted:
- Multi-store deployment without license
- Resale or redistribution
- Modification for commercial use


## Contact
vgoutamram@gmail.com