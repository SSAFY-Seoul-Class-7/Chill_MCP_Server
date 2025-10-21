#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Server State Management
서버 상태 관리 및 백그라운드 작업
"""

import asyncio
import random
import time


class ServerState:
    """서버의 모든 상태를 관리하는 클래스"""
    
    def __init__(self, boss_alertness: int, boss_alertness_cooldown: int):
        """
        Args:
            boss_alertness: Boss 경계도 상승 확률 (0-100%)
            boss_alertness_cooldown: Boss 경계도 자동 감소 주기 (초)
        """
        self.stress_level: int = 50
        self.boss_alert_level: int = 0
        
        self.boss_alertness_prob: float = boss_alertness / 100.0
        self.boss_alertness_cooldown: int = boss_alertness_cooldown
        
        self.last_stress_increase_time: float = time.time()
        self.last_alert_decrease_time: float = time.time()
        
        # 비동기 환경에서 상태 변경의 원자성을 보장하기 위한 락
        self._lock: asyncio.Lock = asyncio.Lock()

    async def increase_stress_over_time(self) -> None:
        """시간 경과에 따른 스트레스 자동 증가 (1분마다 1포인트)"""
        async with self._lock:
            now = time.time()
            if now - self.last_stress_increase_time >= 60:
                self.stress_level = min(100, self.stress_level + 1)
                self.last_stress_increase_time = now

    async def decrease_stress(self, amount: int) -> None:
        """스트레스 감소"""
        async with self._lock:
            self.stress_level = max(0, self.stress_level - amount)

    async def maybe_increase_boss_alert(self) -> None:
        """확률적으로 Boss 경계도 증가"""
        if random.random() < self.boss_alertness_prob:
            async with self._lock:
                if self.boss_alert_level < 5:
                    self.boss_alert_level += 1
                    # 경계도 상승 시 쿨다운 타이머 리셋
                    self.last_alert_decrease_time = time.time()

    async def decrease_boss_alert_over_time(self) -> None:
        """쿨다운 주기마다 Boss 경계도 자동 감소"""
        async with self._lock:
            now = time.time()
            if self.boss_alert_level > 0 and now - self.last_alert_decrease_time >= self.boss_alertness_cooldown:
                self.boss_alert_level = max(0, self.boss_alert_level - 1)
                self.last_alert_decrease_time = now


async def state_ticker(state: ServerState) -> None:
    """주기적으로 서버 상태를 업데이트하는 백그라운드 작업"""
    while True:
        await state.increase_stress_over_time()
        await state.decrease_boss_alert_over_time()
        await asyncio.sleep(1)  # 1초마다 체크

