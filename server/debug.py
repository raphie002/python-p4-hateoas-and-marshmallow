#!/usr/bin/env python3
# server/debug.py
from app import app
from models import db, Newsletter

if __name__ == '__main__':
    
    with app.app_context():
        import ipdb; ipdb.set_trace() # type: ignore
