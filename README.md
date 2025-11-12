# AutoVidAI: The Automated Social Media Video Engine

AutoVidAI is a headless, API-first orchestration engine built in Python to fully automate the production of short-form social media videos. The goal is to create a fully autonomous, "set and forget" content pipeline by composing a series of micro-tasks powered by best-in-class APIs.

The engine currently operates as a **5-stage workflow**, passing structured JSON payloads between each stage to maintain state.

---

## 🚀 How It Works

The system takes a single-word niche (e.g., "Stoicism") and executes the following automated pipeline:

### **Stage 1: Content Strategy (Idea Engine)**
- Uses **Google's Gemini API** to brainstorm a structured, potentially viral video concept based on the input niche.

### **Stage 2: Scripting (Scriptwriter)**
- Takes the concept from Stage 1 and uses further LLM processing to expand it into a detailed, scene-by-scene script optimized for short-form video.

### **Stage 3: Asset Generation (Media Engine)**
- Makes parallel API calls to source all necessary media.
- Fetches relevant stock video clips from the **Pexels API**.
- Generates realistic TTS voiceovers for each scene's narration using the **ElevenLabs API**.

### **Stage 4: Rendering (Video Assembly)**
- Assembles the final edit by sending the script, video assets, and audio assets to the **Shotstack Video API** for programmatic, cloud-based rendering.

### **Stage 5: Distribution (In Development)**
- The final stage will be responsible for programmatically uploading the finished video to social media platforms.

---

## 🛠️ Tech Stack & Architecture

This project is a demonstration of API orchestration and building a resilient, multi-step automated workflow.

**Orchestration & Logic:** Python  
**Core Libraries:** `requests`, `python-dotenv`, `shotstack-sdk`

### **AI & Content APIs:**
- **Google Gemini API:** For idea generation and scripting.
- **Pexels API:** For high-quality stock video footage.
- **ElevenLabs API:** For realistic text-to-speech voiceover synthesis.

### **Cloud Rendering:**
- **Shotstack API:** For programmatic video editing and rendering.

---

## ⚙️ Setup and Installation

To get this project running locally, follow these steps.

### **Quick Setup (Recommended)**

Run the setup script that automates the entire setup process:

```bash
./setup.sh
```

This will:
- Check for Python 3
- Create a virtual environment
- Install all dependencies
- Create a `.env` file from the template
- Set up the temp directory

### **Manual Setup**

If you prefer to set up manually, follow these steps:

### **1. Clone the Repository:**
```bash
git clone https://github.com/mamun-apu/autovidai-engine.git
cd autovidai-engine
```

### **2. Create and Activate a Virtual Environment:**
This project requires a virtual environment to manage dependencies.

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it (on macOS/Linux)
source venv/bin/activate
```

### **3. Install Dependencies:**
Install all the required Python packages.

```bash
pip3 install -r requirements.txt
```

### **4. Set Up Environment Variables:**
You will need API keys from all the services used in this project.

1. Create a `.env` file in the root of the project:
   ```bash
   touch .env
   ```

2. Add the following lines to your `.env` file, replacing the placeholders with your actual keys:
   ```env
   GEMINI_API_KEY="YOUR_GEMINI_KEY_HERE"
   PEXELS_API_KEY="YOUR_PEXELS_KEY_HERE"
   ELEVENLABS_API_KEY="YOUR_ELEVENLABS_KEY_HERE"
   SHOTSTACK_API_KEY="YOUR_SHOTSTACK_KEY_HERE"
   ```

---

## ▶️ How to Run

Once the setup is complete, you can run the entire pipeline with a single command from the project's root directory:

```bash
python3 main.py
```

The script will print status updates for each stage to the console. The final rendered video URL will be displayed at the end of a successful run.

---

## 🗺️ Future Roadmap

This project is an ongoing proof-of-concept. The planned next steps include:

- **Stage 5 (Distributor):** Implementing programmatic uploads using the YouTube Content API, handling OAuth 2.0 for user authentication.
- **Scheduling & Job Queues:** Integrating APScheduler for autonomous, scheduled runs and eventually moving to a more robust job queue system like Celery/Redis.
- **Front-End Control Panel:** Building a React-based UI to manage niches, view render history, and provide a real-time logging dashboard (likely via WebSockets).
- **CI/CD:** Setting up a simple CI/CD pipeline with GitHub Actions for automated testing and deployment.

---

## 🤝 Contributing

Feel free to open issues or pull requests with suggestions!

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

