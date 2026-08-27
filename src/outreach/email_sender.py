"""
Email sending module with SMTP support.
Supports real sending via Gmail SMTP and simulated sending for demo.
Includes duplicate prevention and rate limiting.
"""

import smtplib
import logging
import time
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from src.config import SMTP_EMAIL, SMTP_PASSWORD, SMTP_HOST, SMTP_PORT
from src.database.models import (
    check_duplicate_outreach,
    insert_outreach_log,
    update_outreach_log,
    update_influencer,
)

logger = logging.getLogger(__name__)


class EmailSender:
    """
    Send outreach emails via SMTP or simulate sending for demo.
    Includes: duplicate prevention, rate limiting, error handling, logging.
    """

    def __init__(self, simulate: bool = True):
        """
        Args:
            simulate: If True, simulates sending without actually sending emails.
                     Set to False and configure SMTP credentials for real sending.
        """
        self.simulate = simulate
        self.sent_count = 0
        self.failed_count = 0

        if not simulate:
            if not SMTP_EMAIL or not SMTP_PASSWORD:
                logger.warning("SMTP credentials not configured. Falling back to simulation mode.")
                self.simulate = True

    def send_email(self, influencer: dict) -> dict:
        """
        Send or simulate sending an email to an influencer.

        Returns dict with:
            - success: bool
            - status: SENT / FAILED / DUPLICATE / SKIPPED
            - message: status description
        """
        influencer_id = influencer.get("id")
        email = influencer.get("email", "")
        name = influencer.get("name", "Unknown")
        email_message = influencer.get("email_message", "")

        # --- Validation ---
        if not email or email == "Not Found" or "@" not in email:
            logger.info(f"  Skipping {name}: no valid email address")
            return {"success": False, "status": "SKIPPED", "message": "No valid email"}

        if not email_message:
            logger.info(f"  Skipping {name}: no message generated")
            return {"success": False, "status": "SKIPPED", "message": "No message generated"}

        # --- Duplicate Prevention ---
        if influencer_id and check_duplicate_outreach(influencer_id, "email"):
            logger.info(f"  Skipping {name}: duplicate outreach")
            return {"success": False, "status": "DUPLICATE", "message": "Already contacted"}

        # --- Parse subject and body ---
        subject, body = self._parse_email_message(email_message, name)

        # --- Send or Simulate ---
        if self.simulate:
            result = self._simulate_send(name, email, subject, body)
        else:
            result = self._real_send(email, subject, body, name)

        # --- Log to database ---
        if influencer_id:
            log_id = insert_outreach_log(
                influencer_id=influencer_id,
                channel="email",
                message=email_message[:500],
                status=result["status"],
            )

            if result["status"] == "SENT":
                update_outreach_log(log_id, "SENT")
                update_influencer(influencer_id, {
                    "outreach_status": "SENT",
                    "sent_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                })
            elif result["status"] == "FAILED":
                update_outreach_log(log_id, "FAILED", result.get("message", ""))

        return result

    def send_batch(self, influencers: list[dict]) -> dict:
        """Send emails to a batch of influencers."""
        logger.info(f"{'Simulating' if self.simulate else 'Sending'} emails to {len(influencers)} influencers...")

        results = {"sent": 0, "failed": 0, "skipped": 0, "duplicate": 0, "details": []}

        for i, inf in enumerate(influencers):
            logger.info(f"  [{i+1}/{len(influencers)}] Processing {inf.get('name', 'Unknown')}")

            result = self.send_email(inf)
            results["details"].append({
                "name": inf.get("name"),
                "email": inf.get("email"),
                **result,
            })

            status = result["status"]
            if status == "SENT":
                results["sent"] += 1
            elif status == "FAILED":
                results["failed"] += 1
            elif status == "DUPLICATE":
                results["duplicate"] += 1
            else:
                results["skipped"] += 1

            # Rate limiting
            if i < len(influencers) - 1:
                time.sleep(2)

        logger.info(
            f"Email batch complete: "
            f"{results['sent']} sent, {results['failed']} failed, "
            f"{results['skipped']} skipped, {results['duplicate']} duplicate"
        )

        return results

    def _simulate_send(self, name: str, email: str, subject: str, body: str) -> dict:
        """Simulate sending an email."""
        logger.info(f"  [SIMULATED] Email to {name} <{email}>: '{subject}'")
        self.sent_count += 1
        return {
            "success": True,
            "status": "SENT",
            "message": f"[SIMULATED] Email sent to {email}",
        }

    def _real_send(self, to_email: str, subject: str, body: str, name: str) -> dict:
        """Send a real email via SMTP."""
        try:
            msg = MIMEMultipart()
            msg["From"] = SMTP_EMAIL
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)

            self.sent_count += 1
            logger.info(f"  [REAL] Email sent to {name} <{to_email}>")
            return {
                "success": True,
                "status": "SENT",
                "message": f"Email sent to {to_email}",
            }

        except smtplib.SMTPAuthenticationError:
            logger.error(f"  SMTP authentication failed for {to_email}")
            self.failed_count += 1
            return {
                "success": False,
                "status": "FAILED",
                "message": "SMTP authentication failed",
            }
        except Exception as e:
            logger.error(f"  Email send failed for {to_email}: {e}")
            self.failed_count += 1
            return {
                "success": False,
                "status": "FAILED",
                "message": str(e),
            }

    def _parse_email_message(self, email_message: str, name: str) -> tuple[str, str]:
        """Parse a generated email message into subject and body."""
        subject_match = re.search(r'Subject:\s*(.+?)(?:\n|$)', email_message, re.IGNORECASE)
        if subject_match:
            subject = subject_match.group(1).strip()
            body = email_message[subject_match.end():].strip()
        else:
            subject = f"Collaboration Opportunity — {name}"
            body = email_message

        return subject, body
