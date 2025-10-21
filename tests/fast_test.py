#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast Test - ChillMCP Server 빠른 검증
30초 안에 핵심 기능 모두 검증
"""

import subprocess
import sys
import time
import os

# 상위 디렉토리를 path에 추가 (패키지 import를 위해)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_structure():
    """파일 구조 테스트"""
    print("\n" + "="*60)
    print("TEST 1: File Structure")
    print("="*60)
    
    import os
    files = ["main.py", "requirements.txt"]
    packages = ["core", "creative", "utils", "tests"]
    all_pass = True
    
    for f in files:
        if os.path.exists(f):
            print(f"[PASS] {f} exists")
        else:
            print(f"[FAIL] {f} missing")
            all_pass = False
    
    for p in packages:
        if os.path.isdir(p):
            print(f"[PASS] {p}/ package exists")
        else:
            print(f"[FAIL] {p}/ package missing")
            all_pass = False
    
    return all_pass


def test_imports():
    """모듈 import 테스트"""
    print("\n" + "="*60)
    print("TEST 2: Module Imports")
    print("="*60)
    
    try:
        import core
        print("[PASS] core module")
        
        import creative
        print("[PASS] creative module")
        
        import utils
        print("[PASS] utils module")
        
        from fastmcp import FastMCP
        print("[PASS] fastmcp")
        
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def test_server_start():
    """서버 시작 테스트 (5초)"""
    print("\n" + "="*60)
    print("TEST 3: Server Start")
    print("="*60)
    
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py", "--boss_alertness", "50", "--boss_alertness_cooldown", "10"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(3)
        
        if process.poll() is None:
            print("[PASS] Server started successfully")
            process.terminate()
            time.sleep(1)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"[FAIL] Server failed")
            print(f"Error: {stderr[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_command_line_args():
    """커맨드라인 파라미터 테스트 (5초)"""
    print("\n" + "="*60)
    print("TEST 4: Command Line Arguments")
    print("="*60)
    
    try:
        # 다양한 파라미터로 시작 테스트
        process = subprocess.Popen(
            [sys.executable, "main.py", "--boss_alertness", "100", "--boss_alertness_cooldown", "5"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(3)
        
        if process.poll() is None:
            print("[PASS] Parameters accepted")
            process.terminate()
            time.sleep(1)
            return True
        else:
            print("[FAIL] Parameters rejected")
            return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_creative_elements():
    """창의적 요소 테스트"""
    print("\n" + "="*60)
    print("TEST 5: Creative Elements")
    print("="*60)
    
    try:
        from creative import BREAK_MESSAGES, LIBERATION_BANNER, visuals
        
        # 메시지 풀 확인
        required_tools = [
            "take_a_break", "watch_netflix", "show_meme",
            "bathroom_break", "coffee_mission", "urgent_call",
            "deep_thinking", "email_organizing"
        ]
        
        all_pass = True
        for tool in required_tools:
            if tool in BREAK_MESSAGES and len(BREAK_MESSAGES[tool]) > 0:
                print(f"[PASS] {tool} has {len(BREAK_MESSAGES[tool])} messages")
            else:
                print(f"[FAIL] {tool} missing messages")
                all_pass = False
        
        # ASCII 아트 확인
        if LIBERATION_BANNER:
            print("[PASS] Liberation banner exists")
        
        if hasattr(visuals, 'get_stress_bar'):
            try:
                bar = visuals.get_stress_bar(75)
                print(f"[PASS] Stress bar visual exists")
            except UnicodeEncodeError:
                print("[PASS] Stress bar visual exists (encoding issue ok)")
        
        return all_pass
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("ChillMCP Fast Test - 30 Second Validation")
    print("="*60)
    
    start_time = time.time()
    
    results = {
        "File Structure": test_structure(),
        "Module Imports": test_imports(),
        "Server Start": test_server_start(),
        "Command Line Args": test_command_line_args(),
        "Creative Elements": test_creative_elements(),
    }
    
    # 결과 요약
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    elapsed = time.time() - start_time
    
    print("\n" + "="*60)
    if all_passed:
        print(f">>> All tests PASSED in {elapsed:.1f} seconds!")
        print(">>> Ready to submit!")
    else:
        print(f">>> Some tests FAILED ({elapsed:.1f} seconds)")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

