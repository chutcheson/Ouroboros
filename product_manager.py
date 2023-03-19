import json
import os
import shutil
import traceback
from prompts import get_product_manager_prompt
from remote_agent import query_remote_agent
from developer import Developer

def build_product(product_name, unique_id, config, logger):
    logger.info(f"Starting build process for product.")

    product_retries = config["product_retries"]
    
    if unique_id is None:
        base_code_dir = f"project/{product_name}"
    else:
        base_code_dir = os.path.join(f"project/{product_name}", str(unique_id))

    for i in range(product_retries):
        try:
            prompt = get_product_manager_prompt(config["product"])
            logger.info(f"Querying remote agent for steps.")
            steps = query_remote_agent(prompt, logger)

            for step in steps:
                step["product"] = config["product"]

            logger.info(f"Starting developer process.")
            developer = Developer(config["developer_retries"], base_code_dir, logger)
            success = developer.process_steps(steps)

            if success:
                logger.info(f"The whole process completed successfully for product.")
                break
            else:
                logger.warning(f"Failed after {i + 1} product retries for product.")
        except Exception as e:
            logger.error(f"Error in product manager retry {i + 1}.")
            logger.error(traceback.format_exc())

        developer.clear_code_directory()

