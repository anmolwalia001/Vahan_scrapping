"""
Migration script to add vehicle_registration_data table
Run this script to create the new table in your database
"""
import logging
from sqlalchemy import text
from db.session import engine  
from db.models import VehicleRegistrationData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_vehicle_registration_table():
    """Create the vehicle_registration_data table"""
    try:
        logger.info("Creating vehicle_registration_data table...")

        # Create the table if it doesn't exist
        VehicleRegistrationData.__table__.create(engine, checkfirst=True)
        logger.info("✓ vehicle_registration_data table created successfully")

        # Verify table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name = 'vehicle_registration_data'
            """))
            if result.fetchone():
                logger.info("✓ Table verified in database")
            else:
                logger.error("✗ Table not found after creation")
                return False
        return True

    except Exception as e:
        logger.error(f"Error creating table: {e}")
        return False


def add_indexes():
    """Add useful indexes for query performance"""
    try:
        logger.info("Adding indexes...")

        with engine.connect() as conn:
            # Helper to safely create index
            def create_index_if_not_exists(index_name, columns):
                exists = conn.execute(text(f"""
                    SELECT COUNT(1)
                    FROM information_schema.statistics
                    WHERE table_schema = DATABASE()
                      AND table_name = 'vehicle_registration_data'
                      AND index_name = '{index_name}'
                """)).scalar()

                if not exists:
                    conn.execute(text(f"""
                        CREATE INDEX {index_name}
                        ON vehicle_registration_data({columns})
                    """))
                    logger.info(f"  ✓ Created index: {index_name}")
                else:
                    logger.info(f"  ↺ Index already exists: {index_name}")

            create_index_if_not_exists("idx_vehicle_reg_file_id", "file_id")
            create_index_if_not_exists("idx_vehicle_reg_maker_name", "maker_name")
            create_index_if_not_exists("idx_vehicle_reg_state_year", "state_code, year")
            create_index_if_not_exists("idx_vehicle_reg_rto_code", "rto_code")

            conn.commit()

        logger.info("✓ Indexes created successfully")
        return True

    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        return False


def verify_migration():
    """Verify the migration was successful"""
    try:
        with engine.connect() as conn:
            # Check columns
            result = conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                AND table_name = 'vehicle_registration_data'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()

            logger.info(f"Table has {len(columns)} columns:")
            for col_name, col_type in columns:
                logger.info(f"  - {col_name}: {col_type}")

            # Check indexes
            result = conn.execute(text("""
                SELECT DISTINCT index_name
                FROM information_schema.statistics
                WHERE table_schema = DATABASE()
                AND table_name = 'vehicle_registration_data'
            """))
            indexes = result.fetchall()

            logger.info(f"\nTable has {len(indexes)} indexes:")
            for idx in indexes:
                logger.info(f"  - {idx[0]}")

        return True

    except Exception as e:
        logger.error(f"Error verifying migration: {e}")
        return False


def rollback_migration():
    """Rollback: Drop the table if needed"""
    try:
        logger.warning("Rolling back migration - dropping vehicle_registration_data table...")

        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS vehicle_registration_data"))
            conn.commit()

        logger.info("✓ Table dropped successfully")
        return True

    except Exception as e:
        logger.error(f"Error during rollback: {e}")
        return False


def main():
    """Run the migration"""
    print("\n" + "="*60)
    print("Vehicle Registration Data Table Migration")
    print("="*60 + "\n")

    if not create_vehicle_registration_table():
        print("\n✗ Migration failed at table creation")
        return

    if not add_indexes():
        print("\n⚠ Warning: Indexes creation failed, but table is ready")

    print("\nVerifying migration...")
    if verify_migration():
        print("\n" + "="*60)
        print("✓ Migration completed successfully!")
        print("="*60)
    else:
        print("\n⚠ Migration completed with warnings")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("\n⚠ ROLLBACK MODE")
        confirm = input("Are you sure you want to drop the table? (yes/no): ")
        if confirm.lower() == "yes":
            rollback_migration()
        else:
            print("Rollback cancelled")
    else:
        main()
