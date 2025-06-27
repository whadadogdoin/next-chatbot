

import os
from dotenv import load_dotenv
from vecx.vectorx import VectorX

load_dotenv()

vecx_token = os.getenv("VECX_TOKEN")

vx = VectorX(vecx_token)

index = vx.get_index("next_comp3",)

print(index.describe())


