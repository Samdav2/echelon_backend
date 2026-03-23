#!/bin/bash

# =============================================================================
# Application Startup Guide
# =============================================================================

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                        ║"
echo "║         🚀 Ticket Booking System - Application Startup Guide 🚀        ║"
echo "║                                                                        ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo

# =============================================================================
# Step 1: Check Python
# =============================================================================
echo "📋 Step 1: Checking Python environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed!"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1)
echo "✅ $PYTHON_VERSION"
echo

# =============================================================================
# Step 2: Virtual Environment
# =============================================================================
echo "📋 Step 2: Setting up virtual environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✅ Virtual environment activated"
echo

# =============================================================================
# Step 3: Install Dependencies
# =============================================================================
echo "📋 Step 3: Installing dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found"
fi
echo

# =============================================================================
# Step 4: Environment Configuration
# =============================================================================
echo "📋 Step 4: Checking environment configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "⚠️  IMPORTANT: Update .env with your database credentials!"
    fi
else
    echo "✅ .env file exists"
fi
echo

# =============================================================================
# Step 5: Database Setup (Optional)
# =============================================================================
echo "📋 Step 5: Database setup information..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Before starting the app, ensure:"
echo "  1. MySQL/MariaDB is running"
echo "  2. Database exists: $(grep MYSQL_DATABASE .env 2>/dev/null || echo 'DATABASE_NAME')"
echo "  3. Credentials in .env are correct"
echo
echo "To initialize database with ORM models:"
echo "  python app/core/init_db.py"
echo
echo "Or import SQL schema:"
echo "  mysql -u root -p < database_schema.sql"
echo

# =============================================================================
# Step 6: Start Application
# =============================================================================
echo "📋 Step 6: Starting application..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Choose startup method:"
echo
echo "Option 1: Using Uvicorn (Recommended for development)"
echo "  uvicorn main:app --reload"
echo
echo "Option 2: Using Python module"
echo "  python -m app.main"
echo
echo "Option 3: Direct Python execution"
echo "  python main.py"
echo
echo "Option 4: Production with Gunicorn"
echo "  gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# =============================================================================
# Access Application
# =============================================================================
echo "✨ Once running, access the application:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "  🌐 API Base:           http://localhost:5000"
echo "  📚 Swagger Docs:       http://localhost:5000/docs"
echo "  📖 ReDoc Docs:         http://localhost:5000/redoc"
echo "  ❤️  Health Check:       http://localhost:5000/health"
echo "  ℹ️  API Info:           http://localhost:5000/api/info"
echo
echo "API Endpoints:"
echo "  🔐 Authentication:     /auth"
echo "  🎭 Events:             /event"
echo "  👤 Profiles:           /profile"
echo "  👥 Users:              /user"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# =============================================================================
# Troubleshooting
# =============================================================================
echo "🔧 Troubleshooting Tips:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "  ❌ Database Connection Error:"
echo "     - Check MySQL is running"
echo "     - Verify credentials in .env"
echo "     - Ensure database exists"
echo "     - Run: python app/core/init_db.py"
echo
echo "  ❌ Port Already in Use:"
echo "     - Change PORT in .env"
echo "     - Or kill process on port 5000: lsof -ti:5000 | xargs kill"
echo
echo "  ❌ Import Errors:"
echo "     - Activate virtual environment"
echo "     - Reinstall dependencies: pip install -r requirements.txt"
echo
echo "  ❌ Module Not Found:"
echo "     - Ensure you're in the project root directory"
echo "     - Check app/ directory exists with all modules"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

echo "✅ Setup complete! Ready to start the application."
echo
echo "Run this command to start:"
echo "  uvicorn main:app --reload"
echo
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                    Happy coding! 🚀                                    ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
