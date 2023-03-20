import argparse
import json
import logging
import os
import multiprocessing
import time 
from product_manager import build_product

def setup_logger(product_name, instance_id):

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if instance_id is not None:
        if not os.path.exists(f"logs/{product_name}/{instance_id}"):
            os.makedirs(f"logs/{product_name}/{instance_id}")
        log_file = f"logs/{product_name}/{instance_id}/debug.log"
    else:
        if not os.path.exists(f"logs/{product_name}"):
            os.makedirs(f"logs/{product_name}")
        log_file = f"logs/{product_name}/debug.log"

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

def generate_id(i):
    return f"{int(time.time())}:{i}"

def run_instances(product_name, instances):
    print(f"Running {instances} instances of {product_name}.")
    print(f"Config file: config/config.json")
    print(f"Project directory: projects/{product_name}/")
    print(f"Log directory: logs/{product_name}/")
    print(f"This may take time. Please wait...")
    print(f"Check the log file for progress.")

    with open("config/config.json", "r") as config_file:
        config = json.load(config_file)

    if instances > 1:
        processes = []
        for i in range(instances):
            process_id = generate_id(i)
            process_logger = setup_logger(product_name, process_id)

            process = multiprocessing.Process(target=build_product, args=(product_name, process_id, config, process_logger))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()
    else:
        logger = setup_logger(product_name, None)
        build_product(product_name, None, config, logger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run multiple instances of the product building process.")
    parser.add_argument("product_name", help="Name of the product")
    parser.add_argument("instances", type=int, help="Number", default=1)         
    
    args = parser.parse_args()
    
    run_instances(args.product_name, args.instances)

