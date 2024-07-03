import json
import os
import signal
import subprocess
from multiprocessing import Process
from random import randint
from time import sleep, time
from uuid import uuid4

import undetected_chromedriver as uc
from dotenv import dotenv_values, load_dotenv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

import requests

url = 'http://10.44.109.64:8000/upload'
file_path = ''

load_dotenv()

tokens_str = dotenv_values(".env")["TOKENS"]
tokens = [token.strip() for token in tokens_str.split(',')]

prompt_nb = 30
seed = randint(0, 80000000)

diagram_types = [
    "flowchart",
    "sequence diagram",
    "class diagram",
    "state diagram",
    "entity relationship diagram",
    "user journey",
    "gantt",
    "pie chart",
    "quadrant chart",
    "requirement diagram",
    "gitgraph diagram",
    "Mindmaps diagram",
    "Timeline",
    "zenuml",
    "sankey"
]

# prompts = [
#     f"Generate me a json of prompts asking to create a diagram for a specific need. Do not hesitate to add sentence after to specify more how the diagram should be. For each prompt, generate the equivalent mermaid. The prompts ABSOLUTELY needs to be simple and short. The format of your response needs to be a json with 'prompt' and 'output' as the properties for each element. base ta seed de generation des exemples sur {seed}. Genère seulement 5 elements.",
#     "Generate some more",
#     "Again some more but different"
# ]
prompts = [
    f"Generate me a json of prompts asking to create a diagram for a specific need. Do not hesitate to add sentence after to specify more how the diagram should be. For each prompt, generate the equivalent mermaid. The prompts should not have to specify the type of diagram and the output needs to be a guess of what best represent the entry. The prompts sometimes needs to be simple and short. The format of your response needs to be a json with 'prompt' and 'output' as the properties for each element. Generate 1 example for each type: {str(diagram_types[:5])}. Do not generate the markdown for the mermaid"
]

entry_token = "$entry$"

modification_prompt = [
    f"Generate me a json similar to the things you already generated but the prompt need to emulate a client asking for modifications on the given mermaid and the output need to be the modified mermaid. The entry need to the already existing mermaid need be framed by the token: '{entry_token}' and then the prompt asking for modifications comes into play. Here's an example of prompt: {entry_token}old mermaid{entry_token}prompt asking for modification. The format of your response needs to be a json with 'prompt' and 'output' as the properties for each element. Do that for the following prompts {str(diagram_types[:5])}"
]

plus_prompt = lambda a : f"Generate some more for the following types of diagram: {str(a)}"

# prompts += ["Again some more but different" for _ in range(prompt_nb)]

