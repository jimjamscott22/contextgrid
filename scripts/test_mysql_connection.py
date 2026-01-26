#!/usr/bin/env python3
"""Test MySQL connection to Raspberry Pi."""

import pymysql
import sys

def test_connection():
    """Test connection to MySQL server."""
    try:
        print("Attempting to connect to MySQL server at 192.168.1.25:3306...")
        conn = pymysql.connect(
            host='192.168.1.25',
            port=3306,
            user='contextgrid_user',
            password='Yar22',
            database='contextgrid',
            charset='utf8mb4',
            connect_timeout=10
        )
        print("✓ Connection successful!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✓ MySQL version: {version[0]}")
        
        # List existing tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if tables:
            print(f"✓ Existing tables: {[t[0] for t in tables]}")
        else:
            print("  No tables found (database is empty)")
        
        conn.close()
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check if MySQL is running on the Raspberry Pi:")
        print("   sudo systemctl status mysql")
        print("\n2. Verify MySQL is listening on all interfaces:")
        print("   Check /etc/mysql/mysql.conf.d/mysqld.cnf")
        print("   Ensure: bind-address = 0.0.0.0")
        print("\n3. Check firewall allows port 3306:")
        print("   sudo ufw allow 3306/tcp")
        print("\n4. Verify user has remote access:")
        print("   mysql -u root -p")
        print("   SELECT host, user FROM mysql.user WHERE user='contextgrid_user';")
        print("   -- Should show: 192.168.1.% or % for host")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
