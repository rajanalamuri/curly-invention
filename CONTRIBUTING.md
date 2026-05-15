# Contributing to manifest-versioning

Thank you for your interest in contributing to manifest-versioning!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/manifest-versioning.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
5. Install in development mode: `pip install -e ".[dev]"`

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest tests/`
4. Format code: `black manifest_versioning/ tests/`
5. Check linting: `flake8 manifest_versioning/ tests/`
6. Commit with descriptive messages
7. Push to your fork and create a pull request

## Code Style

- Use Black for code formatting
- Follow PEP 8 guidelines
- Add docstrings to functions and classes
- Write tests for new functionality

## Testing

- All pull requests must include tests
- Aim for >80% code coverage
- Run tests locally before submitting PR: `pytest tests/ -v`

## Bug Reports

Include:
- Python version
- manifest-versioning version
- Clear description of the issue
- Minimal reproducible example
- Expected vs actual behavior

## Feature Requests

- Clearly describe the use case
- Explain why this feature is needed
- Suggest implementation approach if possible
