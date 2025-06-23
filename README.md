# Food Ordering API

A secure Django REST API for a food ordering application with features like user authentication, cart management, and secure payment processing.

## Features

- 🍽️ Browse available meals
- 🛒 Cart management
- 🔐 User authentication
- 💳 Secure payment processing
- 🎁 Gift order support
- 📍 Multiple delivery locations
- 🚚 Various delivery types

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/registration/` - Register a new user
- `POST /api/auth/login/` - Log in
- `POST /api/auth/logout/` - Log out
- `POST /api/auth/password/reset/` - Request password reset
- `POST /api/auth/password/reset/confirm/` - Confirm password reset

### Meals
- `GET /api/meals/` - List all available meals
- `GET /api/meals/{id}/` - Get meal details

### Cart
- `GET /api/cart/` - View cart
- `POST /api/cart/{id}/add_item/` - Add item to cart
- `POST /api/cart/{id}/remove_item/` - Remove item from cart

### Orders
- `GET /api/orders/` - List user's orders
- `POST /api/orders/` - Create a new order
- `GET /api/orders/{id}/` - Get order details
- `POST /api/orders/{id}/confirm_payment/` - Confirm order payment

### Delivery
- `GET /api/delivery-types/` - List delivery types
- `GET /api/locations/` - List delivery locations

## Authentication

The API uses token-based authentication. Include the token in the Authorization header:

```
Authorization: Token <your-token>
```

## Payment Flow

1. Add items to cart
2. Create order (returns payment intent)
3. Complete payment using Stripe
4. Confirm payment
5. Order status updates to 'paid'

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## Security Features

- Token-based authentication
- CSRF protection
- Secure password handling
- Payment information security via Stripe
- Permission-based access control
- Input validation and sanitization 