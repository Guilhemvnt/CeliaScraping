import requests

url = 'http://10.42.0.1:8000/upload'
def sendData(file_path):
    with open(file_path, 'r') as f:
        # Create a dictionary to hold the file data
        files = {'files': f}
        
        # Send the POST request
        response = requests.post(url, files=files)
        
        # Print the response from the server
        print(response.status_code)
        print(response.text)
sendData(input("Enter the file path: "))