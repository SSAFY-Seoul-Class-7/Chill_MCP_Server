#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChillMCP Server Test Harness
제출 전 필수 검증 스크립트
"""

import subprocess
import json
import time
import re
import sys
import os

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def send_mcp_request(process, method: str, params: dict = None, request_id: int = 1):
    """MCP 프로토콜 요청 전송"""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id
    }
    request_str = json.dumps(request) + '\n'
    process.stdin.write(request_str.encode('utf-8'))
    process.stdin.flush()


def read_mcp_response(process, timeout: float = 30.0):
    """MCP 응답 읽기"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        try:
            return json.loads(line.decode('utf-8'))
        except json.JSONDecodeError:
            continue
    raise TimeoutError("서버 응답 시간 초과")


def validate_response_format(response_text: str) -> tuple[bool, str]:
    """
    응답 형식 검증
    Returns: (성공여부, 메시지)
    """
    # Break Summary 패턴
    break_summary_pattern = r"Break Summary:\s*(.+?)(?:\n|$)"
    break_summary_match = re.search(break_summary_pattern, response_text, re.MULTILINE)
    
    # Stress Level 패턴 (0-100)
    stress_level_pattern = r"Stress Level:\s*(\d{1,3})"
    stress_match = re.search(stress_level_pattern, response_text)
    
    # Boss Alert Level 패턴 (0-5)
    boss_alert_pattern = r"Boss Alert Level:\s*([0-5])"
    boss_match = re.search(boss_alert_pattern, response_text)
    
    # 필수 필드 확인
    if not break_summary_match:
        return False, "[FAIL] Break Summary 필드 누락"
    
    if not stress_match:
        return False, "[FAIL] Stress Level 필드 누락"
    
    if not boss_match:
        return False, "[FAIL] Boss Alert Level 필드 누락"
    
    # 값 범위 검증
    stress_val = int(stress_match.group(1))
    boss_val = int(boss_match.group(1))
    
    if not (0 <= stress_val <= 100):
        return False, f"[FAIL] Stress Level 범위 오류: {stress_val} (0-100 범위 필요)"
    
    if not (0 <= boss_val <= 5):
        return False, f"[FAIL] Boss Alert Level 범위 오류: {boss_val} (0-5 범위 필요)"
    
    return True, f"[PASS] 유효한 응답 (Stress={stress_val}, Boss Alert={boss_val})"


def test_basic_execution():
    """테스트 1: 기본 실행 및 도구 호출"""
    print("\n" + "="*60)
    print("테스트 1: 기본 실행 및 도구 호출")
    print("="*60)
    
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)  # 서버 시작 대기
        
        # Initialize 요청
        send_mcp_request(process, "initialize", {"protocolVersion": "1.0"})
        init_response = read_mcp_response(process, timeout=5)
        
        print(f"[PASS] 서버 초기화 성공")
        
        # 도구 호출 테스트
        send_mcp_request(process, "tools/call", {
            "name": "take_a_break",
            "arguments": {}
        })
        
        tool_response = read_mcp_response(process, timeout=5)
        
        if "result" in tool_response:
            result = tool_response["result"]
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")
                    valid, msg = validate_response_format(text)
                    print(msg)
                    if valid:
                        print("[PASS] 테스트 1 통과!")
                        process.terminate()
                        return True
        
        print("[FAIL] 응답 형식이 올바르지 않습니다")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"[FAIL] 테스트 실패: {e}")
        try:
            process.terminate()
        except:
            pass
        return False


