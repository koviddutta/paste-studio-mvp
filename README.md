# Paste Studio MVP - Indian Sweets Formulation Engine

Production-ready formulation system for converting 1000+ Indian sweet recipes into gelato pastes.

## Features

✅ 1000+ Indian sweet recipes from Supabase  
✅ Ingredient classification (6 processing classes)  
✅ Detailed 40-step production SOPs  
✅ Property calculations (water activity, shelf-life, viscosity)  
✅ Safety validations and warnings  
✅ Interactive UI with Reflex  

## Setup

1. **Clone the repository:**
bash
git clone https://github.com/koviddutta/paste-studio-mvp.git
cd paste-studio-mvp


2. **Install dependencies:**
bash
pip install -r requirements.txt


3. **Configure environment variables:**
bash
cp .env.example .env
# Edit .env with your Supabase credentials


4. **Set up database:**
- Go to your Supabase dashboard
- Run the SQL in `app/database/schema.sql`

5. **Run the app:**
bash
reflex run


## Environment Variables

Required variables in `.env`:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon/service key

## Tech Stack

- **Backend:** Reflex (Python)
- **Database:** Supabase (PostgreSQL)
- **UI:** Reflex components with Tailwind CSS

## License

MIT
