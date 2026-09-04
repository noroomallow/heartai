
# HeartAI

HeartAI is a Flask-based AI relationship analysis application that combines personality assessment, relationship compatibility analysis, astrology-based reflection, chat analysis, an AI relationship coach, progress tracking, and professional PDF reports.

## Features

- Personality assessment
- Relationship compatibility scoring
- AI-powered relationship analysis
- AI Coach with persistent conversation history
- Chat/message analysis
- Astrology-based relationship insights
- 30-day relationship bonding plan
- Relationship progress tracking
- Comprehensive relationship reports
- Professional A4 PDF report export
- AI-generated recommendations
- SQLite database by default
- PostgreSQL support
- Health-check endpoint

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite / PostgreSQL
- Google Gemini API
- TextBlob
- ReportLab
- python-dotenv

## Project Structure

```text
heartai/
├── database/
├── instance/
├── models/
├── routes/
├── services/
├── static/
├── templates/
├── uploads/
├── app.py
├── config.py
├── requirements.txt
├── test.py
├── .env
└── README.md
````

## Requirements

Make sure you have:

* Python 3.10+
* pip
* Git
* A Google Gemini API key

## 1. Clone the Repository

```bash
git clone https://github.com/noroomallow/heartai.git
cd heartai
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Create the `.env` File

Create a file named:

```text
.env
```

in the root directory of the project:

```text
heartai/
├── .env
├── app.py
├── config.py
└── ...
```

### Windows

```bash
type nul > .env
```

### macOS / Linux

```bash
touch .env
```

## 6. Configure `.env`

Add the following configuration:

```env
# Flask
SECRET_KEY=change-this-to-a-long-random-secret-key

# Database
# SQLite is used by default.
DATABASE_URL=sqlite:///heartai.db

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Optional Gemini configuration
GEMINI_MODEL=gemini-3.7-flash
GEMINI_FALLBACK_MODELS=gemini-3.6-flash,gemini-3.5-flash-lite
GEMINI_RETRIES=2
GEMINI_RETRY_BASE_SECONDS=1.5
```

## 7. Get a Gemini API Key

Create a Google Gemini API key from Google AI Studio.

After creating the key, put it in `.env`:

```env
GEMINI_API_KEY=your_actual_api_key
```

Do not commit your real API key to Git.

## 8. Optional PostgreSQL Configuration

HeartAI uses SQLite by default, so PostgreSQL is not required for local development.

If you want to use PostgreSQL, replace:

```env
DATABASE_URL=sqlite:///heartai.db
```

with your PostgreSQL connection string:

```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME
```

Example:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/heartai
```

Make sure PostgreSQL is running before starting the application.

## 9. Verify the Environment

You can verify that the required packages are installed:

```bash
pip list
```

You should see packages including:

```text
Flask
Flask-SQLAlchemy
Werkzeug
python-dotenv
google-genai
textblob
psycopg2-binary
reportlab
```

## 10. Run the Application

Start HeartAI with:

```bash
python app.py
```

The Flask development server will start on:

```text
http://127.0.0.1:5000
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## 11. Health Check

HeartAI provides a health-check endpoint.

Open:

```text
http://127.0.0.1:5000/health
```

A successful response should look similar to:

```json
{
  "status": "ok",
  "application": "HeartAI",
  "gemini": true,
  "model": "gemini-3.7-flash"
}
```

If:

```json
"gemini": false
```

appears, check that `GEMINI_API_KEY` is correctly configured in `.env`.

## 12. Database

For the default SQLite configuration, HeartAI automatically creates the required database and tables when the application starts.

Default configuration:

```env
DATABASE_URL=sqlite:///heartai.db
```

You do not need to manually create the SQLite database.

## 13. Uploads

The application automatically creates the upload directories required by the application when it starts.

The application supports uploaded chat screenshots and related analysis data.

Keep uploaded/private user data out of Git.

