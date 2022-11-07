from mangum import Mangum
from stac_fastapi.pgstac.app import app

handler = Mangum(app)
