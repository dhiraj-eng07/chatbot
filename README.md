# Meeting Chatbot

An intelligent chatbot application designed to process meeting transcripts, answer questions about meeting content, and generate summaries.

## Features

- **Meeting Transcript Processing**: Upload and process meeting transcripts
- **Query Understanding**: Answer questions about meeting content
- **Summary Generation**: Generate concise summaries of meetings
- **Entity Extraction**: Identify key entities (dates, participants, action items)
- **Conversation History**: Maintain context across conversation turns

## Project Structure

```
meeting-chatbot/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Application entry point
│   ├── chatbot.py            # Main chatbot logic
│   ├── models.py             # Data models
│   ├── database.py           # Database operations
│   ├── ai_handlers.py        # AI processing logic
│   ├── summary_generator.py  # Summary generation
│   └── config.py             # Configuration management
├── requirements.txt          # Project dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd meeting-chatbot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

Run the chatbot:
```bash
python -m app.main
```

## Configuration

Edit `.env` file with your settings:

- `AI_API_KEY`: Your AI service API key
- `AI_API_PROVIDER`: AI provider (e.g., 'openai')
- `DB_PATH`: Path to database file
- `DEBUG`: Enable debug mode
- `PORT`: Server port
- `HOST`: Server host

## API Modules

### ChatBot (`app/chatbot.py`)
Main chatbot class that handles conversation logic and orchestrates other modules.

### AI Handlers (`app/ai_handlers.py`)
Processes queries and generates responses using AI services.

### Summary Generator (`app/summary_generator.py`)
Generates summaries and extracts key points from meeting transcripts.

### Database (`app/database.py`)
Handles data persistence for meetings and conversations.

### Models (`app/models.py`)
Defines data structures for meetings, messages, and conversations.

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Linting
```bash
flake8 app/
```

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please follow the coding standards and submit pull requests.
