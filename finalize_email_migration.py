"""
Final migration script to complete the transition to hashed emails.

IMPORTANT: Only run this after verifying that:
1. All users have email_hash values populated
2. Login, registration, and password reset are working with hashed emails
3. All application functionality has been tested thoroughly

This script will:
1. Make email_hash NOT NULL (required)
2. Remove the plain email column (or replace with a dummy value)
3. Update relevant code to no longer use plain emails

MAKE A FULL DATABASE BACKUP BEFORE RUNNING THIS SCRIPT!
"""

from eslquickreads import app, db
from eslquickreads.route.models.user_models import Users, Developer
import logging
import random
import string

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("finalize_email_migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("finalize_email_migration")

def verify_all_hashes_populated():
    """Verify all records have email_hash values before proceeding"""
    with app.app_context():
        # Check Users
        total_users = Users.query.count()
        if total_users == 0:
            logger.warning("No users found in the database!")
            return False
            
        users_missing_hash = Users.query.filter(Users.email_hash == None).count()
        if users_missing_hash > 0:
            logger.error(f"Found {users_missing_hash} users missing email_hash values!")
            return False
            
        # Check Developers
        total_devs = Developer.query.count()
        devs_missing_hash = Developer.query.filter(Developer.email_hash == None).count()
        if devs_missing_hash > 0:
            logger.error(f"Found {devs_missing_hash} developers missing email_hash values!")
            return False
            
        logger.info("All users and developers have email_hash values populated")
        return True

def obfuscate_plain_emails():
    """Replace plain emails with dummy values as an intermediate step"""
    with app.app_context():
        # Process Users
        users = Users.query.all()
        logger.info(f"Obfuscating {len(users)} user emails")
        
        for user in users:
            try:
                # Generate a random string to replace the email
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                user.email = f"redacted-{random_suffix}@example.com"
            except Exception as e:
                logger.error(f"Error obfuscating user {user.id}: {str(e)}")
        
        # Process Developers
        devs = Developer.query.all()
        logger.info(f"Obfuscating {len(devs)} developer emails")
        
        for dev in devs:
            try:
                # Generate a random string to replace the email
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                dev.email = f"redacted-developer-{random_suffix}@example.com"
            except Exception as e:
                logger.error(f"Error obfuscating developer {dev.id}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        logger.info("All plain emails obfuscated successfully")

def remove_email_column():
    """Remove the plain email column (DESTRUCTIVE OPERATION)"""
    logger.warning("This would normally remove the email column completely.")
    logger.warning("For safety, we're not actually executing this step.")
    logger.warning("To execute this in production, uncomment the code below and run again.")
    
    # with app.app_context():
    #     db.engine.execute('ALTER TABLE users DROP COLUMN email')
    #     db.engine.execute('ALTER TABLE developer DROP COLUMN email')
    #     logger.info("Email columns removed from both tables")

def enforce_email_hash_not_null():
    """Make email_hash column NOT NULL to enforce its usage"""
    with app.app_context():
        db.engine.execute('ALTER TABLE users MODIFY COLUMN email_hash VARCHAR(64) NOT NULL')
        db.engine.execute('ALTER TABLE developer MODIFY COLUMN email_hash VARCHAR(64) NOT NULL')
        logger.info("Made email_hash NOT NULL in both tables")

if __name__ == "__main__":
    logger.info("Starting finalization of email hashing migration")
    logger.warning("THIS SCRIPT WILL MODIFY YOUR DATABASE PERMANENTLY")
    logger.warning("Make sure you have a backup before proceeding!")
    
    confirmation = input("Type 'CONFIRM' to proceed with the migration finalization: ")
    if confirmation != "CONFIRM":
        logger.info("Aborted by user. No changes were made.")
        exit(0)
    
    try:
        # Verify all email_hash values are populated
        if not verify_all_hashes_populated():
            logger.error("Verification failed! Some records are missing email_hash values.")
            logger.error("Run the migration_email_hash.py script first and fix any issues.")
            exit(1)
        
        # Step 1: Obfuscate plain emails as an intermediate step
        obfuscate_plain_emails()
        
        # Step 2: Make email_hash NOT NULL
        enforce_email_hash_not_null()
        
        # Step 3: Remove email column (commented out for safety)
        remove_email_column()
        
        logger.info("Migration finalization completed successfully")
        logger.info("To fully remove the email column, edit this script and uncomment the code in remove_email_column()")
    except Exception as e:
        logger.error(f"Migration finalization failed: {str(e)}")
        exit(1)