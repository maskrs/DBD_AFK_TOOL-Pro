"""
State Manager Module - Handles application state
"""
from threading import Lock
from typing import Any, Dict

class StateManager:
    """Thread-safe state manager"""
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._state = {
                'begin_state': False,  # 开始状态
                'index': 0,  # 列表的下标
                'game_stage': "",  # 游戏阶段
                'pause': False,  # 监听暂停标志
                'stop_thread': False,  # 检查tip标志
                'stop_space': False,  # 自动空格标志
                'stop_action': False,  # 执行动作标志
            }
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        with self._lock:
            return self._state.get(key, default)
    
    def set_state(self, key: str, value: Any):
        """Set state value"""
        with self._lock:
            self._state[key] = value
    
    def update_states(self, states: Dict[str, Any]):
        """Update multiple states at once"""
        with self._lock:
            self._state.update(states)
    
    def reset_states(self):
        """Reset all states to default values"""
        with self._lock:
            self._state.update({
                'begin_state': False,
                'index': 0,
                'game_stage': "",
                'pause': False,
                'stop_thread': False,
                'stop_space': False,
                'stop_action': False,
            })

# Global instance
state_manager = StateManager()
