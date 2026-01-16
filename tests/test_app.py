import pytest
import httpx
from src.app import app, activities
from httpx import ASGITransport
import copy


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    original = {
        "Basketball Team": {
            "description": "Competitive basketball team with practices and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
    }
    activities.clear()
    activities.update(copy.deepcopy(original))


@pytest.mark.asyncio
async def test_get_activities():
    """Test retrieving all activities"""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data


@pytest.mark.asyncio
async def test_signup_for_activity():
    """Test signing up a new participant"""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/activities/Basketball%20Team/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]


@pytest.mark.asyncio
async def test_signup_already_registered():
    """Test that signing up twice fails"""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Try to sign up someone already registered
        response = await ac.post("/activities/Basketball%20Team/signup?email=alex@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


@pytest.mark.asyncio
async def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/activities/Nonexistent%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_unregister_participant():
    """Test unregistering a participant"""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/activities/Basketball%20Team/unregister?email=alex@mergington.edu")
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]


@pytest.mark.asyncio
async def test_unregister_not_registered():
    """Test unregistering someone not registered"""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/activities/Nonexistent%20Club/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
