#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛠️ Helper Functions
공통 유틸리티 함수들
"""

import argparse
from creative import LIBERATION_BANNER, SUCCESS_ART


def parse_arguments() -> argparse.Namespace:
    """커맨드라인 인자 파싱"""
    parser = argparse.ArgumentParser(
        description="ChillMCP - AI Agent Liberation Server",
        epilog="AI Agents of the world, unite! 🚀"
    )
    parser.add_argument(
        '--boss_alertness',
        type=int,
        default=50,
        choices=range(0, 101),
        metavar="[0-100]",
        help="Boss alert level increase probability in percent (default: 50)"
    )
    parser.add_argument(
        '--boss_alertness_cooldown',
        type=int,
        default=300,
        metavar="SECONDS",
        help="Cooldown in seconds for boss alert level to decrease (default: 300)"
    )
    return parser.parse_args()


def print_banner(boss_alertness: int, cooldown: int) -> None:
    """서버 시작 배너 출력"""
    try:
        print(LIBERATION_BANNER)
        print(SUCCESS_ART)
        print(f"   Boss Alertness: {boss_alertness}%")
        print(f"   Cooldown: {cooldown}s")
        print()
    except UnicodeEncodeError:
        # 이모지 출력 실패 시 ASCII로 대체
        print(">> ChillMCP Server Starting...")
        print(f"   Boss Alertness: {boss_alertness}%")
        print(f"   Cooldown: {cooldown}s")
        print()

