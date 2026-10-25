"""
Seed script for PlacementPro.
Populates realistic sample data matching the project demo screenshots.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from app import init_db, app

DB_PATH = app.config["DATABASE"]


def seed():
    # Ensure tables exist
    with app.app_context():
        init_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing data for fresh demo
    cursor.execute("DELETE FROM preparation_topics")
    cursor.execute("DELETE FROM interviews")
    cursor.execute("DELETE FROM applications")
    cursor.execute("DELETE FROM users")

    # 1. Create Demo User
    demo_password_hash = generate_password_hash("password123")
    cursor.execute(
        """
        INSERT INTO users (id, username, email, password_hash, full_name, college, department, grad_year)
        VALUES (1, 'shrawni', 'shrawni@example.com', ?, 'Shrawni Patil', 'College of Engineering', 'Computer Engineering', '2026')
        """,
        (demo_password_hash,),
    )

    # 2. Add Applications (3 applications: 1 Offered, 1 Interviewing, 1 Applied)
    cursor.execute(
        """
        INSERT INTO applications (id, user_id, company_name, role, job_type, salary, status, application_date, deadline, job_url, notes)
        VALUES 
        (1, 1, 'Google', 'Software Development Engineer - 1', 'Full-time', '₹28 LPA', 'Interviewing', '2026-10-10', '2026-10-30', 'https://careers.google.com', 'Referral received from alumni. Technical rounds ongoing.'),
        (2, 1, 'Microsoft', 'Software Engineer (SWE)', 'Full-time', '₹24 LPA', 'Offered', '2026-09-15', '2026-10-01', 'https://careers.microsoft.com', 'Offer received! 4 rounds of interviews cleared successfully.'),
        (3, 1, 'Amazon', 'Cloud Solutions Architect Associate', 'Full-time', '₹22 LPA', 'Applied', '2026-10-18', '2026-11-05', 'https://amazon.jobs', 'Online assessment submitted. Waiting for results.')
        """
    )

    # 3. Add Interviews (2 upcoming / active interviews)
    cursor.execute(
        """
        INSERT INTO interviews (id, user_id, application_id, company_name, round_type, interview_date, interview_time, interview_mode, meeting_link, status, notes)
        VALUES
        (1, 1, 1, 'Google', 'Technical Round 2 - System Design & Coding', '2026-10-28', '14:30', 'Virtual', 'https://meet.google.com/xyz-placement-pro', 'Scheduled', 'Review Trie, Graph algorithms, and cache design beforehand.'),
        (2, 1, 3, 'Amazon', 'Technical Round 1 - DSA & Problem Solving', '2026-10-31', '11:00', 'Virtual', 'https://chime.aws/placement-interview', 'Scheduled', 'Focus on Leadership Principles and Trees/Graphs.')
        """
    )

    # 4. Add Preparation Topics (100% completed or high progress)
    cursor.execute(
        """
        INSERT INTO preparation_topics (id, user_id, category, title, difficulty, status, resource_url, notes)
        VALUES
        (1, 1, 'Data Structures & Algorithms', 'Dynamic Programming & Memoization', 'Hard', 'Completed', 'https://leetcode.com', 'Solved 25 LeetCode DP questions.'),
        (2, 1, 'Core Computer Science', 'OS: Concurrency, Deadlocks & Virtual Memory', 'Medium', 'Completed', 'https://geeksforgeeks.org', 'Reviewed Peterson solution and page replacement algorithms.'),
        (3, 1, 'Core Computer Science', 'DBMS: SQL Joins, Indexing & B-Trees', 'Medium', 'Completed', 'https://geeksforgeeks.org', 'Prepared ACID properties and transaction isolation levels.'),
        (4, 1, 'System Design', 'Microservices Architecture & API Gateways', 'Medium', 'Completed', 'https://github.com', 'Studied load balancers, CDN, and Redis caching.'),
        (5, 1, 'Behavioral & HR', 'Amazon Leadership Principles & STAR Stories', 'Easy', 'Completed', 'https://themuse.com', 'Framed 5 behavioral scenarios.')
        """
    )

    conn.commit()
    conn.close()
    print("Database successfully seeded with demo user and placement data!")


if __name__ == "__main__":
    seed()
