#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChillMCP 간단 대화형 테스트
"""

import subprocess
import json
import sys
import os
import time
import threading

def get_root_dir():
    """프로젝트 루트 디렉토리"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_python():
    root = get_root_dir()
    venv = os.path.join(root, "venv", "Scripts", "python.exe")
    return venv if os.path.exists(venv) else sys.executable

class SimpleTester:
    def __init__(self):
        self.server = None
        self.req_id = 1
        
    def start(self):
        print("\n" + "="*60)
        print("ChillMCP 대화형 테스트")
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
            encoding='utf-8',  # Windows cp949 문제 해결
            errors='replace',  # 디코딩 에러 시 '?' 로 대체
            bufsize=1,
            cwd=root  # 프로젝트 루트에서 실행
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
        # 1단계: initialize 요청
        self.send({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "chat-test",
                    "version": "1.0.0"
                }
            },
            "id": self.req_id
        })
        self.req_id += 1
        time.sleep(1)
        
        # 2단계: initialized 알림 (id 없음 - notification)
        self.send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })
        time.sleep(0.5)
        
        # 사용 가능한 명령어 안내
        print("\n" + "="*60)
        print("사용 가능한 명령어:")
        print("="*60)
        print("\n도구 호출:")
        print("  help          - 서버 소개 및 상세 도움말")
        print("  list          - 전체 도구 목록 조회")
        print("\n🎮 휴식 도구:")
        print("  coffee        - ☕ 커피 타러 가기")
        print("  netflix       - 📺 넷플릭스 보기")
        print("  meme          - 😂 밈 감상하기")
        print("  bathroom      - 🚽 화장실 가기")
        print("  call          - 📞 급한 전화 받기")
        print("  think         - 🤔 심오한 사색")
        print("  email         - 📧 이메일 정리")
        print("  break         - ⏸️  기본 휴식")
        print("  ascii         - 🎨 아스키 아트 감상")
        print("  memo          - 📝 비밀 메모장 작성")
        print("\n⚙️  기타:")
        print("  quit / exit   - 종료")
        print("="*60 + "\n")
        
        self.loop()
    
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
                
                # JSON 응답만 파싱 (배너는 자동으로 무시됨)
                if line.startswith('{'):
                    try:
                        res = json.loads(line)
                        self.show(res)
                    except json.JSONDecodeError:
                        pass  # JSON이 아니면 무시
            except Exception as e:
                print(f"\n[read_responses 에러] {e}")
                break
    
    def show(self, res):
        """응답 표시"""
        print("\n" + "-"*60)
        
        if "result" in res:
            r = res["result"]
            
            # 도구 목록
            if "tools" in r:
                print(f"[도구 목록] {len(r['tools'])}개")
                for i, t in enumerate(r['tools'], 1):
                    print(f"  {i}. {t['name']}")
            
            # 도구 호출 결과
            elif "content" in r:
                if isinstance(r["content"], list) and r["content"]:
                    print(r["content"][0].get("text", ""))
            
            # 기타
            else:
                print(json.dumps(r, indent=2, ensure_ascii=False))
        
        elif "error" in res:
            print(f"[에러] {res['error']}")
        
        print("-"*60)
    
    def loop(self):
        """명령어 루프"""
        tools = {
            "coffee": "coffee_mission",
            "netflix": "watch_netflix",
            "meme": "show_meme",
            "bathroom": "bathroom_break",
            "call": "urgent_call",
            "think": "deep_thinking",
            "email": "email_organizing",
            "break": "take_a_break",
            "ascii": "show_ascii_art",  # 아스키 아트 도구 추가
            "memo": "memo_to_boss",  # 메모장 도구 추가
            "help": "show_help",  # 서버의 help 도구 호출
        }
        
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                
                if not cmd:
                    continue
                
                if cmd in ["quit", "exit", "q"]:
                    print("\n[종료]")
                    self.server.terminate()
                    break
                
                elif cmd == "list":
                    self.send({"jsonrpc":"2.0","method":"tools/list","params":{},"id":self.req_id})
                    self.req_id += 1
                
                elif cmd in tools:
                    self.send({
                        "jsonrpc":"2.0",
                        "method":"tools/call",
                        "params":{"name":tools[cmd],"arguments":{}},
                        "id":self.req_id
                    })
                    self.req_id += 1
                
                else:
                    print(f"[알 수 없는 명령어: {cmd}]")
                    print("💡 'help'를 입력하면 사용 가능한 명령어를 볼 수 있습니다")
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n\n[Ctrl+C 종료]")
                self.server.terminate()
                break

if __name__ == "__main__":
    SimpleTester().start()

