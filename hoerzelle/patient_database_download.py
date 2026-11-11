import sqlalchemy as db

DATABASE_URL = "mysql+pymysql://hoerzell:Abcd123$@fbi-mysqllehre.th-brandenburg.de/hoerzell_db"
engine = db.create_engine(DATABASE_URL)

def download_patients():
    with engine.connect() as connection:
        metadata = db.MetaData()
        user_table = db.Table('user', metadata, autoload_with=connection) 

        columns_to_fetch = [
            user_table.columns.lastname, 
            user_table.columns.firstname,
            user_table.columns.date_of_birth, 
            user_table.columns.gender, 
            user_table.columns.email,
            user_table.columns.id
        ]
        
        fetch_user = db.select(*columns_to_fetch)
        
        results = connection.execute(fetch_user).mappings().all()     
    return results