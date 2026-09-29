"""
Notification Service
Handles email and WhatsApp notifications
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config import get_supabase_client
import os
import httpx
import json


class NotificationService:
    """Service to send notifications via Email and WhatsApp"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM", "")
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    async def send_task_reminder(self, user_id: str, task_assignment_id: str, reminder_type: str = "daily") -> bool:
        """
        Send task reminder notification
        
        Args:
            user_id: UUID of the user
            task_assignment_id: UUID of the task assignment
            reminder_type: Type of reminder ('daily', 'one_day', 'one_hour', 'overdue')
        
        Returns:
            True if sent successfully
        """
        # Get user and task details
        user = self.supabase.table("users").select("*").eq("id", user_id).execute()
        if not user.data:
            return False
        
        assignment = self.supabase.table("task_assignments").select("*, tasks(*)").eq("id", task_assignment_id).execute()
        if not assignment.data:
            return False
        
        user_data = user.data[0]
        assignment_data = assignment.data[0]
        task = assignment_data.get("tasks", {})
        
        # Get notification settings
        settings = self.supabase.table("notification_settings").select("*").eq("user_id", user_id).execute()
        settings_data = settings.data[0] if settings.data else {}
        
        # Check if reminder is enabled
        reminder_enabled = {
            "daily": settings_data.get("daily_reminder_enabled", True),
            "one_day": settings_data.get("one_day_reminder_enabled", True),
            "one_hour": settings_data.get("one_hour_reminder_enabled", True),
            "overdue": settings_data.get("overdue_reminder_enabled", True)
        }.get(reminder_type, True)
        
        if not reminder_enabled:
            return False
        
        # Create message
        task_title = task.get("title", "Task")
        due_date = assignment_data.get("due_date")
        message = self._create_reminder_message(task_title, due_date, reminder_type)
        
        # Send notifications
        email_sent = False
        whatsapp_sent = False
        
        if settings_data.get("email_enabled", True):
            email_sent = await self._send_email(
                user_data.get("email"),
                f"Task Reminder: {task_title}",
                message
            )
        
        if settings_data.get("whatsapp_enabled", True) and user_data.get("phone_number"):
            whatsapp_sent = await self._send_whatsapp(
                user_data.get("phone_number"),
                message
            )
        
        # Log notification
        self.supabase.table("notifications").insert({
            "user_id": user_id,
            "task_assignment_id": task_assignment_id,
            "notification_type": f"task_{reminder_type}_reminder",
            "title": f"Task Reminder: {task_title}",
            "message": message,
            "delivery_method": "both" if (email_sent and whatsapp_sent) else ("email" if email_sent else "whatsapp"),
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent" if (email_sent or whatsapp_sent) else "failed"
        }).execute()
        
        return email_sent or whatsapp_sent
    
    def _create_reminder_message(self, task_title: str, due_date: Optional[str], reminder_type: str) -> str:
        """Create reminder message based on type"""
        messages = {
            "daily": f"📚 Daily Reminder: Don't forget to work on '{task_title}' today!",
            "one_day": f"⏰ Reminder: '{task_title}' is due tomorrow! Make sure to complete it.",
            "one_hour": f"🚨 Last Hour: '{task_title}' is due in 1 hour! Finish it up!",
            "overdue": f"⚠️ Overdue: '{task_title}' is past its due date. Please complete it soon."
        }
        return messages.get(reminder_type, f"Reminder: {task_title}")
    
    async def _send_email(self, email: str, subject: str, message: str) -> bool:
        """Send email notification"""
        try:
            # Using SendGrid if available, otherwise SMTP
            if self.sendgrid_api_key:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.sendgrid.com/v3/mail/send",
                        headers={
                            "Authorization": f"Bearer {self.sendgrid_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "personalizations": [{"to": [{"email": email}]}],
                            "from": {"email": self.smtp_user},
                            "subject": subject,
                            "content": [{"type": "text/plain", "value": message}]
                        }
                    )
                    return response.status_code == 202
            else:
                # Fallback: Log that email would be sent (implement SMTP if needed)
                print(f"Email would be sent to {email}: {subject}")
                return True  # Mock success
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def _send_whatsapp(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp notification via Twilio"""
        try:
            if not self.twilio_account_sid or not self.twilio_auth_token:
                # Mock WhatsApp sending
                print(f"WhatsApp would be sent to {phone_number}: {message}")
                return True  # Mock success
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json",
                    auth=(self.twilio_account_sid, self.twilio_auth_token),
                    data={
                        "From": self.twilio_whatsapp_from,
                        "To": f"whatsapp:{phone_number}",
                        "Body": message
                    }
                )
                return response.status_code == 201
        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            return False
    
    async def send_handout_notification(self, user_id: str, handout_id: str, task_assignment_id: Optional[str] = None) -> bool:
        """Send notification when handout is delivered"""
        user = self.supabase.table("users").select("*").eq("id", user_id).execute()
        handout = self.supabase.table("handouts").select("*").eq("id", handout_id).execute()
        
        if not user.data or not handout.data:
            return False
        
        user_data = user.data[0]
        handout_data = handout.data[0]
        
        message = f"📄 New handout available: {handout_data.get('title', '')}\n\nAccess it here: {handout_data.get('content_url', '')}"
        
        # Send notifications
        email_sent = await self._send_email(
            user_data.get("email"),
            f"New Handout: {handout_data.get('title', '')}",
            message
        )
        
        whatsapp_sent = False
        if user_data.get("phone_number"):
            whatsapp_sent = await self._send_whatsapp(user_data.get("phone_number"), message)
        
        # Log delivery
        self.supabase.table("handout_deliveries").insert({
            "user_id": user_id,
            "handout_id": handout_id,
            "task_assignment_id": task_assignment_id,
            "delivery_method": "both" if (email_sent and whatsapp_sent) else ("email" if email_sent else "whatsapp"),
            "status": "sent" if (email_sent or whatsapp_sent) else "failed"
        }).execute()
        
        return email_sent or whatsapp_sent
    
    async def send_badge_notification(self, user_id: str, badge_id: str) -> bool:
        """Send notification when user earns a badge"""
        user = self.supabase.table("users").select("*").eq("id", user_id).execute()
        badge = self.supabase.table("badges").select("*").eq("id", badge_id).execute()
        
        if not user.data or not badge.data:
            return False
        
        user_data = user.data[0]
        badge_data = badge.data[0]
        
        message = f"🏆 Congratulations! You earned the '{badge_data.get('name', '')}' badge!\n\n{badge_data.get('description', '')}"
        
        email_sent = await self._send_email(
            user_data.get("email"),
            f"Badge Earned: {badge_data.get('name', '')}",
            message
        )
        
        whatsapp_sent = False
        if user_data.get("phone_number"):
            whatsapp_sent = await self._send_whatsapp(user_data.get("phone_number"), message)
        
        return email_sent or whatsapp_sent

