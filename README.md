# Subscription Management API

 Flask API for managing user subscriptions.

## Features

- ✅ User sign up & JWT authentication
- ✅ Subscription plan management
- ✅ Cursor-based pagination
- ✅ Optimized SQL queries for fetching subscriptions
- ✅ Marshmallow schema validation
- ✅ SQLite DB

## Setup

###  Prerequisites

- Python 3.9+
- pipenv (recommended) or pip
- SQLite (default) or PostgreSQL

### Installation

```bash
# Clone the repository
git clone https://github.com/dev-habib-nuhu/subscription-api.git
cd subscription-api

# Install dependencies (using pipenv)
pipenv shell

# Or with regular pip
python -m venv venv

source venv/bin/activate  # Linux/Mac

# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Configuration

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
FLASK_APP=manage.py
FLASK_ENV=development
DATABASE_URL=sqlite:///subscriptions.db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

### Database Setup

```bash
# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed sample data
flask seed
```

## Running the Application

### Development Mode

```bash
flask run
```

API will be available at `http://localhost:5000`


## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app
```


````markdown
## 📌 API Reference

This outlines all available API endpoints, including the HTTP method, endpoint path, and the expected request payload.

---

> ⚠️ All subscription and plan endpoints require authentication via a JWT token sent in the `Authorization` header:
>
> ```
> Authorization: Bearer <access_token>
> ```
````
### Authentication

#### Register User
- **Method:** POST  
- **Endpoint:** `/api/users/signup`  
- **Description:** Register a new user account  
- **Request Payload:**
```json
{
  "username": "habib",
  "email": "habibnuhu@example.com",
  "password": "Test123!"
}
````

#### Login

* **Method:** POST
* **Endpoint:** `/api/users/login`
* **Description:** Authenticate user and return a JWT token
* **Request Payload:**

```json
{
  "username": "habib",
  "password": "Test123!"
}
```

---

### 📦  Plans

#### Create Subscription Plan

* **Method:** POST
* **Endpoint:** `/api/plans`
* **Description:** Create a new subscription plan
* **Request Payload:**

```json
{
  "name": "Premium",
  "description": "Full feature access",
  "price": 9.99,
  "duration_in_days": 30
}
```

#### Get All Plans

* **Method:** GET
* **Endpoint:** `/api/plans`
* **Description:** Retrieve all available subscription plans
* **Request Payload:** None

---

### 📑 Subscriptions

#### Create Subscription

* **Method:** POST
* **Endpoint:** `/api/subscriptions`
* **Description:** Create a new subscription for the authenticated user
* **Request Payload:**

```json
{
  "plan_id": 2,
  "auto_renew": true
}
```

#### Get Active Subscriptions

* **Method:** GET
* **Endpoint:** `/api/subscriptions/active`
* **Description:** Fetch active subscriptions with optional cursor-based pagination
* **Query Parameters:**
  `cursor=2023-07-15T10:00:00Z&limit=10`
* **Request Payload:** None

#### Get Subscription History

* **Method:** GET
* **Endpoint:** `/api/subscriptions/history`
* **Description:** Retrieve the user's subscription history
* **Query Parameters:**
  `limit=5`
* **Request Payload:** None

#### Cancel Subscription

* **Method:** PUT
* **Endpoint:** `/api/subscriptions/2/cancel`
* **Description:** Cancel an existing subscription to prevent auto-renewal
* **Request Payload:**

```json
{}
```

#### Upgrade Subscription

* **Method:** GET
* **Endpoint:** `/api/subscriptions/2/upgrade`
* **Description:** Upgrade an existing subscription to a new plan
* **Request Payload:**

```json
{
  "new_plan_id": 456
}
```



# Optimization Choices for Subscription Management API

## **Database Indexing**

To enhance query performance, several indexes were added to frequently queried fields across models:

### Subscription Table
- `idx_subscription_user_plan` — speeds up lookups where both `user_id` and `plan_id` are involved (e.g., checking for existing active subscriptions).
- `idx_subscription_active` — optimizes queries filtering by `is_active`.
- `idx_subscription_end_date` — improves sorting and filtering by subscription expiration.
- `idx_subscription_user_created` — supports user-based historical queries ordered by `created_at`.

### User Table
- `ix_users_email` — allows fast email lookups, especially useful during login or signup processes.
- `ix_users_username` — allows fast username lookups.

These indexes were chosen based on anticipated access patterns like:
- Fetching a user's active or historical subscriptions.
- Looking up subscriptions about to expire.
- Finding users by email during authentication or validation.

---

##  **Efficient SQL Querying**

Instead of relying solely on SQLAlchemy ORM for complex listing endpoints, we use raw SQL for operations like:
- Cursor-based pagination using `created_at`.
- Joining `subscriptions` and `plans` to reduce round trips.
- Selecting only required fields instead of whole model objects.

This ensures:
- Smaller query payloads.
- Faster data retrieval.
- Better control over pagination performance in large datasets.

We chose **cursor-based pagination** over the traditional **limit-offset** approach due to:

- **Performance at scale**: Cursor-based pagination performs better with indexed fields, especially on large datasets. In contrast, limit-offset queries can become increasingly slower as the offset grows, since the database must scan and discard rows up to the offset.


