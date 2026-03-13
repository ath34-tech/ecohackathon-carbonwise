import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .db import log_notification

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str, recipient_type: str = "other"):
        """Sends an email and logs it to the database."""
        print(f"📧 [EMAIL SERVICE] Sending email to {to_email}...")
        print(f"Subject: {subject}")
        print(f"Body: {body[:100]}...")

        # In a real app, you'd use SendGrid, Resend, or SMTP
        # For this demo, we'll "send" it to the console and log to DB
        
        log_notification(
            recipient_type=recipient_type,
            identifier=to_email,
            channel="email",
            metadata={"subject": subject, "body_preview": body[:200]}
        )
        
        return {"status": "delivered", "to": to_email}

    @staticmethod
    def send_dealer_lead(dealer_email: str, lead_data: dict):
        subject = f"New High-Intent Lead: {lead_data.get('user_email', 'Valued Customer')}"
        body = f"""
        Hello,
        
        CarbonWise has identified a potential buyer for yours.
        
        Lead Details:
        - Interest: {lead_data.get('vehicle_type', 'Unknown')}
        - Intent: {lead_data.get('intent_type', 'Dealer Search')}
        - Location: {lead_data.get('user_city', 'Active Search Area')}
        
        AI Summary:
        {lead_data.get('ai_draft', 'The user is highly interested in eco-friendly options.')}
        
        Please contact them to follow up.
        
        Best,
        CarbonWise AI Agent
        """
        return EmailService.send_email(dealer_email, subject, body, recipient_type="dealer")
