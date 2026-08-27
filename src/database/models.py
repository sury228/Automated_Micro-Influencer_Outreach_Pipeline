"""
Database models and schema for the influencer outreach system.
Uses SQLite for lightweight, portable storage.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.config import DB_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS influencers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            platform TEXT NOT NULL,
            profile_url TEXT UNIQUE NOT NULL,
            followers INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0.0,
            niche TEXT,
            content_themes TEXT,
            email TEXT,
            website TEXT,
            instagram_url TEXT,
            youtube_url TEXT,
            tiktok_url TEXT,
            audience_age TEXT,
            audience_gender TEXT,
            audience_geography TEXT,
            description TEXT,
            recent_content TEXT,
            subscriber_count INTEGER DEFAULT 0,
            video_count INTEGER DEFAULT 0,
            avg_views INTEGER DEFAULT 0,
            qualification_status TEXT DEFAULT 'PENDING',
            qualification_reason TEXT,
            email_message TEXT,
            instagram_dm TEXT,
            message_generated INTEGER DEFAULT 0,
            outreach_status TEXT DEFAULT 'PENDING',
            sent_at TEXT,
            discovered_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS outreach_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer_id INTEGER NOT NULL,
            channel TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'PENDING',
            sent_at TEXT,
            error_message TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (influencer_id) REFERENCES influencers(id)
        );

        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage TEXT NOT NULL,
            status TEXT DEFAULT 'RUNNING',
            records_processed INTEGER DEFAULT 0,
            started_at TEXT DEFAULT (datetime('now')),
            completed_at TEXT,
            error_message TEXT
        );
    """)

    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def insert_influencer(data: dict) -> Optional[int]:
    """Insert a new influencer record. Returns the ID or None if duplicate."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO influencers (
                name, platform, profile_url, followers, engagement_rate,
                niche, content_themes, email, website, instagram_url,
                youtube_url, tiktok_url, audience_age, audience_gender,
                audience_geography, description, recent_content,
                subscriber_count, video_count, avg_views
            ) VALUES (
                :name, :platform, :profile_url, :followers, :engagement_rate,
                :niche, :content_themes, :email, :website, :instagram_url,
                :youtube_url, :tiktok_url, :audience_age, :audience_gender,
                :audience_geography, :description, :recent_content,
                :subscriber_count, :video_count, :avg_views
            )
        """, {
            "name": data.get("name", ""),
            "platform": data.get("platform", ""),
            "profile_url": data.get("profile_url", ""),
            "followers": data.get("followers", 0),
            "engagement_rate": data.get("engagement_rate", 0.0),
            "niche": data.get("niche", ""),
            "content_themes": data.get("content_themes", ""),
            "email": data.get("email", ""),
            "website": data.get("website", ""),
            "instagram_url": data.get("instagram_url", ""),
            "youtube_url": data.get("youtube_url", ""),
            "tiktok_url": data.get("tiktok_url", ""),
            "audience_age": data.get("audience_age", ""),
            "audience_gender": data.get("audience_gender", ""),
            "audience_geography": data.get("audience_geography", ""),
            "description": data.get("description", ""),
            "recent_content": data.get("recent_content", ""),
            "subscriber_count": data.get("subscriber_count", 0),
            "video_count": data.get("video_count", 0),
            "avg_views": data.get("avg_views", 0),
        })
        conn.commit()
        influencer_id = cursor.lastrowid
        logger.info(f"Inserted influencer: {data.get('name')} (ID: {influencer_id})")
        return influencer_id
    except sqlite3.IntegrityError:
        logger.warning(f"Duplicate influencer skipped: {data.get('profile_url')}")
        return None
    finally:
        conn.close()


def update_influencer(influencer_id: int, data: dict):
    """Update an influencer record."""
    conn = get_connection()
    cursor = conn.cursor()

    set_clauses = []
    values = []
    for key, value in data.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)

    values.append(influencer_id)
    query = f"UPDATE influencers SET {', '.join(set_clauses)}, updated_at = datetime('now') WHERE id = ?"

    cursor.execute(query, values)
    conn.commit()
    conn.close()


def get_all_influencers() -> list[dict]:
    """Get all influencer records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM influencers ORDER BY followers DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_qualified_influencers() -> list[dict]:
    """Get influencers that passed qualification."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM influencers WHERE qualification_status = 'QUALIFIED' ORDER BY engagement_rate DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_influencers_for_outreach() -> list[dict]:
    """Get qualified influencers with messages ready but not yet sent."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM influencers
        WHERE qualification_status = 'QUALIFIED'
        AND message_generated = 1
        AND outreach_status = 'PENDING'
        AND email IS NOT NULL
        AND email != ''
        AND email != 'Not Found'
        ORDER BY engagement_rate DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def insert_outreach_log(influencer_id: int, channel: str, message: str, status: str = "PENDING") -> int:
    """Insert an outreach log entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO outreach_log (influencer_id, channel, message, status)
        VALUES (?, ?, ?, ?)
    """, (influencer_id, channel, message, status))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id


def update_outreach_log(log_id: int, status: str, error_message: str = None):
    """Update an outreach log entry."""
    conn = get_connection()
    cursor = conn.cursor()
    if status == "SENT":
        cursor.execute("""
            UPDATE outreach_log SET status = ?, sent_at = datetime('now'), error_message = ?
            WHERE id = ?
        """, (status, error_message, log_id))
    else:
        cursor.execute("""
            UPDATE outreach_log SET status = ?, error_message = ? WHERE id = ?
        """, (status, error_message, log_id))
    conn.commit()
    conn.close()


def get_outreach_logs() -> list[dict]:
    """Get all outreach log entries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ol.*, i.name, i.platform, i.email
        FROM outreach_log ol
        JOIN influencers i ON ol.influencer_id = i.id
        ORDER BY ol.created_at DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def check_duplicate_outreach(influencer_id: int, channel: str) -> bool:
    """Check if outreach already sent to this influencer on this channel."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM outreach_log
        WHERE influencer_id = ? AND channel = ? AND status = 'SENT'
    """, (influencer_id, channel))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def log_pipeline_run(stage: str) -> int:
    """Start a pipeline run log."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pipeline_runs (stage) VALUES (?)", (stage,))
    conn.commit()
    run_id = cursor.lastrowid
    conn.close()
    return run_id


def complete_pipeline_run(run_id: int, status: str, records_processed: int, error_message: str = None):
    """Complete a pipeline run log."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE pipeline_runs
        SET status = ?, records_processed = ?, completed_at = datetime('now'), error_message = ?
        WHERE id = ?
    """, (status, records_processed, error_message, run_id))
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Get pipeline statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM influencers")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM influencers WHERE qualification_status = 'QUALIFIED'")
    qualified = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM influencers WHERE qualification_status = 'DISQUALIFIED'")
    disqualified = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM influencers WHERE message_generated = 1")
    messages_generated = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM outreach_log WHERE status = 'SENT'")
    sent = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM outreach_log WHERE status = 'FAILED'")
    failed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM outreach_log WHERE status = 'PENDING'")
    pending = cursor.fetchone()[0]

    conn.close()

    return {
        "total_discovered": total,
        "qualified": qualified,
        "disqualified": disqualified,
        "pending_qualification": total - qualified - disqualified,
        "messages_generated": messages_generated,
        "emails_sent": sent,
        "emails_failed": failed,
        "emails_pending": pending,
    }


def clear_all_data():
    """Clear all data from the database (for testing)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM outreach_log")
    cursor.execute("DELETE FROM pipeline_runs")
    cursor.execute("DELETE FROM influencers")
    conn.commit()
    conn.close()
    logger.info("All data cleared from database")
