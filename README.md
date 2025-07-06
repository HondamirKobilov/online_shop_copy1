# Online Shop Admin Panel

A simple Django admin panel for managing the Online Shop Bot database.

## Features

- User management
- Product management
- Order management
- Shopping basket management
- Social media links management
- Contact information management

## Requirements

- Python 3.9+
- Django 5.0+

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Admin Panel

1. Start the Django development server:
```bash
python manage.py runserver
```

2. Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

You will be automatically redirected to the admin login page.

3. Create a superuser to access the admin panel:
```bash
python manage.py createsuperuser
```

4. Log in with the superuser credentials you created.

## Database

The admin panel uses the existing SQLite database from the Online Shop Bot project located at:
```
Online-Shop-Bot-main/data/main.db
```

## Models

The admin panel includes the following models:

- **User**: Represents customers in the shop
- **Product**: Represents items available for purchase
- **ConnectUs**: Stores contact information text
- **SocialMedia**: Stores social media links
- **Order**: Represents customer purchases
- **OrderDetail**: Represents individual items within an order
- **Basket**: Represents items in a user's shopping basket

## License

This project is licensed under the MIT License - see the LICENSE file for details.
