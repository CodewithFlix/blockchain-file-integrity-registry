# backend/main.py
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session

# === IMPORT blockchain client kamu ===
from integrity_client import register_file as bc_register_file, verify_file as bc_verify_file

# ========== CONFIG ==========
DATABASE_URL = "sqlite:///./app.db"
SECRET_KEY = "GANTI_INI_DENGAN_SECRET_KEY_YG_KEREN"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 hari

# ========== DB SETUP ==========
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    credits = Column(Integer, nullable=False, default=20)
    created_at = Column(DateTime, default=datetime.utcnow)

    files = relationship("FileRecord", back_populates="user")


class FileRecord(Base):
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, index=True)
    tx_hash = Column(String, nullable=True)
    block_number = Column(Integer, nullable=True)

    # nama kolom di DB tetap "metadata",
    # tapi nama atribut Python diganti "metadata_"
    metadata_ = Column("metadata", String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="files")

Base.metadata.create_all(bind=engine)

# ========== SECURITY / AUTH ==========
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user


# ========== SCHEMAS ==========
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    credits: int

    class Config:
        orm_mode = True


class FileRecordOut(BaseModel):
    id: int
    filename: str
    file_hash: str
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    metadata_: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class VerifyResultOut(BaseModel):
    filename: str
    file_hash: str
    on_chain: bool
    match: Optional[bool]
    record: Optional[dict]


# ========== APP ==========
app = FastAPI(title="Blockchain File Integrity Registry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # untuk dev, nanti bisa dibatasi ke domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/register", response_model=UserOut)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        credits=20,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username.lower()).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@app.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/files/register", response_model=FileRecordOut)
async def register_file(
    file: UploadFile = File(...),
    metadata: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="No credits remaining. Please top up.",
        )

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    try:
        result = bc_register_file(str(tmp_path), metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blockchain error: {e}",
        )

    current_user.credits -= 1
    record = FileRecord(
         user_id=current_user.id,
         filename=file.filename,
         file_hash=result["file_hash"],
         tx_hash=result["tx_hash"],
         block_number=result["block_number"],
         metadata_=metadata,
    )
    db.add(record)
    db.add(current_user)
    db.commit()
    db.refresh(record)

    return record


@app.post("/files/verify", response_model=VerifyResultOut)
async def verify_file(
    file: UploadFile = File(...),
):
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    try:
        result = bc_verify_file(str(tmp_path))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blockchain error: {e}",
        )

    return VerifyResultOut(
        filename=file.filename,
        file_hash=result["file_hash"],
        on_chain=result["on_chain"],
        match=result.get("match"),
        record=result.get("record"),
    )


@app.get("/files", response_model=List[FileRecordOut])
def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = (
        db.query(FileRecord)
        .filter(FileRecord.user_id == current_user.id)
        .order_by(FileRecord.created_at.desc())
        .all()
    )
    return records
