#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Test - ChillMCP Server 기본 기능 검증
"""

import subprocess
import sys
import time

def test_server_start():
    """서버 시작 테스트"""
    print("\n" + "="*60)
    print("TEST 1: Server Start")
    print("="*60)
    
    try:
        # 서버 실행
        process = subprocess.Popen(
            [sys.executable, "main.py", "--boss_alertness", "50", "--boss_alertness_cooldown", "10"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 2초 대기
        time.sleep(2)
        
        # 프로세스가 살아있는지 확인
        if process.poll() is None:
            print("[PASS] Server started successfully")
            process.terminate()
            time.sleep(1)
            return True
        else:
            stdout, stderr = process.communicate()
            print("[FAIL] Server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        try:
            process.terminate()
        except:
            pass
        return False


def test_command_line_args():
    """커맨드라인 파라미터 테스트"""
    print("\n" + "="*60)
    print("TEST 2: Command Line Arguments")
    print("="*60)
    
    try:
        # --boss_alertness와 --boss_alertness_cooldown 파라미터로 실행
        process = subprocess.Popen(
            [sys.executable, "main.py", "--boss_alertness", "100", "--boss_alertness_cooldown", "5"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(2)
        
        if process.poll() is None:
            print("[PASS] Server accepts command line parameters")
            process.terminate()
            time.sleep(1)
            return True
        else:
            stdout, stderr = process.communicate()
            print("[FAIL] Server failed with parameters")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        try:
            process.terminate()
        except:
            pass
        return False


def test_imports():
    """필수 모듈 임포트 테스트"""
    print("\n" + "="*60)
    print("TEST 3: Required Modules")
    print("="*60)
    
    try:
        import fastmcp
        print("[PASS] fastmcp imported")
        
        import asyncio
        print("[PASS] asyncio imported")
        
        import argparse
        print("[PASS] argparse imported")
        
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_file_structure():
    """파일 구조 테스트"""
    print("\n" + "="*60)
    print("TEST 4: File Structure")
    print("="*60)
    
    import os
    
    required_files = ["main.py", "requirements.txt"]
    all_exist = True
    
    for filename in required_files:
        if os.path.exists(filename):
            print(f"[PASS] {filename} exists")
        else:
            print(f"[FAIL] {filename} not found")
            all_exist = False
    
    return all_exist


def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("ChillMCP Server - Simple Test")
    print("="*60)
    
    results = {
        "File Structure": test_file_structure(),
        "Required Modules": test_imports(),
        "Server Start": test_server_start(),
        "Command Line Args": test_command_line_args(),
    }
    
    # 결과 요약
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("All tests PASSED! Ready to submit!")
    else:
        print("Some tests FAILED. Please fix the issues.")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

