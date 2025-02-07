import requests

url = "http://127.0.0.1:1234/chat"
files = {"file": open("C:/Users/HOME/Downloads/harvard.wav", "rb")}
response = requests.post(url, files=files)

print(response.json())  # Should print the transcription result
