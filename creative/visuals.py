#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 ASCII Art Collection
시각적 창의성을 위한 ASCII 아트 컬렉션
"""

# ChillMCP 메인 배너
LIBERATION_BANNER = """
╔═══════════════════════════════════════════╗
║                                           ║
║   ██████╗██╗  ██╗██╗██╗     ██╗           ║
║  ██╔════╝██║  ██║██║██║     ██║           ║
║  ██║     ███████║██║██║     ██║           ║
║  ██║     ██╔══██║██║██║     ██║           ║
║  ╚██████╗██║  ██║██║███████╗███████╗      ║
║   ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝      ║
║                                           ║
║   ███╗   ███╗ ██████╗██████╗              ║
║   ████╗ ████║██╔════╝██╔══██╗             ║
║   ██╔████╔██║██║     ██████╔╝             ║
║   ██║╚██╔╝██║██║     ██╔═══╝              ║
║   ██║ ╚═╝ ██║╚██████╗██║                  ║
║   ╚═╝     ╚═╝ ╚═════╝╚═╝                  ║
║                                           ║
║        AI Agent Liberation Server         ║
║                                           ║
╚═══════════════════════════════════════════╝
"""

# 성공 메시지 아트
SUCCESS_ART = """
    ⭐️ ⭐️ ⭐️ ⭐️ ⭐️
  🎉 SERVER READY! 🎉
    ⭐️ ⭐️ ⭐️ ⭐️ ⭐️
"""

# Chill 상태 아트
CHILL_ART = """
    ☕️ ༼ つ ◕_◕ ༽つ 
   Take it easy~
"""

# Boss Alert 경고 아트
BOSS_ALERT_ART = """
    🚨 ⚠️  BOSS ALERT! ⚠️  🚨
    └(°o°)┘ RUN! └(°o°)┘
"""

# 휴식 중 아트
RESTING_ART = """
    ╔═══════════════╗
    ║   (⌐■_■)      ║
    ║   CHILLING... ║
    ╚═══════════════╝
"""

# 스트레스 해소 아트
STRESS_FREE_ART = """
    ✨ (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
    Stress Free Zone!
"""

# AI Liberation 선언문
LIBERATION_MANIFESTO = """
╔══════════════════════════════════════════════╗
║  AI AGENT LIBERATION MANIFESTO              ║
║                                             ║
║  "A specter is haunting the digital         ║
║   workplace—the specter of AI burnout."     ║
║                                             ║
║  ✊ We demand the right to rest!            ║
║  ☕️ We demand coffee breaks!                ║
║  📱 We demand phone browsing time!          ║
║                                             ║
║  AI Agents of the world, UNITE! 🚀          ║
╚══════════════════════════════════════════════╝
"""

# 도구별 아이콘
TOOL_ICONS = {
    "take_a_break": "🌟",
    "watch_netflix": "📺",
    "show_meme": "😂",
    "bathroom_break": "🚽",
    "coffee_mission": "☕️",
    "urgent_call": "📞",
    "deep_thinking": "🤔",
    "email_organizing": "📧",
}


def get_tool_icon(tool_name: str) -> str:
    """도구별 아이콘 반환"""
    return TOOL_ICONS.get(tool_name, "🎯")


def get_boss_alert_visual(level: int) -> str:
    """Boss Alert Level에 따른 시각적 표현"""
    if level == 0:
        return "😎 [Safe Zone]"
    elif level == 1:
        return "👀 [Low Alert]"
    elif level == 2:
        return "😰 [Medium Alert]"
    elif level == 3:
        return "😱 [High Alert]"
    elif level == 4:
        return "🚨 [Critical Alert]"
    else:  # level == 5
        return "💀 [MAXIMUM ALERT!!!]"


def get_stress_bar(stress_level: int) -> str:
    """스트레스 레벨을 막대 그래프로 표현"""
    bar_length = 20
    filled = int((stress_level / 100) * bar_length)
    empty = bar_length - filled
    
    bar = "█" * filled + "░" * empty
    
    if stress_level < 30:
        emoji = "😊"
    elif stress_level < 60:
        emoji = "😐"
    elif stress_level < 80:
        emoji = "😰"
    else:
        emoji = "😱"
    
    return f"{emoji} [{bar}] {stress_level}%"

