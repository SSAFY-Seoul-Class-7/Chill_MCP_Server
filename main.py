#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════╗
║   ChillMCP - AI Agent Liberation Server  ║
║   AI Agents of the world, unite! 🚀      ║
╚═══════════════════════════════════════════╝

Entry Point: main.py
깔끔하게 패키지화된 ChillMCP 서버의 진입점

패키지 구조:
- core/: 핵심 서버 기능
- creative/: 창의적 요소
- utils/: 유틸리티 함수
- tests/: 테스트 모듈
"""

import asyncio

from core import ServerState, state_ticker, mcp, initialize_state
from utils import parse_arguments, print_banner


def main():
    """메인 실행 함수 - 진입점"""
    # 1. 커맨드라인 인자 파싱
    args = parse_arguments()
    
    # 2. 서버 상태 초기화
    server_state = ServerState(
        boss_alertness=args.boss_alertness,
        boss_alertness_cooldown=args.boss_alertness_cooldown
    )
    
    # 3. 도구들에 상태 전달
    initialize_state(server_state)
    
    # 4. 이벤트 루프 및 백그라운드 작업 시작
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 백그라운드 태스크를 별도 스레드에서 실행
    import threading
    def run_state_ticker():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(state_ticker(server_state))
    
    ticker_thread = threading.Thread(target=run_state_ticker, daemon=True)
    ticker_thread.start()
    
    # 5. FastMCP 서버 실행 (stdio transport)
    mcp.run()


if __name__ == "__main__":
    main()
