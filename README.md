# FastAPI Ticket Booking System

A modern ticketing platform built with FastAPI and Python.

## Features

- **User Management**: User registration, authentication, and profiles
- **Event Management**: Create, retrieve, and manage events
- **Ticket System**: Purchase tickets, track attendance
- **JWT Authentication**: Secure token-based authentication
- **File Upload**: Event image uploads
- **Email Notifications**: Email service integration
- **MySQL Database**: Persistent data storage
- **RESTful API**: Complete REST API with Swagger documentation

## Project Structure

```
app/
├── models/          # Database models (SQLAlchemy)
├── schema/          # Pydantic request/response schemas
├── api/             # API route handlers
│   ├── auth.py      # Authentication endpoints
│   ├── events.py    # Event endpoints
│   ├── profile.py   # User profile endpoints
│   └── user.py      # User endpoints
├── repo/            # Repository pattern (data access)
│   └── repositories.py
├── service/         # Business logic layer
│   ├── services.py  # Core business logic
│   └── email_service.py
├── dependencies/    # Dependency injection
└── core/            # Core utilities
    ├── config.py    # Configuration management
    ├── database.py  # Database connection pool
    └── security.py  # JWT and password handling
main.py             # Application entry point
requirements.txt    # Python dependencies
.env.example        # Environment variables template
```

## Installation

### Prerequisites

- Python 3.8+
- MySQL Server 5.7+ (or compatible)
- pip package manager

### Setup

1. **Clone or extract the project**

```bash
cd app.samdavweb.org.ng
```

2. **Run setup script** (Linux/macOS)

```bash
chmod +x setup.sh
./setup.sh
```

Or **manual setup** (Linux/macOS/Windows):

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Setup database**

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE ticket_db;"

# Run migrations (if applicable)
# python migrate.py
```

## Running the Application

### Development Mode

```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Or using Python
python3 main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Events
- `POST /event/event` - Create event (multipart form with image)
- `GET /event/getAllEvent` - Get all events
- `GET /event/getEvent/{event_id}` - Get event by ID
- `GET /event/getEventByCategory/{category}` - Get events by category
- `POST /event/attendEvent/{event_id}` - Attend event (purchase ticket)
- `GET /event/getAttendedEvents` - Get user's attended events
- `GET /event/getAttendee/{event_id}` - Get event attendees
- `DELETE /event/deleteEvent/{event_id}` - Delete event
- `DELETE /event/deleteTicket/{ticket_id}` - Delete ticket

### Profile
- `GET /profile/getProfile` - Get current user profile
- `PUT /profile/updateProfile` - Update user profile

### Health
- `GET /health` - Health check
- `GET /` - Welcome endpoint

## Environment Variables

See `.env.example` for all available configuration options:

```env
# Server
DEBUG=False
PORT=5000

# Database
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ticket_db

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRATION_HOURS=24

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

## Database Schema

The system uses the following main tables:

- **users** - User accounts
- **eventcreation** - Events
- **tickets** - Ticket purchases

Ensure these tables exist in your MySQL database.

## Development

### Project Architecture

The project follows a layered architecture:

1. **API Layer** (`app/api/`) - Route handlers
2. **Service Layer** (`app/service/`) - Business logic
3. **Repository Layer** (`app/repo/`) - Data access
4. **Database Layer** (`app/core/database.py`) - Connection management

### Adding New Endpoints

1. Create a router in `app/api/`
2. Add business logic in `app/service/`
3. Add data access methods in `app/repo/`
4. Include the router in `main.py`

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad request
- `401` - Unauthorized
- `404` - Not found
- `500` - Server error

## Deployment

For production deployment:

1. Update `.env` with production values
2. Use a production ASGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

3. Use a reverse proxy (Nginx) for SSL/TLS
4. Setup a process manager (Systemd, Supervisor)

## Troubleshooting

### Database Connection Issues

- Ensure MySQL is running
- Check credentials in `.env`
- Verify database exists

### Import Errors

- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use

- Change port in `.env` or via CLI:
  ```bash
  uvicorn main:app --port 8001
  ```

## License

ISC License

## Author

Amiola_Dev
# echelon_backend
# echelon_backend
