from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, insert
from passlib.context import CryptContext
import jwt

from typing import Annotated
from datetime import datetime, timedelta, timezone

from app.backend.db_depends import DBSessionDep
from app.schemas import CreateUser, OutputUser, OutputToken, GetUser
from app.models.user import User, UserRole
from settings import SECRET_KEY, ALGORITHM


router = APIRouter(prefix='/auth', tags=['auth 🔐'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def authenticate_user(db: DBSessionDep, username: str, password: str) -> User:
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password) or user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def create_access_token(username: str, user_id: int, user_role: UserRole, expires_delta: timedelta) -> str:
    payload = {
        'sub': username,
        'id': user_id,
        'user_role': user_role.value,
        'exp': datetime.now(timezone.utc) + expires_delta
    }
    
    # Преобразование datetime в timestamp (количество секунд с начала эпохи)
    payload['exp'] = int(payload['exp'].timestamp())
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> GetUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get('sub')
        user_id: int | None = payload.get('id')
        user_role: str | None = payload.get('user_role')
        expire: int | None = payload.get('exp')
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='No access token supplied'
            )
        if not isinstance(expire, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid token format'
            )
        
        # Проверка срока действия токена
        current_time = datetime.now(timezone.utc).timestamp()
        if expire < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired!'
            )

        return GetUser.model_validate({
            'username': username,
            'id': user_id,
            'user_role': user_role
            })
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired!'
        )
    except jwt.exceptions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )


CurrentUserDep = Annotated[GetUser, Depends(get_current_user)]

@router.get('/read_current_user')
async def read_current_user(user: CurrentUserDep) -> GetUser:
    return user


@router.post('/token', summary='Get access token')
async def login(db: DBSessionDep,
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> OutputToken:
    user = await authenticate_user(db, form_data.username, form_data.password)
    token = await create_access_token(user.username, user.id, user.user_role, expires_delta=timedelta(minutes=20))
    
    return {
        'access_token': token,
        'token_type': 'bearer'
    }


@router.post('/', status_code=status.HTTP_201_CREATED, summary='Create new user')
async def create_user(db: DBSessionDep, create_user: CreateUser) -> OutputUser:
    await db.execute(insert(User).values(**create_user.model_dump(exclude={'password'}),
                                         hashed_password=bcrypt_context.hash(create_user.password)))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'message': 'Successful'
    }
