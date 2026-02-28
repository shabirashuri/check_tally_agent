from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse
from sqlalchemy.orm import Session as DBSession
from app.models.user import User
from app.db.base import get_db
from app.utils.password_hashing import hash_pass, verify_pass
from app.utils.jwt_handler import create_access_token
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: DBSession = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user: User registration data
        db: Database session
        
    Returns:
        Created user information
    """
    try:
        logger.info(f"Signup attempt for email: {user.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        new_user = User(
            id=str(uuid.uuid4()),
            email=user.email,
            username=user.username,
            password_hash=hash_pass(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User registered successfully: {user.email}")
        
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Signup error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=UserLoginResponse)
def login_user(
    user_input: UserLogin,
    db: DBSession = Depends(get_db)
):
    """
    Login user and receive access token
    
    Args:
        user_input: Login credentials
        db: Database session
        
    Returns:
        Access token and user information
    """
    try:
        logger.info(f"Login attempt for email: {user_input.email}")
        
        # Find user by email
        db_user = db.query(User).filter(User.email == user_input.email).first()
        if not db_user:
            logger.warning(f"User not found: {user_input.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_pass(user_input.password, db_user.password_hash):
            logger.warning(f"Invalid password for user: {user_input.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create access token with 'sub' claim for user identification
        token = create_access_token({"sub": db_user.id, "email": db_user.email})
        logger.info(f"Successful login: {user_input.email}")
        
        return UserLoginResponse(
            email=db_user.email,
            username= db_user.username,
            access_token=token,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )