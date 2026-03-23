import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import asyncio
import json
from typing import Dict, Any, Optional
import os


TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "email")

# Simple in-memory cache for verification codes
class CacheService:
    """Simple in-memory cache service"""
    _cache: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def set(key: str, value: Dict[str, Any], ttl: Optional[int] = None):
        """Set a value in cache"""
        import time
        ttl = ttl or settings.CACHE_TTL
        CacheService._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }

    @staticmethod
    def get(key: str) -> Optional[Dict[str, Any]]:
        """Get a value from cache"""
        import time
        if key not in CacheService._cache:
            return None

        cache_item = CacheService._cache[key]
        if time.time() > cache_item['expires_at']:
            del CacheService._cache[key]
            return None

        return cache_item['value']

    @staticmethod
    def delete(key: str):
        """Delete a value from cache"""
        if key in CacheService._cache:
            del CacheService._cache[key]

    @staticmethod
    def clear():
        """Clear all cache"""
        CacheService._cache.clear()

class EmailService:
    """Email sending service"""

    @staticmethod
    def render_template(template_name: str, context: Dict[str, Any]) -> str:
        """Render a very simple HTML template using string replacement.

        This avoids adding a full template engine and is enough for
        personalisation tokens like {{ variable }} in the HTML.
        """

        template_path = os.path.join(TEMPLATES_DIR, template_name)

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            # Fallback: return a minimal plain body
            return context.get("body_text", "")

        # Very small/naive {{ key }} replacement so we don't depend on Jinja2
        rendered = content
        for key, value in context.items():
            rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))

        return rendered

    @staticmethod
    async def send_email(recipient: str, subject: str, body: str, is_html: bool = True) -> bool:
        """Send an email"""
        try:
            # Run blocking email operation in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, EmailService._send_sync, recipient, subject, body, is_html)
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    async def send_templated_email(
        recipient: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
    ) -> bool:
        """Send an HTML email using one of the branded templates.

        All emails going through this helper will get the same
        gold-and-black Ticket Lounge styling.
        """

        html_body = EmailService.render_template(template_name, context)
        return await EmailService.send_email(
            recipient=recipient,
            subject=subject,
            body=html_body,
            is_html=True,
        )

    @staticmethod
    def _send_sync(recipient: str, subject: str, body: str, is_html: bool = True) -> bool:
        """Synchronous email sending (using Mailjet if configured, falling back to basic SMTP)"""
        try:
            # Use Mailjet if API keys are available
            if hasattr(settings, 'MAILJET_API_KEY') and settings.MAILJET_API_KEY and settings.MAILJET_API_SECRET:
                from mailjet_rest import Client
                mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
                data = {
                    'Messages': [
                        {
                            "From": {
                                "Email": settings.EMAIL_FROM,
                                "Name": "EchelonTix"
                            },
                            "To": [
                                {
                                    "Email": recipient,
                                    "Name": recipient.split('@')[0]
                                }
                            ],
                            "Subject": subject,
                            "TextPart": body if not is_html else "",
                            "HTMLPart": body if is_html else ""
                        }
                    ]
                }
                result = mailjet.send.create(data=data)
                return result.status_code == 200

            # Fallback to standard SMTP if no Mailjet API key
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = recipient
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

class FileService:
    """File handling service"""

    @staticmethod
    def save_upload_file(file) -> str:
        """Save uploaded file (uses Cloudinary exclusively)"""
        import os
        from datetime import datetime
        import logging

        if not hasattr(settings, 'CLOUDINARY_CLOUD_NAME') or not settings.CLOUDINARY_CLOUD_NAME:
            raise ValueError("Cloudinary configuration missing. Check .env")

        import cloudinary
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

        try:
            # Reset file pointer if needed and upload
            file.file.seek(0)
            upload_result = cloudinary.uploader.upload(file.file)
            secure_url = upload_result.get("secure_url")
            if not secure_url:
                raise ValueError("Cloudinary upload succeeded but no secure_url in response")
            return secure_url
        except Exception as e:
            logging.error(f"Cloudinary upload failed: {str(e)}")
            raise ValueError(f"Image upload to Cloudinary failed: {str(e)}")


email_service = EmailService()
file_service = FileService()
cache_service = CacheService()
