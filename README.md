# Amman Movies

A Django project for tracking movie showings across different cinemas in Amman.

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd movies_django
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up VS Code:

   - The project includes a `movies_django.code-workspace` file with shared settings
   - Copy `.vscode/secrets.json.template` to `.vscode/secrets.json`
   - Update the paths in `secrets.json` to match your environment
   - Install recommended VS Code extensions (Python, Django)

5. Create a `.env` file in the root directory with your environment variables:

   ```
   DJANGO_SECRET_KEY=your-secret-key
   DEBUG=True
   ```

6. Run migrations:

   ```bash
   cd backend
   python manage.py migrate
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Testing

The project uses Django's test runner with a custom configuration. To run tests:

1. In VS Code:

   - Use the Testing sidebar (beaker icon)
   - Click the play button to run all tests
   - Or click on individual test files to run specific tests

2. From the command line:
   ```bash
   cd backend
   python manage.py test
   ```

## Project Structure

```
movies_django/
├── backend/                 # Django project directory
│   ├── movie_showings/     # Project settings
│   └── showings/          # Main app
├── .vscode/               # VS Code settings
│   ├── secrets.json      # Local environment settings (not in git)
│   └── secrets.json.template  # Template for secrets.json
├── movies_django.code-workspace  # Shared VS Code workspace settings
└── requirements.txt      # Python dependencies
```

## Development

- The project uses Django's built-in test runner
- Test files are in `backend/showings/tests/`
- Use Faker for generating test data
- Coverage reports are generated with `coverage run -m unittest discover`
