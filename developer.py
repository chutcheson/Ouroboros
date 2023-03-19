import os
import subprocess
import traceback
import json
import shutil
from prompts import get_developer_code_prompt, get_developer_error_prompt
from remote_agent import query_remote_agent

class Developer:
    def __init__(self, developer_retries, base_code_dir, logger):
        self.developer_retries = developer_retries
        self.base_code_dir = base_code_dir
        self.logger = logger
        os.makedirs(self.base_code_dir, exist_ok=True)

    def process_steps(self, steps):
        for step in steps:
            success = self._process_step(step)
            if not success:
                return False
        return True

    def clear_code_directory(self):
        for filename in os.listdir(self.base_code_dir):
            file_path = os.path.join(self.base_code_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        os.rmdir(self.base_code_dir)

    def _process_step(self, step):
        retry = False
        for i in range(self.developer_retries):
            try:
                if not retry:
                    self.logger.info("Getting code prompt")
                    code_prompt = get_developer_code_prompt(step)
                    self.logger.debug(f"Code prompt: {code_prompt}")
                    code_response = query_remote_agent(code_prompt, self.logger)
                self._pretty_print_code_files(code_response)
                self._save_code_files(code_response["code"])
                self._save_code_files(code_response["tests"])

                # Run the code and tests
                test_filename = code_response["code"][0]["filename"]
                result = subprocess.run(["python3", f"{self.base_code_dir}/{test_filename}"], capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info(f"Step {step['n']} completed successfully.")
                    return True
                else:
                    self.logger.warning(f"Step {step['n']} failed.")
                    retry = True
                    self.logger.info("Getting error prompt")
                    error_prompt = get_developer_error_prompt(code_prompt, code_response, result.stderr)
                    self.logger.debug(f"Error prompt: {error_prompt}")
                    code_response = query_remote_agent(error_prompt, self.logger)
            except Exception as e:
                self.logger.error(f"Error in developer retry {i + 1}: {e}")
                self.logger.debug(traceback.format_exc())
                continue

        self.logger.warning(f"Failed step {step['n']} after {self.developer_retries} developer retries.")
        return False

    def _save_code_files(self, files):
        for file in files:
            with open(f"{self.base_code_dir}/{file['filename']}", "w") as f:
                f.write(file["content"])

    def _pretty_print_code_files(self, json_data):
        for file_type in ['code', 'tests']:
            self.logger.debug(f"{file_type.capitalize()}:")
            for file in json_data[file_type]:
                self.logger.debug(f"File: {file['filename']}")
                self.logger.debug("Content:")
                self.logger.debug(file['content'])

