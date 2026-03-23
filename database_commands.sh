#!/bin/bash
# Multi-Database Quick Command Reference
# Save this file as: database_commands.sh
# Usage: bash database_commands.sh

echo "🚀 Multi-Database Commands Reference"
echo "===================================="
echo ""

# Test with SQLite
test_sqlite() {
    echo "Testing SQLite Database..."
    export DB_TYPE=sqlite
    python app/core/init_db.py
    echo "✅ SQLite test complete"
}

# Test with MySQL
test_mysql() {
    echo "Testing MySQL Database..."
    export DB_TYPE=mysql
    export MYSQL_HOST=localhost
    export MYSQL_USER=root
    export MYSQL_PASSWORD=${1:-""}
    export MYSQL_DATABASE=ticket_db
    python app/core/init_db.py
    echo "✅ MySQL test complete"
}

# Test with PostgreSQL
test_postgresql() {
    echo "Testing PostgreSQL Database..."
    export DB_TYPE=postgresql
    export PG_HOST=localhost
    export PG_USER=postgres
    export PG_PASSWORD=${1:-""}
    export PG_DATABASE=ticket_db
    python app/core/init_db.py
    echo "✅ PostgreSQL test complete"
}

# Show current database
show_database() {
    echo "Current Database Configuration:"
    python -c "from app.core.db_connector import db; print(db.get_db_info())"
}

# Quick start
quick_start() {
    echo "Quick Start Setup..."
    echo "Setting DB_TYPE=sqlite"
    export DB_TYPE=sqlite
    python app/core/init_db.py
    echo ""
    echo "✅ Ready to run: python app/main.py"
}

# Show help
show_help() {
    cat << 'EOF'
Usage: bash database_commands.sh [command]

Commands:
  sqlite              → Test with SQLite (recommended for development)
  mysql [password]    → Test with MySQL (requires password)
  postgresql [pwd]    → Test with PostgreSQL (requires password)
  info                → Show current database configuration
  quick-start         → Quick setup with SQLite
  help                → Show this help message

Examples:
  bash database_commands.sh sqlite
  bash database_commands.sh mysql my_password
  bash database_commands.sh postgresql pg_password
  bash database_commands.sh info

Environment Variables:
  DB_TYPE             → sqlite, mysql, or postgresql
  SQLITE_PATH         → Path to SQLite database file
  MYSQL_HOST          → MySQL server host
  MYSQL_USER          → MySQL username
  MYSQL_PASSWORD      → MySQL password
  MYSQL_DATABASE      → MySQL database name
  PG_HOST             → PostgreSQL server host
  PG_USER             → PostgreSQL username
  PG_PASSWORD         → PostgreSQL password
  PG_DATABASE         → PostgreSQL database name
EOF
}

# Main
case "${1:-help}" in
    sqlite)
        test_sqlite
        ;;
    mysql)
        test_mysql "$2"
        ;;
    postgresql)
        test_postgresql "$2"
        ;;
    info)
        show_database
        ;;
    quick-start)
        quick_start
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
