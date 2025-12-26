import logging, time
from modules import price_model, survive_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    while True:
        try:
            logger.info("Training pricer...")
            price_model_instance = price_model.train_cycle()
            if price_model_instance:
                logger.info("Running predictions for pricer...")
                price_model.run_predictions(price_model_instance)
            logger.info("Training survivor...")
            survivor_model_instance = survive_model.train_cycle()
            if survivor_model_instance:
                logger.info("Running predictions for survivor...")
                survivor_model.run_predictions(survivor_model_instance)
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        logger.info("Sleeping for 1 hour...")
        time.sleep(3600)  # Re-check every hour
