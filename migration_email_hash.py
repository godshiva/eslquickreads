"""
Migration script to populate email_hash column for all existing users.

This script:
1. Adds the email_hash column to Users and Developer tables if they don't exist
2. Populates the email_hash for all existing users
3. Verifies the migration was successful

Run this script after deploying the updated model code but before switching to use email_hash exclusively.
"""

from eslquickreads import app, db
from eslquickreads.route.models.user_models import Users, Developer, hash_email
from sqlalchemy import Column, String
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("email_migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("email_migration")

def add_email_hash_column():
    """Add email_hash column to both tables if it doesn't exist"""
    
    # Check if the column exists for Users
    try:
        # First try to access the column to see if it exists
        Users.email_hash
        logger.info("Users.email_hash column already exists")
    except:
        # If it doesn't exist, add it
        logger.info("Adding email_hash column to Users table")
        with app.app_context():
            db.engine.execute('ALTER TABLE users ADD COLUMN email_hash VARCHAR(64) UNIQUE')
        logger.info("Added email_hash column to Users table")
    
    # Check if the column exists for Developer
    try:
        Developer.email_hash
        logger.info("Developer.email_hash column already exists")
    except:
        logger.info("Adding email_hash column to Developer table")
        with app.app_context():
            db.engine.execute('ALTER TABLE developer ADD COLUMN email_hash VARCHAR(64) UNIQUE')
        logger.info("Added email_hash column to Developer table")

def populate_email_hash_for_existing_users():
    """Update all existing users with hashed email values"""
    with app.app_context():
        # Process Users
        users = Users.query.all()
        logger.info(f"Found {len(users)} regular users to update")
        
        for user in users:
            try:
                old_email = user.email
                success = user.update_email_hash()
                if success:
                    logger.info(f"Updated hash for user email: {old_email[:3]}...{old_email[-3:]}")
                else:
                    logger.warning(f"Failed to update hash for user: {user.id}")
            except Exception as e:
                logger.error(f"Error updating user {user.id}: {str(e)}")
        
        # Process Developers
        devs = Developer.query.all()
        logger.info(f"Found {len(devs)} developers to update")
        
        for dev in devs:
            try:
                old_email = dev.email
                success = dev.update_email_hash()
                if success:
                    logger.info(f"Updated hash for developer email: {old_email[:3]}...{old_email[-3:]}")
                else:
                    logger.warning(f"Failed to update hash for developer: {dev.id}")
            except Exception as e:
                logger.error(f"Error updating developer {dev.id}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        logger.info("All changes committed to database")

def verify_migration():
    """Verify all records have been updated correctly"""
    with app.app_context():
        # Check Users
        total_users = Users.query.count()
        updated_users = Users.query.filter(Users.email_hash != None).count()
        logger.info(f"Users with email_hash: {updated_users}/{total_users}")
        
        # Check Developers
        total_devs = Developer.query.count()
        updated_devs = Developer.query.filter(Developer.email_hash != None).count()
        logger.info(f"Developers with email_hash: {updated_devs}/{total_devs}")
        
        # Overall success rate
        success_rate = 100 * (updated_users + updated_devs) / (total_users + total_devs) if (total_users + total_devs) > 0 else 0
        logger.info(f"Migration success rate: {success_rate:.2f}%")
        
        # Validate hash correctness for a sample user
        sample_user = Users.query.first()
        if sample_user:
            original_hash = sample_user.email_hash
            recalculated_hash = hash_email(sample_user.email)
            hash_matches = original_hash == recalculated_hash
            logger.info(f"Sample hash validation: {'PASSED' if hash_matches else 'FAILED'}")
            if not hash_matches:
                logger.error(f"Hash mismatch! DB has: {original_hash}, Calculated: {recalculated_hash}")

if __name__ == "__main__":
    logger.info("Starting email_hash migration")
    
    try:
        # Step 1: Add columns
        add_email_hash_column()
        
        # Step 2: Populate email_hash for existing users
        populate_email_hash_for_existing_users()
        
        # Step 3: Verify migration
        verify_migration()
        
        logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")