prompts += [plus_prompt(diagram_types[(i * 5) : (i * 5) + (min(5, len(diagram_types) - (i * 5)))]) for i in range(len(diagram_types) // 5 + 1 if len(diagram_types) % 5 else len(diagram_types) // 5)]

#prompts += modification_prompt

# prompts += [plus_prompt(diagram_types[(i * 5) : (i * 5) + (min(5, len(diagram_types) - (i * 5)))]) for i in range(len(diagram_types) // 5 + 1 if len(diagram_types) % 5 else len(diagram_types) // 5)]

# prompts = prompts * prompt_nb

# print(*prompts, sep="\n")
# exit()

def sendData():
    with open(file_path, 'rb') as f:
        # Create a dictionary to hold the file data
        files = {'files': f}
        
        # Send the POST request
        response = requests.post(url, files=files)
        
        # Print the response from the server
        print(response.status_code)
        print(response.text)

def execute_shell_script(script_path):
    try:
        subprocess.run(['sh', script_path], check=True)
        print(f'Shell script "{script_path}" executed successfully.')
    except subprocess.CalledProcessError as e:
        print(f'Error: Failed to execute shell script "{script_path}".')
        print(f'Return code: {e.returncode}, Output: {e.output}')

def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f'File "{file_path}" has been successfully removed.')
    except OSError as e:
        print(f'Error: {file_path} - {e.strerror}')

def merge_file(path_src, path_dest):
    with open(path_src, 'r') as file_src:
        try:
            src_data = json.load(file_src)
        except json.JSONDecodeError:
            print(f"Error: Unable to load JSON from {path_src}")
            return
    
    with open(path_dest, 'r') as file_dest:
        try:
            dest_data = json.load(file_dest)
        except json.JSONDecodeError:
            print(f"Error: Unable to load JSON from {path_dest}")
            return
    
    if not isinstance(src_data, list) or not isinstance(dest_data, list):
        print("Error: Both files should contain JSON arrays (lists).")
        return
    
    merged_data = src_data + dest_data
    
    with open(path_dest, 'w') as merged_file:
        json.dump(merged_data, merged_file, indent=4)
        sendData()

def handler(signum, frame):
    exit(1)
 
class ChatGPT:
    def __init__(self, headless=False, answer_timeout=60, save_file=None, token=None):
        self.__timeout = answer_timeout
        self.__save_file = save_file
        self.__token = token
        self.__initialize_driver(headless)

    def __del__(self):
        self.__driver.close()


    def __save_data(self, data : list[dict]):

        to_save = []

        for entry in data:
            uuid = uuid4()
            filename = f"{uuid}.mmd"
            output_filename = f"{uuid}.svg"
            open(filename, "w").write(entry["output"])

            try:
                subprocess.run(["mmdc","-i", filename, "-o", output_filename])
                os.remove(output_filename)
                to_save.append(entry)
            except:
                ...
            os.remove(filename)
    
        dataset = []
        if os.path.exists(self.__save_file):
            dataset = json.load(open(self.__save_file, "r"))
        dataset.append(to_save)
        
        json.dump(dataset, open(self.__save_file, "w"))


    def __initialize_driver(self, headless):
        self.__driver = uc.Chrome(headless)
        self.__driver.get("https://chatgpt.com/")
        self.__driver.add_cookie({
            "name": "__Secure-next-auth.session-token",
            "value": self.__token
        })
        self.__driver.refresh()

    def prompt(self, prompts):
        results = []
        sleep(randint(5, 6))

        links_elements = self.__driver.find_elements(By.XPATH, "//a[@href]")
        links = [a.get_attribute("href") for a in links_elements]
        travel_link = ""
        for link in links:
            if "/c/" in link:
                travel_link = link
                break

        self.__driver.get(travel_link)

        for i in tqdm(range(len(prompts))):
            sleep(randint(1, 2))

            try:
                textarea = self.__driver.find_element(By.ID, "prompt-textarea")
            except:
                self.__driver.refresh()
                sleep(randint(1, 2))
                continue
            
            ActionChains(self.__driver).move_to_element(textarea).perform()
            textarea.send_keys(prompts[i])
            sleep(randint(1, 2))
            
            # sleep(randint(4, 5))
            textarea.send_keys(Keys.ENTER)
            sleep(randint(2, 3))

            while 1:
                try:
                    close_btn = self.__driver.find_element(By.XPATH, '//*[@id="enforcement-containerchatgpt-freeaccount"]/div[1]')
                    close_btn.click()
                    ActionChains(self.__driver).move_to_element(textarea).perform()
                    sleep(randint(1, 2))
                    textarea.send_keys(Keys.ENTER)
                    sleep(randint(2, 3))
                except:
                    break

            # print("Pre juice button")
            while True:
                try:
                    stop_btn = self.__driver.find_element(By.CSS_SELECTOR, 'button[data-testid="fruitjuice-stop-button"]')
                    break
                except:
                    ...
                try:
                    stop_btn = self.__driver.find_element(By.CSS_SELECTOR, 'svg[xmlns="http://www.w3.org/2000/svg"]')
                    stop_btn = stop_btn.find_element(By.XPATH, "../..")
                    stop_btn.click()
                    sleep(0.5)
                except:
                    ...
                try:
                    self.__driver.find_element(By.CLASS_NAME, "text-token-text-error")
                    return(1)
                except:
                    ...


            start_timeout = time()
            fail = False

            # print("prestopbtn wait")
            while 1:
                try:
                    if not(stop_btn.is_enabled()):
                        break
                except:
                    fail = True
                    break
                if time() - start_timeout > self.__timeout:
                    stop_btn.click()
                    fail = True
                    break

            if not fail:
                try:
                    content = self.__driver.find_elements(By.CSS_SELECTOR, 'div[data-message-author-role="assistant"]')[-1].text
                    content = content[content.index("["):content.rindex("]") + 1].replace("\\\\", "[n]").replace("\n", "").replace("[n]", "\\\\")
                    
                    if self.__save_file:
                        p = Process(target=self.__save_data, args=(json.loads(content),))
                        p.run()
                    else:
                        results.append(content)

                except Exception as e:
                    print(f"Error processing content: {e}")

        return results

def run_instance(instance, prompts):
    instance.prompt(prompts)

def switchToken(token_index):
    token_index += 1
    if token_index < len(tokens):
        print(f"Switching to token {token_index}")
    else:
        print("No more tokens available.")
        token_index = 0
        print(f"Retry with token {token_index}")
    return token_index

def main(prompts):
    token_index = 0
    # with open(file_path, 'a') as file:
    #     file.write('[]')

    while token_index < len(tokens):
        # try:
        instance = ChatGPT(save_file=file_path, token=tokens[token_index])
        if(instance.prompt(prompts) == 1):
            token_index = switchToken(token_index)
        # break
        # except Exception as e:
        #     token_index = switchToken(token_index)

signal.signal(signal.SIGINT, handler)

main(prompts)