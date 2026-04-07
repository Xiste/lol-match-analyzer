from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine("sqlite:///data/lol.db")