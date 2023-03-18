import json
import os
import shutil
import traceback
from prompts import get_product_manager_prompt
from remote_agent import query_remote_agent
from developer import Developer

# Load config file
with open("config/config.json", "r") as config_file:
    config = json.load(config_file)

product_retries = config["product_retries"]

# Run the whole process with retries
for i in range(product_retries):
    try:
        # Get product manager prompt
        prompt = get_product_manager_prompt(config["product"])
        steps = query_remote_agent(prompt)

        for step in steps:
            step["product"] = config["product"]

        # Process each step with the developer
        developer = Developer(config["developer_retries"])
        success = developer.process_steps(steps)

        if success:
            print("The whole process completed successfully.")
            break
        else:
            print(f"Failed after {i + 1} product retries.")
    except Exception as e:
        print(f"Error in product manager retry {i + 1}: {e}")
        print(traceback.format_exc())

    if os.path.exists("code"):
        for filename in os.listdir("code"):
            file_path = os.path.join("code", filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        print("The 'code' directory does not exist.")

