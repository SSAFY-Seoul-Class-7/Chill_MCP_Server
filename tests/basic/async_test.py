#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChillMCP 비동기 실행 테스트
백그라운드 스트레스 증가 및 상태 관리 시스템 검증
"""

import subprocess
import json
import sys
import os
import time
import threading
import asyncio
from typing import Optional

def get_root_dir():
    """프로젝트 루트 디렉토리"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_python():
    root = get_root_dir()
    venv = os.path.join(root, "venv", "Scripts", "python.exe")
    return venv if os.path.exists(venv) else sys.executable

class AsyncTester:
    def __init__(self):
        self.server = None
        self.req_id = 1
        self.responses = []
        self.server_running = False
        
    def start(self):
        print("\n" + "="*60)
        print("ChillMCP 비동기 실행 테스트")
        print("="*60 + "\n")
        
        root = get_root_dir()
        python_path = get_python()
        main_path = os.path.join(root, "main.py")
        
        print(f"[Python] {python_path}")
        print(f"[Server] {main_path}\n")
        
        print("[1] 서버 시작...")
        self.server = subprocess.Popen(
            [python_path, main_path, "--boss_alertness", "50", "--boss_alertness_cooldown", "10"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            cwd=root
        )
        
        # 서버 에러 모니터링 시작
        threading.Thread(target=self.monitor_stderr, daemon=True).start()
        
        # 백그라운드로 응답 읽기
        threading.Thread(target=self.read_responses, daemon=True).start()
        
        time.sleep(3)
        
        # 서버 시작 체크
        if self.server.poll() is not None:
            print("\n[에러] 서버 시작 실패! stderr를 확인하세요")
            sys.exit(1)
        
        print("[2] 초기화...\n")
        
        # 자동 초기화 (MCP 프로토콜 형식)
        self.send({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "async-test",
                    "version": "1.0.0"
                }
            },
            "id": self.req_id
        })
        self.req_id += 1
        time.sleep(1)
        
        # initialized 알림
        self.send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })
        time.sleep(0.5)
        
        self.server_running = True
        self.run_async_tests()
    
    def send(self, req):
        """요청 전송"""
        try:
            self.server.stdin.write(json.dumps(req) + '\n')
            self.server.stdin.flush()
        except Exception as e:
            print(f"\n[에러] 요청 전송 실패: {e}")
            print("서버가 종료되었을 수 있습니다")
            sys.exit(1)
    
    def monitor_stderr(self):
        """서버 에러 모니터링 (백그라운드)"""
        while True:
            try:
                line = self.server.stderr.readline()
                if not line:
                    break
                if "Traceback" in line or "Error" in line:
                    print(f"\n[서버 에러] {line.strip()}")
            except:
                break
    
    def read_responses(self):
        """응답 읽기 (백그라운드)"""
        while True:
            try:
                line = self.server.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                
                # JSON 응답만 파싱
                if line.startswith('{'):
                    try:
                        res = json.loads(line)
                        self.responses.append(res)
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                print(f"\n[read_responses 에러] {e}")
                break
    
    def run_async_tests(self):
        """비동기 실행 테스트 실행"""
        print("="*60)
        print("비동기 실행 테스트 시작")
        print("="*60)
        
        # 테스트 1: 초기 상태 확인
        print("\n[테스트 1] 초기 상태 확인")
        self.test_initial_state()
        
        # 테스트 2: 백그라운드 스트레스 증가 확인
        print("\n[테스트 2] 백그라운드 스트레스 증가 확인")
        self.test_background_stress_increase()
        
        # 테스트 3: 도구 사용 후 스트레스 감소 확인
        print("\n[테스트 3] 도구 사용 후 스트레스 감소 확인")
        self.test_tool_stress_reduction()
        
        # 테스트 4: 연속 도구 사용 시 스트레스 변화 확인
        print("\n[테스트 4] 연속 도구 사용 시 스트레스 변화 확인")
        self.test_consecutive_tool_usage()
        
        # 테스트 5: 보스 경계도 변화 확인
        print("\n[테스트 5] 보스 경계도 변화 확인")
        self.test_boss_alert_changes()
        
        print("\n" + "="*60)
        print("비동기 실행 테스트 완료")
        print("="*60)
        
        # 서버 종료
        self.server.terminate()
    
    def test_initial_state(self):
        """초기 상태 확인"""
        print("  - 초기 스트레스 레벨 확인...")
        
        # take_a_break 도구 호출하여 초기 상태 확인
        self.send({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "take_a_break", "arguments": {}},
            "id": self.req_id
        })
        self.req_id += 1
        
        time.sleep(2)
        
        # 응답에서 스트레스 레벨 추출
        help_response = self.get_latest_response()
        if help_response and "result" in help_response:
            content = help_response["result"].get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                stress_level = self.extract_stress_level(text)
                print(f"  ✅ 초기 스트레스 레벨: {stress_level}")
                
                if stress_level == 50:
                    print("  ✅ 초기 스트레스 레벨이 정상입니다 (50)")
                else:
                    print(f"  ⚠️  초기 스트레스 레벨이 예상과 다릅니다: {stress_level}")
            else:
                print("  ❌ 응답에서 스트레스 레벨을 추출할 수 없습니다")
        else:
            print("  ❌ help 응답을 받지 못했습니다")
    
    def test_background_stress_increase(self):
        """백그라운드 스트레스 증가 확인"""
        print("  - 10초 대기하며 스트레스 증가 확인...")
        
        # 초기 스트레스 레벨 확인
        initial_stress = self.get_current_stress_level()
        print(f"  - 초기 스트레스: {initial_stress}")
        
        # 10초 대기 (스트레스가 3-4 증가해야 함)
        for i in range(10):
            time.sleep(1)
            current_stress = self.get_current_stress_level()
            if current_stress != initial_stress:
                print(f"  - {i+1}초 후 스트레스: {current_stress} (증가: +{current_stress - initial_stress})")
                break
        
        final_stress = self.get_current_stress_level()
        
        if initial_stress is None or final_stress is None:
            print(f"  ❌ 스트레스 레벨을 읽을 수 없습니다 (초기: {initial_stress}, 최종: {final_stress})")
            return
        
        stress_increase = final_stress - initial_stress
        
        if stress_increase > 0:
            print(f"  ✅ 백그라운드 스트레스 증가 확인: +{stress_increase}")
        else:
            print(f"  ❌ 백그라운드 스트레스 증가 실패: +{stress_increase}")
    
    def test_tool_stress_reduction(self):
        """도구 사용 후 스트레스 감소 확인"""
        print("  - 도구 사용 전 스트레스 확인...")
        before_stress = self.get_current_stress_level()
        print(f"  - 도구 사용 전 스트레스: {before_stress}")
        
        # coffee 도구 사용
        print("  - coffee 도구 사용...")
        self.send({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "coffee_mission", "arguments": {}},
            "id": self.req_id
        })
        self.req_id += 1
        
        time.sleep(2)
        
        after_stress = self.get_current_stress_level()
        
        if before_stress is None or after_stress is None:
            print(f"  ❌ 스트레스 레벨을 읽을 수 없습니다 (사전: {before_stress}, 사후: {after_stress})")
            return
        
        stress_reduction = before_stress - after_stress
        
        print(f"  - 도구 사용 후 스트레스: {after_stress}")
        
        if stress_reduction > 0:
            print(f"  ✅ 도구 사용으로 스트레스 감소 확인: -{stress_reduction}")
        else:
            print(f"  ❌ 도구 사용으로 스트레스 감소 실패: -{stress_reduction}")
    
    def test_consecutive_tool_usage(self):
        """연속 도구 사용 시 스트레스 변화 확인"""
        print("  - 연속 도구 사용 테스트...")
        
        initial_stress = self.get_current_stress_level()
        print(f"  - 초기 스트레스: {initial_stress}")
        
        # 3개 도구 연속 사용
        tools = ["coffee_mission", "watch_netflix", "show_meme"]
        
        for i, tool in enumerate(tools):
            print(f"  - {i+1}번째 도구 사용: {tool}")
            self.send({
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": tool, "arguments": {}},
                "id": self.req_id
            })
            self.req_id += 1
            time.sleep(1)
        
        time.sleep(2)
        final_stress = self.get_current_stress_level()
        
        if initial_stress is None or final_stress is None:
            print(f"  ❌ 스트레스 레벨을 읽을 수 없습니다 (초기: {initial_stress}, 최종: {final_stress})")
            return
        
        total_reduction = initial_stress - final_stress
        
        print(f"  - 최종 스트레스: {final_stress}")
        print(f"  - 총 스트레스 감소: -{total_reduction}")
        
        if total_reduction > 0:
            print(f"  ✅ 연속 도구 사용으로 스트레스 감소 확인: -{total_reduction}")
        else:
            print(f"  ❌ 연속 도구 사용으로 스트레스 감소 실패: -{total_reduction}")
    
    def test_boss_alert_changes(self):
        """보스 경계도 변화 확인"""
        print("  - 보스 경계도 변화 확인...")
        
        initial_boss_alert = self.get_current_boss_alert_level()
        print(f"  - 초기 보스 경계도: {initial_boss_alert}")
        
        # 도구 사용하여 보스 경계도 증가 시도
        self.send({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "coffee_mission", "arguments": {}},
            "id": self.req_id
        })
        self.req_id += 1
        
        time.sleep(2)
        
        final_boss_alert = self.get_current_boss_alert_level()
        
        if initial_boss_alert is None or final_boss_alert is None:
            print(f"  ❌ 보스 경계도를 읽을 수 없습니다 (초기: {initial_boss_alert}, 최종: {final_boss_alert})")
            return
        
        boss_alert_change = final_boss_alert - initial_boss_alert
        
        print(f"  - 최종 보스 경계도: {final_boss_alert}")
        print(f"  - 보스 경계도 변화: {boss_alert_change:+d}")
        
        if boss_alert_change >= 0:
            print(f"  ✅ 보스 경계도 변화 확인: {boss_alert_change:+d}")
        else:
            print(f"  ❌ 보스 경계도 변화 실패: {boss_alert_change:+d}")
    
    def get_current_stress_level(self):
        """현재 스트레스 레벨 가져오기"""
        self.send({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "take_a_break", "arguments": {}},
            "id": self.req_id
        })
        self.req_id += 1
        
        time.sleep(1)
        
        response = self.get_latest_response()
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                return self.extract_stress_level(text)
        
        return None
    
    def get_current_boss_alert_level(self):
        """현재 보스 경계도 가져오기"""
        self.send({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "take_a_break", "arguments": {}},
            "id": self.req_id
        })
        self.req_id += 1
        
        time.sleep(1)
        
        response = self.get_latest_response()
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                return self.extract_boss_alert_level(text)
        
        return None
    
    def extract_stress_level(self, text):
        """텍스트에서 스트레스 레벨 추출"""
        import re
        # 여러 패턴 시도
        patterns = [
            r"Stress Level:\s*(\d+)",
            r"스트레스 레벨:\s*(\d+)",
            r"Stress Level: (\d+)",
            r"스트레스 레벨: (\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        # 디버깅을 위해 텍스트 출력
        print(f"  [디버그] 스트레스 레벨을 찾을 수 없습니다. 텍스트: {text[:200]}...")
        return None
    
    def extract_boss_alert_level(self, text):
        """텍스트에서 보스 경계도 추출"""
        import re
        pattern = r"Boss Alert Level:\s*(\d+)"
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        return None
    
    def get_latest_response(self):
        """최신 응답 가져오기"""
        if self.responses:
            return self.responses[-1]
        return None

if __name__ == "__main__":
    AsyncTester().start()
