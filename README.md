# Amman Movies

A Django project for tracking movie showings across different cinemas in Amman. The project aggregates showings from multiple cinema websites (Grand, Taj, and Prime) and provides a unified API for accessing movie schedules.

## Features

- Aggregates movie showings from multiple cinemas in Amman
- RESTful API with OpenAPI documentation
- Automatic data collection and parsing
- Fuzzy matching for movie titles across different sources
- Comprehensive test coverage
- Modern development workflow with pre-commit hooks

## Project Structure

```
movies_django/
├── backend/                     # Django project directory
│   ├── movie_showings/         # Project settings
│   ├── showings/              # Main app
│   │   ├── tests/            # Test files
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   ├── test_util.py
│   │   │   └── ...
│   │   ├── migrations/       # Database migrations
│   │   ├── models.py        # Data models
│   │   ├── views.py         # View logic
│   │   ├── urls.py          # URL routing
│   │   ├── services.py      # Business logic
│   │   ├── clients.py       # External API clients
│   │   ├── parsers.py       # Data parsing
│   │   └── util.py          # Utility functions
│   ├── manage.py            # Django management script
│   └── docs/                # Project documentation
├── .vscode/                 # VS Code settings
├── docs/                    # Project-wide documentation
├── .venv/                   # Virtual environment
├── requirements.txt         # Python dependencies
├── .pre-commit-config.yaml  # Pre-commit hooks
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

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

5. Create a `.env` file in the backend directory with your environment variables:

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

## Development

### Code Style

The project uses:

- `black` for code formatting
- `isort` for import sorting
- Pre-commit hooks for automated checks

To format code manually:

```bash
black .
isort .
```

### Testing

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

3. For coverage reports:
   ```bash
   coverage run -m unittest discover
   coverage report
   coverage html  # For HTML report
   ```

### API Documentation

The API documentation is available at `/api/schema/` when running the development server. It's generated using `drf-spectacular`.

## Contributing

1. Create a new branch for your feature:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:

   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. Push your changes:

   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request
