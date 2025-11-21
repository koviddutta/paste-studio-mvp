# Contributing to Paste Studio MVP

Thank you for your interest in contributing to Paste Studio MVP!

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/paste-studio-mvp.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up `.env` with your Supabase credentials
6. Run the app: `reflex run`

## Coding Standards

### Python Style
- Follow PEP 8 (use `black` formatter)
- Add type hints to all function parameters
- Write Google-style docstrings
- Keep functions under 50 lines
- Use descriptive variable names

### Example:

def calculate_water_activity(
    composition: Composition, constants: dict[str, float]
) -> float | None:
    """Calculates water activity (Aw) using the Norrish equation.

    Args:
        composition: A dictionary with the mass of water, sugar, and protein.
        constants: A dictionary of formulation constants from the database.

    Returns:
        The calculated water activity (Aw) value, or None on error.
    """
    # Implementation


## Submitting Changes

1. Make your changes
2. Run tests (if available)
3. Format code: `black .`
4. Commit: `git commit -m "feat: add new feature"`
5. Push: `git push origin feature/your-feature`
6. Create a Pull Request

## Pull Request Guidelines

- Clear description of changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure all checks pass

## Questions?

Open an issue or discussion on GitHub.
