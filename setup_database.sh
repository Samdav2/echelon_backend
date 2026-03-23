#!/bin/bash

# Database Setup Script
# Run this script to set up the MySQL database for the FastAPI Ticket Booking System

echo "================================"
echo "Setting up Database"
echo "================================"

# Variables
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-}"
MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
DB_NAME="ticket_db"

# Check if MySQL is running
echo "Checking MySQL connection..."
mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "✗ Failed to connect to MySQL"
    echo "Please ensure MySQL is running and credentials are correct"
    exit 1
fi

echo "✓ MySQL connection successful"
echo ""

# Create database and tables
echo "Creating database and tables..."
mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < database_schema.sql

if [ $? -eq 0 ]; then
    echo "✓ Database setup completed successfully"
else
    echo "✗ Failed to setup database"
    exit 1
fi

echo ""
echo "================================"
echo "Database Setup Complete!"
echo "================================"
echo ""
echo "Database: $DB_NAME"
echo "Host: $MYSQL_HOST:$MYSQL_PORT"
echo ""
