from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config import DATABASE_URL

Base = declarative_base()

class Filme(Base):
    __tablename__ = 'filmes'
    
    id = Column(Integer, primary_key=True)
    filme = Column(String, nullable=False, unique=True)
    titulo_original = Column(String)
    data_lancamento = Column(String)
    avaliacao = Column(Float)
    duracao = Column(Integer)
    imagem = Column(String)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)
