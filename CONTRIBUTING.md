# Contributing to Paste Studio MVP

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Quick Start

1. **Fork the repository**
   bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/paste-studio-mvp.git
   cd paste-studio-mvp
   

2. **Set up development environment**
   bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   

3. **Set up environment variables**
   bash
   # Copy example env file
   cp .env.example .env
   
   # Add your Supabase credentials
   # SUPABASE_URL=your_url_here
   # SUPABASE_KEY=your_key_here
   

4. **Run the app locally**
   bash
   reflex run
   

## 📝 Development Workflow

1. **Create a feature branch**
   bash
   git checkout -b feature/your-feature-name
   

2. **Make your changes**
   - Follow PEP 8 style guide
   - Add docstrings to all functions
   - Use type hints
   - Keep functions under 50 lines

3. **Test your changes**
   bash
   # Run the app and test manually
   reflex run
   
   # Check code formatting
   black app/
   

4. **Commit your changes**
   bash
   git add .
   git commit -m "feat: Add your feature description"
   

5. **Push and create PR**
   bash
   git push origin feature/your-feature-name
   
   Then create a Pull Request on GitHub.

## 🏗️ Project Structure


paste-studio-mvp/
├── app/
│   ├── app.py              # Main Reflex application
│   ├── states/             # State management
│   ├── components/         # UI components
│   ├── engines/            # Business logic (classifier, SOP generator)
│   ├── calculators/        # Property calculations
│   ├── validators/         # Validation rules
│   └── database/           # Database client & schema


## 🎯 Areas for Contribution

### High Priority
- [ ] Add unit tests for calculators
- [ ] Implement PDF export functionality
- [ ] Add ingredient image uploads
- [ ] Create admin dashboard for ingredient management

### Medium Priority
- [ ] Add user authentication
- [ ] Implement custom recipe creation
- [ ] Add batch history tracking
- [ ] Create troubleshooting wizard

### Low Priority
- [ ] Add dark mode support
- [ ] Implement multi-language support
- [ ] Add data visualization charts
- [ ] Create mobile-responsive design improvements

## 📚 Coding Standards

### Python Style
- **PEP 8**: All code must follow PEP 8 guidelines
- **Type hints**: Required for all function parameters
- **Docstrings**: Google-style docstrings for all functions
- **Error handling**: Use try-except with specific error types

### Example Function

def calculate_water_activity(composition: dict[str, float]) -> float:
    """Calculates water activity using the Norrish equation.
    
    Args:
        composition: Dictionary with water, sugar, and protein masses.
        
    Returns:
        The calculated water activity (0.0-1.0).
        
    Raises:
        ValueError: If composition data is invalid.
    """
    try:
        # Implementation
        return aw
    except Exception as e:
        logging.exception(f"Error calculating water activity: {e}")
        raise


### Naming Conventions
- **Functions**: `snake_case` (e.g., `calculate_viscosity`)
- **Classes**: `PascalCase` (e.g., `FormulationState`)
- **Constants**: `UPPER_CASE` (e.g., `MOLAR_MASS_WATER`)
- **Variables**: `snake_case` (e.g., `batch_size_kg`)

## 🔒 Security Guidelines

- **Never commit secrets**: Use .env files (already in .gitignore)
- **Validate user input**: Always validate and sanitize
- **Use parameterized queries**: Prevent SQL injection
- **Handle errors gracefully**: Don't expose stack traces to users

## 🧪 Testing

Currently, the project uses manual testing. Contributions for automated testing are highly welcome!

### Manual Testing Checklist
- [ ] Search for recipes
- [ ] Select different batch sizes
- [ ] Generate formulations
- [ ] Check calculated properties
- [ ] Verify SOP steps
- [ ] Test validation warnings

## 📖 Documentation

- Update README.md for new features
- Add docstrings to all new functions
- Update plan.md if changing architecture
- Add comments for complex logic only

## ❓ Questions?

- Open an issue for bugs
- Start a discussion for feature ideas
- Check existing issues before creating new ones

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Paste Studio MVP! 🎉
