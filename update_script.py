import re

with open("app/service/email_service.py", "r") as f:
    content = f.read()

replacement = """class FileService:
    \"\"\"File handling service\"\"\"

    @staticmethod
    def save_upload_file(file) -> str:
        \"\"\"Save uploaded file (uses Cloudinary exclusively)\"\"\"
        import os
        from datetime import datetime

        if not hasattr(settings, 'CLOUDINARY_CLOUD_NAME') or not settings.CLOUDINARY_CLOUD_NAME:
            raise ValueError("Cloudinary configuration missing. Check .env")

        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True
            )

            # Reset file pointer if needed and upload
            file.file.seek(0)
            upload_result = cloudinary.uploader.upload(file.file)
            return upload_result.get("secure_url")
        except ImportError:
            raise ImportError("Cloudinary module not found. 'pip install cloudinary'")
        except Exception as e:
            import logging
            logging.error(f"Cloudinary upload failed: {str(e)}")
            raise ValueError(f"Image upload to Cloudinary failed: {str(e)}")
"""

content = re.sub(r'class FileService:.*?return filepath', replacement, content, flags=re.DOTALL)

with open("app/service/email_service.py", "w") as f:
    f.write(content)

