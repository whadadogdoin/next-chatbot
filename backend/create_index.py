from vecx.vectorx import VectorX
import os
from dotenv import load_dotenv

load_dotenv()

vecx_token = os.getenv("VECX_TOKEN")

vx = VectorX(vecx_token)

def index_creation():
    encryption_key = vx.generate_key()
    vx.create_index(
    name="next_enc_idx",
    dimension=1024,
    key=encryption_key,
    space_type="cosine"
    )

index = vx.get_index("next_enc_idx",os.getenv("ENCRYPTION_KEY"))

if __name__=="__main__":
    index_creation()





