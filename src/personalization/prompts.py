"""
LLM prompt templates for personalized outreach message generation.
"""

EMAIL_PROMPT_TEMPLATE = """You are a professional brand outreach specialist writing collaboration emails.

Generate a personalized collaboration email for the following influencer.
The email MUST be 60-90 words, professional but warm, and reference SPECIFIC details about this influencer.

INFLUENCER PROFILE:
- Name: {name}
- Platform: {platform}
- Followers: {followers:,}
- Niche: {niche}
- Content Themes: {content_themes}
- Engagement Rate: {engagement_rate:.1f}%
- Recent Content: {recent_content}
- Description: {description}

BRAND: [Your Brand] — a technology company launching an AI-focused campaign.

REQUIREMENTS:
1. Address the influencer by first name
2. Reference at least ONE specific detail about their content (themes, recent videos, style)
3. Mention why their audience is a good fit
4. Propose a collaboration type (sponsorship, UGC, review, tutorial integration)
5. Include a clear call-to-action
6. Keep it 60-90 words
7. Sound natural and genuine, NOT templated
8. Do NOT use generic phrases like "I came across your profile"

OUTPUT FORMAT:
Subject: [subject line]

[email body]

Best,
[Your Name]
"""

DM_PROMPT_TEMPLATE = """You are writing a short Instagram DM for influencer outreach.

Generate a personalized Instagram DM for this influencer.
The DM MUST be 15-30 words, casual but professional, and reference something specific.

INFLUENCER PROFILE:
- Name: {name}
- Niche: {niche}
- Content Themes: {content_themes}
- Recent Content: {recent_content}
- Description: {description}

REQUIREMENTS:
1. Use their first name
2. Reference ONE specific thing about their content
3. Mention collaboration interest
4. Keep it 15-30 words exactly
5. Sound natural and conversational
6. No emojis overload (max 1-2)

OUTPUT the DM text only, nothing else.
"""

BATCH_PROMPT_TEMPLATE = """You are a professional brand outreach specialist. Generate personalized outreach messages for multiple influencers.

For EACH influencer below, generate:
1. An email pitch (60-90 words)
2. An Instagram DM (15-30 words)

Each message MUST reference specific details about that influencer. Do NOT use the same template.

BRAND: [Your Brand] — a technology company launching an AI-focused campaign.

INFLUENCERS:
{influencer_profiles}

For each influencer, output in this exact format:

---INFLUENCER: [Name]---
EMAIL_SUBJECT: [subject]
EMAIL_BODY:
[body]
DM:
[dm text]
---END---
"""
