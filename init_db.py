#!/usr/bin/env python3
"""
Database initialization script
Creates tables and adds sample user for testing
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.session import engine, SessionLocal
from app.db.models import Base, User
from app.core.security import get_password_hash
from app.core.logging import logger


def init_database():
    """Initialize database and create sample data"""
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Create sample user
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        
        if not existing_user:
            sample_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                is_active=True,
                is_superuser=True
            )
            
            db.add(sample_user)
            db.commit()
            
            logger.info("Sample admin user created:")
            logger.info("  Username: admin")
            logger.info("  Password: admin123")
            logger.info("  Email: admin@example.com")
        else:
            logger.info("Admin user already exists")
        
        # Create regular test user
        test_user = db.query(User).filter(User.username == "testuser").first()
        
        if not test_user:
            test_user = User(
                email="test@example.com",
                username="testuser",
                hashed_password=get_password_hash("test123"),
                full_name="Test User",
                is_active=True,
                is_superuser=False
            )
            
            db.add(test_user)
            db.commit()
            
            logger.info("Sample test user created:")
            logger.info("  Username: testuser")
            logger.info("  Password: test123")
            logger.info("  Email: test@example.com")
        else:
            logger.info("Test user already exists")
            
    except Exception as e:
        logger.error(f"Error creating sample users: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting database initialization...")
    init_database()
    logger.info("Database initialization completed!")