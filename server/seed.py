#!/usr/bin/env python3
# server/seed.py
from faker import Faker # type: ignore
import random
from app import app
from models import db, Newsletter, Comment

with app.app_context():
    fake = Faker()

    print("Clearing database...")
    Comment.query.delete()
    Newsletter.query.delete()

    print("Seeding newsletters...")
    newsletters = []
    for _ in range(10):
        n = Newsletter(
            title=fake.text(max_nb_chars=20),
            body=fake.paragraph(nb_sentences=5),
        )
        newsletters.append(n)
    
    db.session.add_all(newsletters)
    db.session.commit()

    print("Seeding comments...")
    comments = []
    for n in newsletters:
        # Give each newsletter 1-3 random comments
        for _ in range(random.randint(1, 3)):
            c = Comment(
                text=fake.sentence(),
                newsletter_id=n.id
            )
            comments.append(c)

    db.session.add_all(comments)
    db.session.commit()

    print("Done seeding!")