#!/usr/bin/env python3
"""
Migration Script: Update Ladder/Snake Configurations
This script updates the conf table with new ladder/snake positions
"""

import sqlite3
import os

def migrate_conf_table():
    """Update conf table with new ladder/snake configurations"""
    db_path = "static/db/ular.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"🔧 Updating ladder/snake configurations in {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing conf data
        cursor.execute("DELETE FROM conf;")
        print("  ✅ Cleared old configurations")
        
        # Insert new ladder/snake configurations
        cursor.executemany(
            "INSERT INTO conf (start, end, type) VALUES (?, ?, ?)",
            [
                ('3', '12', 'ladder'),
                ('8', '21', 'ladder'),
                ('18', '25', 'ladder'),
                ('16', '28', 'ladder'),
                ('15', '2', 'snake'),
                ('17', '11', 'snake'),
                ('23', '10', 'snake'),
                ('9', '4', 'snake'),
            ]
        )
        print("  ✅ Added new ladder/snake configurations")
        
        # Verify
        cursor.execute("SELECT * FROM conf ORDER BY type, start;")
        configs = cursor.fetchall()
        print(f"\n📊 Current configurations ({len(configs)} total):")
        
        ladders = [c for c in configs if c[3] == 'ladder']
        snakes = [c for c in configs if c[3] == 'snake']
        
        print(f"\n  🪜 Ladders ({len(ladders)}):")
        for config in ladders:
            print(f"     {config[1]} → {config[2]}")
        
        print(f"\n  🐍 Snakes ({len(snakes)}):")
        for config in snakes:
            print(f"     {config[1]} → {config[2]}")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🔄 LADDER/SNAKE CONFIGURATION MIGRATION")
    print("=" * 60)
    print()
    
    migrate_conf_table()
    
    print()
    print("=" * 60)
    print("✅ Done!")
    print("=" * 60)
    print()
