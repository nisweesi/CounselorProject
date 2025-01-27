/*
  script.js
  ---------
  Main client-side script for integrating microphone input (via Web Speech API),
  visualizing the audio (via AudioMotionAnalyzer), sending text to the server,
  and retrieving + displaying AI responses.
*/

// Wait for the DOM content to be fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("container");
    const audioElement = document.getElementById("audio");
    const micButton = document.getElementById("micButton");
    const sendButton = document.getElementById("sendButton");
    const userInput = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");
  
    // Global variables
    let audioContext;
    let micSource;
    let recognition;
  
    // Create (or get) AudioMotionAnalyzer instance
    // Will be used to visualize microphone input in real-time
    if (!window.audioMotion) {
      window.audioMotion = new AudioMotionAnalyzer(container, {
        height: 200,
        barSpace: 0.5,
        showScaleX: false,
        showScaleY: false,
        ledBars: true,
        smoothing: 0.7
      });
    }
  
    // Initialize speech recognition
    // (Vendor prefixes: Chrome uses webkitSpeechRecognition)
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = false;
    recognition.lang = "en-US";
    recognition.interimResults = false;
  
    // Attach event listeners to recognition
    recognition.onstart = function () {
      console.log("Speech recognition started...");
      // Turn on the frequency scale in AudioMotion when recording
      window.audioMotion.options.showScaleX = true;
    };
  
    recognition.onresult = function (event) {
        let userSpeech = event.results[0][0].transcript;
        console.log("Recognized speech:", userSpeech);
        userInput.value = userSpeech;
        sendMessage();
    };
    
  
    recognition.onend = function () {
      console.log("Speech recognition ended.");
      // Restore mic button color
      micButton.style.backgroundColor = "#4A4B57";
      // Disconnect the microphone from visualizer
      window.audioMotion.disconnectInput();
    };
  
    recognition.onerror = function (event) {
      console.error("Speech recognition error:", event.error);
      micButton.style.backgroundColor = "#4A4B57";
      // Disconnect the microphone from visualizer if an error occurs
      window.audioMotion.disconnectInput();
    };
  
    // Function to start speech recognition + mic input
    window.startRecognition = async function () {
        try {
            // Create AudioContext only AFTER user interaction (Fix for security warning)
            if (!audioContext) {
                audioContext = new AudioContext(); // Initialize inside user interaction
                console.log("AudioContext created:", audioContext);
            }

            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Ensure we use the SAME AudioContext for both microphone and visualizer
            micSource = audioContext.createMediaStreamSource(stream);

            // Ensure AudioMotionAnalyzer uses the same AudioContext
            if (!window.audioMotion) {
                window.audioMotion = new AudioMotionAnalyzer(container, {
                    audioCtx: audioContext,  // Use the same AudioContext
                    height: 200,
                    barSpace: 0.5,
                    showScaleX: false,
                    showScaleY: false,
                    ledBars: true,
                    smoothing: 0.7,
                });
            }

            window.audioMotion.connectInput(micSource); // Connect microphone to analyzer
            recognition.start();
            document.getElementById("micButton").style.backgroundColor = "red"; // Indicate listening
        } catch (error) {
            console.error("Error accessing microphone:", error);
        }
    };
    
  
    // Function to send text from the input to the Flask server
    async function sendMessage() {
      if (userInput.value.trim() === "") return;
  
      // Display user message in the chat box
      chatBox.innerHTML += `
        <div class="message user-message">
          <strong>You:</strong> ${escapeHtml(userInput.value)}
        </div>
      `;
  
      try {
        // Send the text to the Flask endpoint /chat
        let response = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: userInput.value })
        });

        if (!response.ok) {
          console.error("Server returned an error:", response.status, response.statusText);
        }
  
        let data = await response.json();
        console.log("Chat Response:", data);
  
        // Display AI response in the chat box
        chatBox.innerHTML += `
          <div class="message ai-message">
            <strong>AI:</strong> ${escapeHtml(data.response)}
          </div>
        `;
  
        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
  
        // Optionally speak the AI response (server-side TTS or client TTS)
        await speakResponse(data.response);
  
        // Clear user input
        userInput.value = "";
      } catch (error) {
        console.error("Error sending message:", error);
      }
    }
  
    // Function to call your Flask /speak endpoint (server-based TTS) or do client TTS
    async function speakResponse(text) {
      // Temporarily change the mic button color to indicate "speaking"
      micButton.style.backgroundColor = "yellow";
  
      // ---- Option A: Server-based TTS (Flask endpoint) ----
      // If you have a Flask route that returns an audio file, you could do:
      //
      //   const ttsResponse = await fetch("/speak", { ... });
      //   const audioBlob = await ttsResponse.blob();
      //   audioElement.src = URL.createObjectURL(audioBlob);
      //   audioElement.play();
      //
      // ---- Option B: Client-based TTS (Web Speech API) ----
      // Example:
      const synth = window.speechSynthesis;
      const utterance = new SpeechSynthesisUtterance(text);
      synth.speak(utterance);
  
      // Reset mic button color after finishing speech
      utterance.onend = () => {
        micButton.style.backgroundColor = "#4A4B57";
      };
    }
  
    // Simple helper to avoid HTML injection in user-provided text
    function escapeHtml(unsafe) {
      return unsafe
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }
  
    // Attach listeners to buttons
    micButton.addEventListener("click", startRecognition);
    sendButton.addEventListener("click", sendMessage);
  
    // (Optional) If you want to allow pressing Enter to send messages:
    userInput.addEventListener("keyup", (e) => {
      if (e.key === "Enter") {
        sendMessage();
      }
    });
  });
  