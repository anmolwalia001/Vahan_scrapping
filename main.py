from configs.setting import load_logging_config
import logging

# Initialize logging
load_logging_config()
logger = logging.getLogger("app")

def main():
    logger.info("Application started")
    logger.debug("Debugging details here...")
    logger.error("Sample error message")

if __name__ == "__main__":
    main()
