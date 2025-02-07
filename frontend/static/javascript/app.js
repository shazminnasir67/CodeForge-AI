document.addEventListener("DOMContentLoaded", function () {

    const MAX_MESSAGE_LENGTH = 27000; // Set maximum message length


    const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes in milliseconds

    // Check if session is expired and generate a new session if necessary
    function checkSession() {
        const sessionStartTime = localStorage.getItem("sessionStartTime");
        const sessionId = localStorage.getItem("sessionId");

        if (!sessionStartTime || !sessionId || new Date().getTime() - sessionStartTime > SESSION_TIMEOUT) {
            // Session expired or doesn't exist
            const newSessionId = generateSessionId();
            const newSessionStartTime = new Date().getTime();
            localStorage.setItem("sessionId", newSessionId);
            localStorage.setItem("sessionStartTime", newSessionStartTime);
            return newSessionId;
        }

        return sessionId;
    }

    // Generate a unique session ID (simple example)
    function generateSessionId() {
        return 'session-' + Math.random().toString(36).substr(2, 9);
    }
    // Save a message to session history
    function saveChatHistory(userMessage, aiMessage) {
        const sessionId = checkSession();
        const chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];

        // Save chat messages with timestamp
        chatHistory.push({
            sessionId,
            timestamp: new Date().toLocaleString(),
            userMessage,
            aiMessage
        });

        // Limit chat history length
        if (chatHistory.length > 10) {
            chatHistory.shift(); // Remove the oldest chat if there are more than 10
        }

        localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
    }

    // Display chat history
    function displayChatHistory() {
        const chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];
        const chatList = document.querySelector(".chat-list ul");

        chatList.innerHTML = ""; // Clear the list before repopulating it

        chatHistory.forEach(chat => {
            const listItem = document.createElement("li");
            listItem.textContent = chat.timestamp;
            listItem.onclick = function () {
                loadChatHistory(chat.sessionId);
            };
            chatList.appendChild(listItem);
        });
    }

    // Load a specific chat from history
    function loadChatHistory(sessionId) {
        const chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];
        const chat = chatHistory.find(chat => chat.sessionId === sessionId);

        if (chat) {
            const messagesContainer = document.getElementById("messages");
            messagesContainer.innerHTML = ""; // Clear current chat

            // Display chat history
            const userMessage = document.createElement("div");
            userMessage.classList.add("message", "user-message");
            userMessage.textContent = chat.userMessage;
            messagesContainer.appendChild(userMessage);

            const aiMessage = document.createElement("div");
            aiMessage.classList.add("message", "ai-message");
            aiMessage.textContent = chat.aiMessage;
            messagesContainer.appendChild(aiMessage);

            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    // Call displayChatHistory() when the page loads
    document.addEventListener("DOMContentLoaded", function () {
        displayChatHistory();
    });


    function handleFileSelection() {
        const fileInput = document.getElementById("input-file");
        const fileContainer = document.getElementById("file-container");
        if (fileInput.files && fileInput.files.length > 0) {
            Array.from(fileInput.files).forEach((file) => {
                // Create a new file name box for each selected file
                const fileNameBox = document.createElement('div');
                fileNameBox.classList.add('file-name-box');
    
                // Create file icon span
                const fileIcon = document.createElement('span');
                fileIcon.classList.add('file-icon');
                fileIcon.innerHTML = '&#128194;'; // File icon (can replace with image)
    
                // Create file name span
                const fileNameElement = document.createElement('span');
                fileNameElement.classList.add('file-name');
                fileNameElement.textContent = file.name;
    
                // Create remove button (cross)
                const removeButton = document.createElement('span');
                removeButton.classList.add('file-remove');
                removeButton.innerHTML = '&#10005;';  // Cross symbol
                removeButton.onclick = function() {
                    removeFile(fileNameBox, fileInput, file);
                };
    
                // Append elements to file name box
                fileNameBox.appendChild(fileIcon);  // Add file icon
                fileNameBox.appendChild(fileNameElement);  // Add file name
                fileNameBox.appendChild(removeButton);  // Add remove button
    
                // Append file name box to the container
                fileContainer.appendChild(fileNameBox);
            });
        }
    }
    
    function removeFile(fileNameBox, fileInput, file) {
        // Remove the file name box from the container
        fileNameBox.remove();
    
        // Rebuild the file list (if required) to maintain the correct state in fileInput
        const files = Array.from(fileInput.files).filter(f => f !== file);
        const dataTransfer = new DataTransfer();
        files.forEach(f => dataTransfer.items.add(f));
        fileInput.files = dataTransfer.files;
    
        // Optionally, handle the case where no files are left in the input
        if (fileInput.files.length === 0) {
            fileInput.value = '';  // Reset the input field if no files are left
        }
    }
    
    function handleInputFocus() {
        const h1Element = document.querySelector(".messages-container h1");
        const pElement = document.querySelector(".messages-container p");
        const featureBoxes = document.querySelectorAll(".feature-box");
        const strokeBoxes = document.querySelectorAll(".stroke");

        if (h1Element) h1Element.style.display = "none";
        if (pElement) pElement.style.display = "none"; // Hide the paragraph

        featureBoxes.forEach(box => box.style.display = "none"); // Hide feature boxes
        strokeBoxes.forEach(box => box.style.display = "none");
        const messagesContainer = document.getElementById("messages");
        const existingAIMessage = document.querySelector(".ai-message");

        if (!existingAIMessage) {
            const message = document.createElement("div");
            message.textContent = "How can I help you today?";
            message.classList.add("message", "ai-message");
            messagesContainer.appendChild(message);
        }

        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    window.handleFileSelection = handleFileSelection;
    window.removeFile = removeFile;
    window.handleInputFocus = handleInputFocus;

    function sendMessage() {
        const inputField = document.getElementById("chat-input");
        const userMessage = inputField.value.trim();

        if (!userMessage && fileInput.files.length === 0) {
            alert("Message or file is required.");
            return;
        }

        const MAX_MESSAGE_LENGTH = 27000;
        if (userMessage.length > MAX_MESSAGE_LENGTH) {
            alert(`Message cannot exceed ${MAX_MESSAGE_LENGTH} characters.`);
            return;
        }

        const messagesContainer = document.getElementById("messages");
        const newMessage = document.createElement("div");
        newMessage.classList.add("message", "user-message");
        newMessage.textContent = userMessage;
        messagesContainer.appendChild(newMessage);
        inputField.value = "";
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Send the message to the backend
        const payload = {
            messages: [{ role: "user", content: userMessage }],
            temperature: 0.7,
            language: detectLanguage(userMessage)  // Language detection logic
        };

        fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                const aiMessage = document.createElement("div");
                aiMessage.classList.add("message", "ai-message");

                let formattedMessage = data.message;

                // Handle formatting and append the message
                formattedMessage = formatNonCodeSections(formattedMessage);
                appendFormattedMessage(formattedMessage, aiMessage, data.message);

                messagesContainer.appendChild(aiMessage); 
                // const files = fileInput.files;
                // if (files.length > 0) {
                //     const fileIcon = document.createElement("span");
                //     fileIcon.classList.add("file-icon");
                //     fileIcon.innerHTML = "<i class='fas fa-file'></i>"; // File icon
                //     newMessage.appendChild(fileIcon);
                // }
        
                // messagesContainer.appendChild(newMessage);
                inputField.value = "";
                fileInput.value = "";
                fileContainer.innerHTML = ""; // Remove file preview
                messagesContainer.scrollTop = messagesContainer.scrollHeight;

                // Save chat to history
                saveChatHistory(userMessage, data.message);
            })
            .catch(error => {
                console.error('Error:', error);
                const errorMessage = document.createElement("div");
                errorMessage.classList.add("message", "error-message");
                errorMessage.textContent = "There was an error processing your request.";
                messagesContainer.appendChild(errorMessage);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            });
    }
   
    

    
    
    function detectLanguage(message) {
        const langMatch = message.match(/\b(java|javascript|c\+\+|python|c|c#)\b/i);
        return langMatch ? langMatch[1].toLowerCase() : 'plaintext';
    }

    // Utility to format non-code sections
    function formatNonCodeSections(message) {
        // Apply your heading and text formatting here
        let formatted = message.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"); // Bold
        formatted = formatted.replace(/^## (.*?)$/gm, "<h2>$1</h2>"); // H2
        formatted = formatted.replace(/^### (.*?)$/gm, "<h3>$1</h3>"); // H3
        formatted = formatted.replace(/^## (.*?)$/gm, "<h4>$1</h4>"); // H4

        // Format bullet points (group into a single <ul>)
        formatted = formatted.replace(/(\n|^)\* (.*?)(\n|$)/g, "<li style='margin-left: 24px;>$2</li>");
        formatted = formatted.replace(/(<li>.*<\/li>)+/g, "<ul >$&</ul>");

        // Format numbered lists (group into a single <ol>)
        formatted = formatted.replace(/(\n|^)\d+\. (.*?)(\n|$)/g, "<li style='margin-left: 24px;>$2</li>");
        formatted = formatted.replace(/(<li>.*<\/li>)+/g, "<ol>$&</ol>");






        formatted = formatted.replace(/(<p>.*?<\/p>)(<br>)+/g, "$1<br><br>"); // Ensure spacing between paragraphs

        formatted = formatted.replace(/\n(?!<\/?(ul|ol|li)>)/g, "<br>");
        return formatted;
    }

    // Function to append formatted non-code sections and code blocks
    function appendFormattedMessage(formattedMessage, aiMessage, originalMessage) {
        const codeBlockRegex = /```([\s\S]*?)```/g;
        let match;
        let lastIndex = 0;

        while ((match = codeBlockRegex.exec(originalMessage)) !== null) {
            const codeContent = match[1].trim(); // Extract code content

            // Get the text before the code block and append it
            const textBeforeCode = originalMessage.substring(lastIndex, match.index);
            if (textBeforeCode) {
                const explanationContainer = document.createElement("div");
                explanationContainer.innerHTML = formatNonCodeSections(textBeforeCode); // Format non-code sections
                aiMessage.appendChild(explanationContainer);
            }

            // Create and append the code block (Prism.js handling untouched)
            const codeBlock = document.createElement("pre");
            const codeElement = document.createElement("code");
            codeElement.className = `language-${detectLanguage(originalMessage) || 'plaintext'}`; // Detect language
            codeElement.textContent = codeContent;

            codeBlock.appendChild(codeElement);
            aiMessage.appendChild(codeBlock);
            Prism.highlightElement(codeElement); // Let Prism handle code highlighting

            lastIndex = codeBlockRegex.lastIndex;
        }

        // Append any remaining text after the last code block
        const textAfterCode = originalMessage.substring(lastIndex);
        if (textAfterCode) {
            const explanationContainer = document.createElement("div");
            explanationContainer.innerHTML = formatNonCodeSections(textAfterCode); // Format non-code sections
            aiMessage.appendChild(explanationContainer);
        }
    }


    document.getElementById("chat-input").addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    const micButton = document.querySelector("#mic-button");
    const messagesContainer = document.getElementById("messages");

    micButton.addEventListener("click", async () => {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudioToBackend(audioBlob);
            };

            mediaRecorder.start();
            isRecording = true;
            micButton.classList.add("recording"); // Add a visual indicator for recording
        } catch (error) {
            console.error("Error accessing microphone:", error);
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            micButton.classList.remove("recording");
        }
    }

    async function sendAudioToBackend(audioBlob) {
        const formData = new FormData();
        formData.append("audio", audioBlob, "voice_input.wav");

        try {
            const response = await fetch("http://localhost:8000/api/transcribe", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error("Failed to transcribe audio");
            }

            const data = await response.json();
            if (data.transcription) {
                handleTranscribedMessage(data.transcription);
            }
        } catch (error) {
            console.error("Error sending audio:", error);
        }
    }

    function handleTranscribedMessage(transcribedText) {
        if (!transcribedText.trim()) return;

        // Show user message
        const userMessage = document.createElement("div");
        userMessage.classList.add("message", "user-message");
        userMessage.textContent = transcribedText;
        messagesContainer.appendChild(userMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Send the transcribed text as a chat message
        sendMessage(transcribedText);
    }

    

    let recognition;

    // Check if the browser supports the Web Speech API
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();

        recognition.lang = 'en-US';
        recognition.interimResults = false;

        const micButton = document.querySelector("#mic-button");
        const chatArea = document.querySelector("#messages");
        const voiceInputArea = document.querySelector("#voice-input-area");

        micButton.addEventListener("click", () => {

            chatArea.style.display = "none";
            voiceInputArea.style.display = "flex";

            // Start voice recognition
            recognition.start();
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.querySelector("#chat-input").value = transcript;

            // Restore chat area
            chatArea.style.display = "block";
            voiceInputArea.style.display = "none";
        };

        recognition.onend = () => {
            // Restore chat area if no transcription occurs
            chatArea.style.display = "block";
            voiceInputArea.style.display = "none";
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            // Restore chat area
            chatArea.style.display = "block";
            voiceInputArea.style.display = "none";
        };
    } else {
        alert("Voice input is not supported in your browser.");
    }

});



