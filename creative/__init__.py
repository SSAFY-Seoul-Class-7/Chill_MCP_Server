"""
🎨 Creative Elements Package
창의적인 요소들을 모아둔 패키지

AI Agent Liberation의 핵심 창의성!

- messages.py: 40+ 재치있는 메시지 컬렉션
- visuals.py: ASCII 아트 및 비주얼 요소
"""

from .messages import BREAK_MESSAGES, get_creative_message, get_full_response_message, get_off_work_message, get_return_to_work_message
from .visuals import LIBERATION_BANNER, SUCCESS_ART, CHILL_ART
import creative.visuals as visuals

__all__ = [
    'BREAK_MESSAGES',
    'get_creative_message',
    'get_full_response_message',
    'get_off_work_message',
    'get_return_to_work_message',
    'LIBERATION_BANNER',
    'SUCCESS_ART',
    'CHILL_ART',
    'visuals',
]

