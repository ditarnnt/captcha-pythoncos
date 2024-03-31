from fastapi import FastAPI, HTTPException
from PIL import Image, ImageDraw, ImageFont
import io
import string
import random
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

FONT_PATH = os.path.join(os.path.dirname(__file__), "Arial.ttf")
font = ImageFont.truetype(FONT_PATH, 15)


dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

class CaptchaResponse(BaseModel):
    captcha_text: str
    image_url: str

# Initialize FastAPI app
app = FastAPI()

# IBM COS Credentials and Configuration
end_point_url_public = "s3.ap.cloud-object-storage.appdomain.cloud"
COS_ENDPOINT = "https://" + end_point_url_public
COS_API_KEY_ID = os.getenv("COS_API_KEY_ID")
COS_INSTANCE_CRN = os.getenv("COS_INSTANCE_CRN")
bucket_name = os.getenv("bucket_name")

print (COS_API_KEY_ID)
print(COS_ENDPOINT)
print(COS_INSTANCE_CRN)
print(bucket_name)

cos_client = ibm_boto3.client(
    "s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT,
)

# Function to generate captcha text
def generate_captcha_text(length=6):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# Function to generate captcha image and upload to IBM COS
@app.get("/captcha", response_model=CaptchaResponse, summary="Generate CAPTCHA", response_description="CAPTCHA text and image URL")
async def get_captcha():
    try:
        # Generate CAPTCHA text
        captcha_text = generate_captcha_text()
        
        # Create an image with the text
        img = Image.new('RGB', (120, 30), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT_PATH, 15)
        d.text((10, 10), captcha_text, fill=(0, 0, 0), font=font)
        
        # Save the image to a byte buffer
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Upload to IBM COS
        file_name = f"captcha-{captcha_text}.png"
        cos_client.upload_fileobj(buffer, Bucket=bucket_name, Key=file_name)

        
        # Generate image URL
        image_url = f"https://{bucket_name}.s3.ap.cloud-object-storage.appdomain.cloud/{file_name}"

        print (f"image url: {image_url}")
        # Return the CAPTCHA text and image URL
        return JSONResponse(content={"captcha_text": captcha_text, "image_url": image_url})
    
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
