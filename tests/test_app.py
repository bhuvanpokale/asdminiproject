"""
Automated Pytest Test Suite for PlacementPro
Covers Authentication, Dashboard, Applications, Interviews, Preparation, APIs, and Health Check.
"""

import os
import tempfile
import pytest
from app import app, init_db, get_db


@pytest.fixture
def client(tmp_path):
    """Create and configure a clean testing client with an isolated temporary SQLite database."""
    db_file = tmp_path / "test_placementpro.db"
    app.config["TESTING"] = True
    app.config["DATABASE"] = str(db_file)
    app.config["SECRET_KEY"] = "test-secret-key"

    with app.app_context():
        init_db()

    with app.test_client() as client:
        yield client


def register_user(client, username="tester", email="tester@example.com", password="password123"):
    """Helper to register a user in tests."""
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
            "full_name": "Test Student",
            "department": "Computer Engineering",
            "grad_year": "2026",
        },
        follow_redirects=True,
    )


def login_user(client, username="tester", password="password123"):
    """Helper to log in a user in tests."""
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


# -------------------------------------------------------------
# Core Tests matching PDF documentation
# -------------------------------------------------------------


def test_login_page_loads(client):
    """Verify login page renders with status 200 and login form."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Welcome to Placement" in response.data
    assert b"Username or Email" in response.data


def test_registration_page_loads(client):
    """Verify registration page renders with status 200 and fields."""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create Student Account" in response.data
    assert b"Department / Branch" in response.data


def test_dashboard_redirects_logged_out_user(client):
    """Verify unauthenticated user cannot access dashboard and is redirected to login."""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


# -------------------------------------------------------------
# Authentication & User Flow Tests
# -------------------------------------------------------------


def test_user_registration_and_login(client):
    """Verify user registration and subsequent login."""
    reg_response = register_user(client, "alice", "alice@example.com", "securepass")
    assert reg_response.status_code == 200
    assert b"Registration successful" in reg_response.data

    login_response = login_user(client, "alice", "securepass")
    assert login_response.status_code == 200
    assert b"Your placement dashboard" in login_response.data


def test_invalid_login(client):
    """Verify login fails with wrong credentials."""
    response = client.post(
        "/login",
        data={"username": "nonexistent", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data


def test_logout(client):
    """Verify user can log out successfully."""
    register_user(client, "bob", "bob@example.com", "password123")
    login_user(client, "bob", "password123")

    logout_response = client.get("/logout", follow_redirects=True)
    assert logout_response.status_code == 200
    assert b"logged out successfully" in logout_response.data

    # Ensure dashboard is now protected again and redirects with warning message
    dash_response = client.get("/dashboard", follow_redirects=True)
    assert b"Please log in to access this page" in dash_response.data


# -------------------------------------------------------------
# Applications Module Tests
# -------------------------------------------------------------


def test_add_and_list_application(client):
    """Verify adding a job application and verifying it appears in the list."""
    register_user(client, "app_user", "app@example.com", "password123")
    login_user(client, "app_user", "password123")

    response = client.post(
        "/applications/add",
        data={
            "company_name": "Google",
            "role": "Software Engineer",
            "job_type": "Full-time",
            "salary": "₹28 LPA",
            "status": "Applied",
            "application_date": "2026-10-25",
            "deadline": "2026-11-15",
            "job_url": "https://careers.google.com",
            "notes": "Referred by campus alumni",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Application for Google added successfully" in response.data
    assert b"Google" in response.data
    assert b"Software Engineer" in response.data


def test_edit_application(client):
    """Verify updating an application status and details."""
    register_user(client, "edit_user", "edit@example.com", "password123")
    login_user(client, "edit_user", "password123")

    # Add initial application
    client.post(
        "/applications/add",
        data={"company_name": "Microsoft", "role": "SWE", "status": "Applied"},
        follow_redirects=True,
    )

    # Edit application
    response = client.post(
        "/applications/edit/1",
        data={
            "company_name": "Microsoft",
            "role": "Senior SWE",
            "job_type": "Full-time",
            "salary": "₹32 LPA",
            "status": "Offered",
            "notes": "Offer letter received",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"updated successfully" in response.data
    assert b"Offered" in response.data


def test_delete_application(client):
    """Verify deleting an application."""
    register_user(client, "del_user", "del@example.com", "password123")
    login_user(client, "del_user", "password123")

    client.post(
        "/applications/add",
        data={"company_name": "TestCorp", "role": "Intern"},
        follow_redirects=True,
    )

    del_response = client.post("/applications/delete/1", follow_redirects=True)
    assert del_response.status_code == 200
    assert b"Application deleted successfully" in del_response.data


# -------------------------------------------------------------
# Interviews Module Tests
# -------------------------------------------------------------


def test_add_and_list_interview(client):
    """Verify scheduling and viewing an interview."""
    register_user(client, "int_user", "int@example.com", "password123")
    login_user(client, "int_user", "password123")

    response = client.post(
        "/interviews/add",
        data={
            "company_name": "Amazon",
            "round_type": "Technical Round 1",
            "interview_date": "2026-10-30",
            "interview_time": "15:00",
            "interview_mode": "Virtual",
            "meeting_link": "https://chime.aws/test-interview",
            "status": "Scheduled",
            "notes": "Review Binary Search and Graph Traversal",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Interview with Amazon scheduled successfully" in response.data
    assert b"Amazon" in response.data
    assert b"Technical Round 1" in response.data


# -------------------------------------------------------------
# Preparation & Progress Tests
# -------------------------------------------------------------


def test_add_and_toggle_preparation_topic(client):
    """Verify adding a preparation topic and toggling its completion status."""
    register_user(client, "prep_user", "prep@example.com", "password123")
    login_user(client, "prep_user", "password123")

    # Add custom topic
    add_response = client.post(
        "/preparation/add",
        data={
            "category": "System Design",
            "title": "Database Sharding and Replication",
            "difficulty": "Hard",
            "status": "In Progress",
            "resource_url": "https://github.com/donnemartin/system-design-primer",
            "notes": "Horizontal vs vertical partitioning",
        },
        follow_redirects=True,
    )
    assert add_response.status_code == 200
    assert b"Database Sharding and Replication" in add_response.data

    # Toggle status of first auto-seeded topic (ID 1)
    toggle_response = client.post("/preparation/toggle/1", follow_redirects=True)
    assert toggle_response.status_code == 200
    assert b"Updated status" in toggle_response.data


# -------------------------------------------------------------
# API, Dashboard Metrics, and Health Check Tests
# -------------------------------------------------------------


def test_api_stats(client):
    """Verify the /api/stats endpoint returns correct JSON format."""
    register_user(client, "api_user", "api@example.com", "password123")
    login_user(client, "api_user", "password123")

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert "applications" in data
    assert "interviews" in data
    assert "offers" in data
    assert "prep_percentage" in data


def test_health_endpoint(client):
    """Verify /health endpoint returns HTTP 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert json_data["app"] == "PlacementPro"
