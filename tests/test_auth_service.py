import pytest

from src.repositories import  InMemoryUserRepository
from src.services import AuthService
from src.exceptions import UserAlreadyExistsError, InvalidCredentialsError


def make_auth_service():
    return AuthService(InMemoryUserRepository())

#Happy path
def test_sign_up_user_username_password():
    #Arrange
    auth_service = make_auth_service()

    #Act
    user = auth_service.sign_up("sandy", "sandy123")

    #Assert
    assert user.username == "sandy"
    assert user.password == "sandy123"

#Happy path
def test_login_gets_user_for_valid_username_and_password():
    #Arrange
    auth_service = make_auth_service()
    auth_service.sign_up("sandy", "sandy123")

    #Act
    user = auth_service.login("sandy", "sandy123")

    #Assert
    assert user.username == "sandy"
    assert user.password == "sandy123"

#Exception handling, Business logic
def test_sign_up_username_already_exists():
    #Arrange
    auth_service = make_auth_service()
    auth_service.sign_up("sandy", "sandy123")

    #Act/Assert
    with pytest.raises(UserAlreadyExistsError):
        auth_service.sign_up("sandy", "sandy123")

#Invalid input, Exception handling
def test_login_with_wrong_password():
    #Arrange 
    auth_service = make_auth_service()
    auth_service.sign_up("sandy", "sandy123")

    #Act/Assert
    with pytest.raises(InvalidCredentialsError):
        auth_service.login("sandy", "sandy123*")

#Invalid input, Exception handling, Boundary / edge
def test_login_this_user_does_not_exist():
    #Arrange
    auth = make_auth_service()

    #Act/Assert
    with pytest.raises(InvalidCredentialsError):
        auth.login("no_user", "apassword")

#Invalid input, Boundary / edge
def test_sign_up_blank_username_raises_error():
    #Arrange
    auth_service = make_auth_service()

    #Act / Assert
    with pytest.raises(InvalidCredentialsError):
        auth_service.sign_up("   ", "sandy123")

#Invalid input, Boundary / edge
def test_sign_up_blank_password_raises_error():
    #Arrange
    auth_service = make_auth_service()

    #Act / Assert
    with pytest.raises(InvalidCredentialsError):
        auth_service.sign_up("sandy", "   ")