## 14. Running Tests

If you want to run the project's test file:

```bash
python test.py
```

## 15. Git Configuration

Make sure sensitive and generated files are not committed.

Recommended `.gitignore` entries:

```gitignore
# Environment
.env
.env.*

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd

# Virtual environment
venv/
.venv/
env/

# Database
*.db
*.sqlite
*.sqlite3

# Uploaded files
uploads/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Test/cache
.pytest_cache/
.coverage
```

## 16. Recommended Development Workflow

```bash
git clone https://github.com/noroomallow/heartai.git
cd heartai

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create and configure .env
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Environment Variables

| Variable                    | Required    | Default                                  | Description                         |
| --------------------------- | ----------- | ---------------------------------------- | ----------------------------------- |
| `SECRET_KEY`                | Recommended | Development key                          | Flask session/security secret       |
| `DATABASE_URL`              | No          | `sqlite:///heartai.db`                   | Database connection                 |
| `GEMINI_API_KEY`            | Yes for AI  | None                                     | Google Gemini API key               |
| `GOOGLE_API_KEY`            | Alternative | None                                     | Alternative Gemini API key variable |
| `GEMINI_MODEL`              | No          | `gemini-3.7-flash`                       | Primary Gemini model                |
| `GEMINI_FALLBACK_MODELS`    | No          | `gemini-3.6-flash,gemini-3.5-flash-lite` | Fallback Gemini models              |
| `GEMINI_RETRIES`            | No          | `2`                                      | Number of API retries               |
| `GEMINI_RETRY_BASE_SECONDS` | No          | `1.5`                                    | Base retry delay                    |

## Example `.env`

```env
SECRET_KEY=heartai_super_secret_development_key_2026
DATABASE_URL=sqlite:///heartai.db
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-3.6-flash
```

```gitignore
venv/
__pycache__/
*.pyc
.env
heartai.db
uploads/
.DS_Store
```

## Troubleshooting

### `ModuleNotFoundError`

Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Gemini API is not working

Check your `.env`:

```env
GEMINI_API_KEY=your_actual_api_key
```

Then restart the application:

```bash
python app.py
```

### Database problems

For local development, remove the SQLite database and restart the application if you intentionally want to recreate the local database:

```bash
rm heartai.db
python app.py
```

On Windows:

```powershell
del heartai.db
python app.py
```

Only do this if you are okay with losing the local SQLite data.

### Port 5000 is already in use

Stop the process using port 5000, or modify the port in `app.py`.

Current configuration:

```python
app.run(
    host="127.0.0.1",
    port=5000,
    debug=True
)
```

## Security Notes

* Never commit `.env`.
* Never expose your Gemini API key publicly.
* Use a strong random `SECRET_KEY` in production.
* Do not commit uploaded user data.
* Do not use Flask's development server for production deployments.
* Use HTTPS in production.
* Use a production WSGI server for deployment.
* Use a production database configuration when deploying at scale.

## Production Checklist

Before deploying:

```text
[ ] Set a strong SECRET_KEY
[ ] Configure production DATABASE_URL
[ ] Configure GEMINI_API_KEY securely
[ ] Disable Flask debug mode
[ ] Configure HTTPS
[ ] Configure a production WSGI server
[ ] Configure persistent storage
[ ] Protect uploaded files
[ ] Configure database backups
[ ] Review application logs
[ ] Do not commit .env
```

## Quick Start

```bash
git clone https://github.com/noroomallow/heartai.git
cd heartai

python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `.env`:

```env
SECRET_KEY=change-this-secret
DATABASE_URL=sqlite:///heartai.db
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.7-flash
GEMINI_FALLBACK_MODELS=gemini-3.6-flash,gemini-3.5-flash-lite
GEMINI_RETRIES=2
GEMINI_RETRY_BASE_SECONDS=1.5
```

Start the application:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## License

Add the project's license information here if a license is defined for the repository.

```
```
