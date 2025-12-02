# Contributing to Paste Studio MVP

Thank you for your interest in contributing to Paste Studio! This document provides guidelines and instructions for setting up your development environment and submitting contributions.

## Development Setup

### Prerequisites
- Python 3.13+
- Git

### Installation

1. **Clone the repository**
   bash
   git clone https://github.com/koviddutta/paste-studio-mvp.git
   cd paste-studio-mvp
   

2. **Install Dependencies**
   bash
   pip install -r requirements.txt
   

3. **Environment Configuration**
   - Copy the example environment file:
     bash
     cp app/.env.example .env
     
   - Fill in your Supabase credentials in `.env`.

4. **Initialize Reflex**
   bash
   reflex init
   

5. **Run the App**
   bash
   reflex run
   

## Project Structure

The application follows a modular architecture within the `app/` directory:

- `calculators/`: Scientific logic for viscosity, water activity, etc.
- `components/`: Reusable UI components (Tailwind + Reflex).
- `constants/`: Scientific constants and configuration.
- `database/`: Supabase clients and data mappers.
- `engines/`: Business logic orchestrators.
- `services/`: High-level services.
- `states/`: Reflex state management.
- `validators/`: Quality and safety checks.

## Coding Standards

- **Type Hinting**: All functions must have type hints.
- **Reflex Patterns**:
  - Use `rx.cond` for conditionals in UI code.
  - Use `rx.match` for multiple conditionals (3+) in UI code.
  - Use `rx.foreach` for loops in UI code.
  - State variables must be strongly typed.
- **Formatting**: The project uses standard Python formatting.

## Pull Request Process

1. Create a new branch for your feature or fix.
2. Ensure all tests pass (if applicable).
3. Submit a Pull Request with a clear description of changes.

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