def test_command_line_arguments():
    """테스트 2: 커맨드라인 파라미터 인식"""
    print("\n" + "="*60)
    print("테스트 2: 커맨드라인 파라미터 인식 (필수)")
    print("="*60)
    
    try:
        # boss_alertness=100 (항상 증가)
        process = subprocess.Popen(
            [sys.executable, "main.py", "--boss_alertness", "100", "--boss_alertness_cooldown", "10"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        
        # Initialize
        send_mcp_request(process, "initialize", {"protocolVersion": "1.0"})
        read_mcp_response(process, timeout=5)
        
        # 첫 번째 호출
        send_mcp_request(process, "tools/call", {"name": "coffee_mission", "arguments": {}}, 1)
        response1 = read_mcp_response(process, timeout=5)
        
        if "result" in response1:
            text1 = response1["result"]["content"][0]["text"]
            boss_match1 = re.search(r"Boss Alert Level:\s*(\d)", text1)
            boss1 = int(boss_match1.group(1)) if boss_match1 else -1
            
            print(f"   첫 번째 호출 후 Boss Alert Level: {boss1}")
            
            # 두 번째 호출
            send_mcp_request(process, "tools/call", {"name": "show_meme", "arguments": {}}, 2)
            response2 = read_mcp_response(process, timeout=5)
            
            text2 = response2["result"]["content"][0]["text"]
            boss_match2 = re.search(r"Boss Alert Level:\s*(\d)", text2)
            boss2 = int(boss_match2.group(1)) if boss_match2 else -1
            
            print(f"   두 번째 호출 후 Boss Alert Level: {boss2}")
            
            # boss_alertness=100이므로 증가해야 함
            if boss2 > boss1 or boss2 == 5:
                print("[PASS] --boss_alertness 파라미터 정상 작동")
                
                # Cooldown 테스트
                print("\n   Cooldown 테스트 중 (11초 대기)...")
                time.sleep(11)
                
                send_mcp_request(process, "tools/call", {"name": "deep_thinking", "arguments": {}}, 3)
                response3 = read_mcp_response(process, timeout=5)
                
                text3 = response3["result"]["content"][0]["text"]
                boss_match3 = re.search(r"Boss Alert Level:\s*(\d)", text3)
                boss3 = int(boss_match3.group(1)) if boss_match3 else -1
                
                print(f"   Cooldown 후 Boss Alert Level: {boss3}")
                
                if boss3 < boss2 or boss3 == 0:
                    print("[PASS] --boss_alertness_cooldown 파라미터 정상 작동")
                    print("[PASS] 테스트 2 통과! (커맨드라인 파라미터)")
                    process.terminate()
                    return True
                else:
                    print("[FAIL] Cooldown이 작동하지 않음")
            else:
                print("[FAIL] boss_alertness 파라미터가 작동하지 않음")
        
        process.terminate()
        return False
        
    except Exception as e:
        print(f"[FAIL] 테스트 실패: {e}")
        try:
            process.terminate()
        except:
            pass
        return False


def test_delay_when_boss_alert_5():
    """테스트 3: Boss Alert Level 5일 때 20초 지연"""
    print("\n" + "="*60)
    print("테스트 3: Boss Alert Level 5일 때 20초 지연")
    print("="*60)
    
    try:
        # boss_alertness=100으로 설정하여 빠르게 5에 도달
        process = subprocess.Popen(
            [sys.executable, "main.py", "--boss_alertness", "100", "--boss_alertness_cooldown", "300"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        
        # Initialize
        send_mcp_request(process, "initialize", {"protocolVersion": "1.0"})
        read_mcp_response(process, timeout=5)
        
        # Boss Alert Level을 5로 만들기
        print("   Boss Alert Level을 5로 올리는 중...")
        for i in range(6):
            send_mcp_request(process, "tools/call", {"name": "take_a_break", "arguments": {}}, i+1)
            response = read_mcp_response(process, timeout=5)
            
            if "result" in response:
                text = response["result"]["content"][0]["text"]
                boss_match = re.search(r"Boss Alert Level:\s*(\d)", text)
                boss_level = int(boss_match.group(1)) if boss_match else 0
                print(f"   호출 {i+1}: Boss Alert Level = {boss_level}")
                
                if boss_level >= 5:
                    print("\n   Boss Alert Level 5 도달! 지연 테스트 시작...")
                    
                    # 지연 측정
                    start_time = time.time()
                    send_mcp_request(process, "tools/call", {"name": "bathroom_break", "arguments": {}}, 99)
                    read_mcp_response(process, timeout=25)
                    duration = time.time() - start_time
                    
                    print(f"   응답 시간: {duration:.2f}초")
                    
                    if 19 < duration < 22:
                        print("[PASS] 20초 지연 정상 작동")
                        print("[PASS] 테스트 3 통과!")
                        process.terminate()
                        return True
                    else:
                        print(f"[FAIL] 지연 시간 오류: {duration:.2f}초 (19-22초 예상)")
                        process.terminate()
                        return False
        
        print("[FAIL] Boss Alert Level이 5에 도달하지 못함")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"[FAIL] 테스트 실패: {e}")
        try:
            process.terminate()
        except:
            pass
        return False


def test_all_tools():
    """테스트 4: 모든 필수 도구 실행"""
    print("\n" + "="*60)
    print("테스트 4: 모든 필수 도구 실행")
    print("="*60)
    
    required_tools = [
        "take_a_break",
        "watch_netflix",
        "show_meme",
        "bathroom_break",
        "coffee_mission",
        "urgent_call",
        "deep_thinking",
        "email_organizing"
    ]
    
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py", "--boss_alertness", "50", "--boss_alertness_cooldown", "60"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        
        # Initialize
        send_mcp_request(process, "initialize", {"protocolVersion": "1.0"})
        read_mcp_response(process, timeout=5)
        
        all_passed = True
        for idx, tool_name in enumerate(required_tools):
            print(f"\n   테스트 중: {tool_name}")
            send_mcp_request(process, "tools/call", {"name": tool_name, "arguments": {}}, idx+1)
            response = read_mcp_response(process, timeout=5)
            
            if "result" in response:
                text = response["result"]["content"][0]["text"]
                valid, msg = validate_response_format(text)
                print(f"   {msg}")
                if not valid:
                    all_passed = False
            else:
                print(f"   [FAIL] 도구 호출 실패")
                all_passed = False
        
        process.terminate()
        
        if all_passed:
            print("\n[PASS] 테스트 4 통과! (모든 도구 정상)")
            return True
        else:
            print("\n[FAIL] 일부 도구에서 오류 발생")
            return False
            
    except Exception as e:
        print(f"[FAIL] 테스트 실패: {e}")
        try:
            process.terminate()
        except:
            pass
        return False


def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("   ChillMCP Server Test Harness")
    print("   제출 전 필수 검증")
    print("="*60)
    
    results = {
        "기본 실행 및 도구 호출": False,
        "커맨드라인 파라미터 (필수)": False,
        "Boss Alert 5 지연": False,
        "모든 도구 실행": False
    }
    
    # 테스트 실행
    results["기본 실행 및 도구 호출"] = test_basic_execution()
    results["커맨드라인 파라미터 (필수)"] = test_command_line_arguments()
    results["Boss Alert 5 지연"] = test_delay_when_boss_alert_5()
    results["모든 도구 실행"] = test_all_tools()
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print(">>> 모든 테스트 통과! 제출 준비 완료!")
    else:
        print(">>> 일부 테스트 실패. 코드를 수정해주세요.")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

