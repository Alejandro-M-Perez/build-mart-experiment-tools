# Build Mart Experiment Tools

This repository contains software components used to run the **Build Mart project‑management experiment**.  The goal of the experiment is to compare three conditions—no project manager, a human project manager and an AI project manager—while teams of participants build structures in the Minecraft minigame *Build Mart*.

The tools in this repository support data collection, condition assignment and AI project‑management functionality.  They target **Minecraft 1.21.x** (Java Edition) and are designed to be lightweight and easy to integrate into a Paper/Spigot server.

## Contents

| File | Description |
|---|---|
| `aipm_service.py` | A FastAPI service that plays the role of an AI project manager.  It receives build progress statistics from the instrumentation plugin via HTTP, optionally calls a language model to generate managerial feedback and sends chat messages back to players.  Rate limiting and a placeholder `generate_advice()` function are included; integrate with an LLM of your choice (e.g., OpenAI API) in that function. |
| `latin_square_assigner.py` | Generates Latin–square–based orders for experimental conditions so that each team experiences every condition without order bias.  Run this script to assign condition orders to teams when scheduling sessions. |
| `data_logger.py` | Converts JSON logs produced by the instrumentation plugin into an SQLite database for analysis.  It ingests event time stamps, event types and payloads, making it easy to run SQL queries and export to statistical software. |
| `BuildMartInstrumentationPlugin.java` | A Paper/Spigot plugin for Minecraft 1.21.x.  It captures key events such as block placements/breaks and chat messages, writes them to `events.log` in JSON format and periodically aggregates progress statistics and sends them to the AI PM service via HTTP.  Use this plugin to instrument *Build Mart*. |

## Requirements

- **Minecraft Java Edition 1.21.x** and a **Paper or Spigot server 1.21.x** to host Build Mart.
- Java 17 JDK to compile and run the plugin.
- Python 3.8+ for the scripts and AI service.
- Recommended: `pip install fastapi uvicorn pydantic requests` for running the AI PM service and data logger.

## Setup and Usage

1. **Compile and install the instrumentation plugin**

   - Navigate to the `BuildMartInstrumentationPlugin.java` file and compile it against the Paper API (`paper-api-1.21.x.jar`).  A simple example using Maven or Gradle is recommended; the class is self‑contained and may also be built manually:
     ```bash
     javac -cp paper-api-1.21.0-R0.1-SNAPSHOT.jar BuildMartInstrumentationPlugin.java
     jar cf BuildMartInstrumentationPlugin.jar BuildMartInstrumentationPlugin.class
     ```
   - Place the resulting JAR file in your server’s `plugins/` directory and restart the server.  When players join *Build Mart*, the plugin will create an `events.log` file in the server directory and begin recording events.

2. **Run the AI Project Manager service**

   - Install dependencies: `pip install fastapi uvicorn pydantic requests`.
   - Start the service:
     ```bash
     python3 aipm_service.py
     ```
   - The service will listen on `http://localhost:8000`.  It exposes a `/stats/` endpoint to receive JSON statistics from the plugin.  Customize the `generate_advice()` function to call a language‑model API and return context‑appropriate feedback for players.

3. **Assign conditions using the Latin square assigner**

   - Use `latin_square_assigner.py` to produce balanced orders of the three conditions for your team count:
     ```bash
     python3 latin_square_assigner.py 6 3
     ```
   - The script prints assignments so that each team experiences all conditions in a counterbalanced order.

4. **Convert logs for analysis**

   - After running sessions, use `data_logger.py` to ingest the JSON log file into an SQLite database:
     ```bash
     python3 data_logger.py --input events.log --output experiment.db
     ```
   - You can then query the `events` table or export the database to CSV for statistical analysis.

## Running the Experiment

1. **Install Build Mart** on your Minecraft server and verify that the instrumentation plugin is active (a new `events.log` file appears and chat/placement events are recorded).
2. **Recruit teams** of four participants and assign them to conditions using the Latin–square output.  Ensure each team experiences every condition in a unique order.
3. **Start the AI PM service** if the AI condition is used.  Configure the plugin to send build statistics to the service (by default it uses `http://localhost:8000/stats/`).
4. **Collect logs** from the server after each session and convert them to a database using `data_logger.py`.
5. **Analyze the data** with appropriate statistical methods (e.g., repeated‑measures ANOVA) to compare build performance across conditions.

## Customizing the AI PM Service

The `aipm_service.py` file includes a placeholder function:

```python
def generate_advice(history: str, stats: Dict[str, Any]) -> str:
    """Generate AI project manager advice.

    Replace this function with calls to your preferred LLM provider.
    The inputs include a history of previous advice messages and the
    current build progress statistics.  Return a string to send to players.
    """
    return "Keep going!"
```

Replace this function to call an API such as OpenAI’s `ChatCompletion` or Anthropic’s `Claude`, taking care to abide by your provider’s usage policies and rate limits.  The service will send the returned string to players via the plugin’s chat integration.

## License

No license has been chosen for this repository.  If you wish to add one, choose a license template (e.g., MIT) and update the repository settings.
