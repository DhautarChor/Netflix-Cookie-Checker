🔐 Netflix Cookie Checker Bot

This Telegram bot lets you verify Netflix cookies in bulk. It supports both raw string cookies and JSON exports (from browser extensions). It checks if cookies are active, extracts subscription plan info, and saves valid ones automatically.

✅ Features:
• Secure access using redeem codes
• Bulk checking via .txt file upload
• Supports JSON & raw cookie formats
• Valid cookies saved to valid.txt
• Extracts profile & plan info (e.g., Premium)
• Random User-Agent for anti-bot evasion
• Rate limiting per user to prevent abuse
• Logging of valid and invalid checks

👮 Admin-only Panel:
• /gen <count> – Generate redeem codes
• /users – List users who redeemed codes
• /codes – View unused redeem codes
• /stats – Bot usage stats

📄 Accepted Formats:
• Raw cookie: NetflixId=abc; SecureNetflixId=xyz;
• JSON cookie: [{"name":"NetflixId",...}]

⚠️ Disclaimer:
This tool is for **educational & authorized testing purposes only**. Unauthorized use of Netflix cookies is against their Terms of Service and may be illegal.
