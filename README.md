# CodeForge AI

## Revolutionizing Code Analysis with Offline AI Precision




## Overview

CodeForge AI is a cutting-edge offline AI-powered platform that revolutionizes code testing, analysis, and debugging. Using Large Language Models (LLMs), it automates bug detection, test case generation, static analysis, and code completion, enhancing developer productivity without relying on cloud-based AI services.

This project ensures data privacy, offline accessibility, and AI-powered insights, making it ideal for enterprise, research, and security-focused development environments.

## Demo

![Alt Text](/uploads/WEB%20codeforge1.png)

![Demo](/uploads/demo-vid%20-%20Made%20with%20Clipchamp.gif)


![Alt Text](/uploads/Demo.jpeg)

## Key Features

- Offline AI-powered code analysis (LLM-based)
- Automated bug detection and static analysis
- Test case generation and code completion
- OCR and PDF text extraction for scanned code files
- Interactive chatbot for debugging assistance
- Secure authentication and user management
- Speech-To-Text recognition for prompting
- FastAPI backend with MongoDB integration
- Customizable AI models for enhanced code insights



## Project Structure

```
DVT PROJECT FINAL/
│── DVT PROJECT/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── deps.py
│   │   │   ├── utils.py
│   ├── frontend/
│   ├── datasets/
│── myenv/ (virtual environment)
```

- **Backend**: FastAPI-based API for model interaction, authentication, and code analysis  
- **Frontend**: UI for uploading files, testing code, and interacting with AI insights  
- **Datasets**: Stores relevant data for model improvement  



## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, D3.js  
- **Backend**: FastAPI, Python, Pydantic  
- **Database**: MongoDB  
- **LLM Models**: LLaMA 3.2, DeepSeekCoder V2
- **OCR & File Handling**: PyTesseract, PDFPlumber  
- **Security**: JWT Authentication, OAuth2  



## Installation

### Clone the Repository
```
git clone https://github.com/shazmin-67/codeforge-ai.git
cd codeforge-ai
```

### Set Up Virtual Environment
```
python -m venv myenv
source myenv/bin/activate  # (Linux/macOS)
myenv\Scripts\activate     # (Windows)
```

### Install Dependencies
```
pip install -r requirements.txt
```

### Install FFmpeg (Required for Whisper STT)
- **Linux/macOS**: Run `sudo apt install ffmpeg` or `brew install ffmpeg`
- **Windows**: Download from [FFmpeg official site](https://ffmpeg.org/download.html) and add it to the system path.

### Run the FastAPI Server
```
uvicorn backend.app.main:app --reload
```



## Database Configuration

CodeForge AI requires a connection to MongoDB. Either set up a local MongoDB instance or use MongoDB Atlas.

1. **Install MongoDB**: [MongoDB Installation Guide](https://www.mongodb.com/docs/manual/installation/)
2. **Create a Database**: Run MongoDB and create a database named `codeforge_ai`.
3. **Configure the Connection**:
   - Define the connection URI in the `.env` file as `MONGO_URI=mongodb://localhost:27017/codeforge_ai`
   - If using MongoDB Atlas, replace `localhost` with your cluster URI.



## LM Studio and Model Setup

CodeForge AI uses **DeepSeekCoder V2-lite-instruct GGUF** for offline AI-powered analysis. You can switch models by modifying the `/api/chat` route.

### Install LM Studio

1. Download LM Studio from [LM Studio Official Site](https://lmstudio.ai/)
2. Install and launch LM Studio
3. Download **DeepSeekCoder V2-lite-instruct GGUF** from [Hugging Face](https://huggingface.co/)
4. Set up the model in LM Studio

### Configure CodeForge AI to Use a Different Model

To change the model:
1. Open `backend/app/main.py`
2. Locate the `/api/chat` route
3. Modify the model name as needed



## Usage Guide

1. Upload your code via the web interface
2. Interact with the AI chatbot for real-time debugging help
3. View test case generation and static analysis reports
4. Download suggestions and optimized code



## System Architecture

![Alt Text](/uploads/Architecture%20Diagram%20of%20CodeForge.jpg)

1. **Client-Side (Frontend)**
   - Code Editor with syntax highlighting
   - Interactive chatbot for coding assistance

2. **Server-Side (Backend)**
   - FastAPI-based API
   - Secure user authentication
   - LLM-powered analysis engine

3. **Database & LLM Server**
   - MongoDB for user & chat history
   - LLaMA 3.2 or Deepseek Coder V2 lite for AI-powered insights



## Future Enhancements

- Real-time collaboration for teams
- Integration with GitHub for automated code review
- IDE plugin for VS Code and JetBrains IDEs
- Advanced analytics dashboard
- Live debugging capabilities



## Contributing

We welcome contributions. To contribute:

1. Fork the repository
2. Create a new branch (`feature-branch`)
3. Commit your changes
4. Submit a pull request



## License

This project is licensed under the MIT License.