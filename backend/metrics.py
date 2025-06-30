

import os
from dotenv import load_dotenv
from vecx.vectorx import VectorX

load_dotenv()

vecx_token = os.getenv("VECX_TOKEN")

vx = VectorX(vecx_token)

index = vx.get_index("beir_comp1",)

print(index.describe())


