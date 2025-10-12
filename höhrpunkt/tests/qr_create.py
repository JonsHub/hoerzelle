import sqlalchemy as db
import qrcode
import os

engine = db.create_engine('mysql+pymysql://hoerzell:Abcd123$@fbi-mysqllehre.th-brandenburg.de/hoerzell_db')
metadata = db.MetaData()

def get_all_user_ids():
    user_table = db.Table(
        "user",
        metadata,
        db.Column("id", db.Integer, primary_key=True),
        autoload_with=engine
    )

    with engine.connect() as connection:
        query = db.select(user_table.c.id)
        result = connection.execute(query)
        all_ids = [row[0] for row in result.fetchall()] 
        return all_ids

def create_single_qr_code(user_id):
    user_id_str = str(user_id)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(user_id_str)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    
    directory = os.path.join("höhrpunkt", "tests", "codes")
    filename = f"{user_id_str}.png"
    full_path = os.path.join(directory, filename)
    
    os.makedirs(directory, exist_ok=True) 

    try:
        image.save(full_path)
        print(f"QR Code saved for ID {user_id_str} to {full_path}")
        return filename
    except Exception as e:
        print(f"Error saving QR code for ID {user_id_str}: {e}")
        return None

def generate_all_qr_codes():
    user_ids = get_all_user_ids()
    
    if not user_ids:
        print("No user IDs found in the database.")
        return []

    generated_files = []
    for user_id in user_ids:
        filename = create_single_qr_code(user_id)
        if filename:
            generated_files.append(filename)
        
    return generated_files

if __name__ == "__main__":
    generate_all_qr_codes()