import os
import subprocess
import traceback
import json
from prompts import get_developer_code_prompt, get_developer_error_prompt
from remote_agent import query_remote_agent

class Developer:
    def __init__(self, developer_retries):
        self.developer_retries = developer_retries

    def process_steps(self, steps):
        for step in steps:
            success = self._process_step(step)
            if not success:
                return False
        return True

    def _process_step(self, step):
        retry = False
        for i in range(self.developer_retries):
            try:
                if not retry:
                    print("getting code prompt")
                    code_prompt = get_developer_code_prompt(step)
                    print("getting initial response")
                    code_response = query_remote_agent(code_prompt)
                self._pretty_print_code_files(code_response)
                self._save_code_files(code_response["code"])
                self._save_code_files(code_response["tests"])

                # Run the code and tests
                test_filename = code_response["code"][0]["filename"]
                result = subprocess.run(["python3", f"code/{test_filename}"], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"Step {step['n']} completed successfully.")
                    return True
                else:
                    print(f"Step {step['n']} failed.")
                    retry = True
                    print("getting error prompt")
                    error_prompt = get_developer_error_prompt(code_prompt, code_response, result.stderr)
                    print("getting error response")
                    code_response = query_remote_agent(error_prompt)
            except Exception as e:
                print(f"Error in developer retry {i + 1}: {e}")
                print(traceback.format_exc())
                continue

        print(f"Failed step {step['n']} after {self.developer_retries} developer retries.")
        return False

    def _save_code_files(self, files):
        if not os.path.exists("code"):
            os.makedirs("code")

        for file in files:
            with open(f"code/{file['filename']}", "w") as f:
                f.write(file["content"])

    def _pretty_print_code_files(self, json_data):
        for file_type in ['code', 'tests']:
            print(f"{file_type.capitalize()}:\n")
            for file in json_data[file_type]:
                print(f"File: {file['filename']}")
                print("Content:")
                print(file['content'])
                print("\n")
