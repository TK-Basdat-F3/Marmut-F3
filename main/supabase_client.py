import os
from supabase import create_client, Client

def get_supabase():
    return create_client(os.getenv('https://ibfqonevwbcwcluqqrkx.supabase.co'), os.getenv('process.env.SUPABASE_KEY'))