"""
文件名：protocol.py
"""
from constants import CHECK

def build_cmd(addr, code, data=None):
    """
    构建通信指令
    格式: [Addr, Code, Data..., Checksum]
    """
    if data is None:
        data = []
    cmd = bytearray()
    cmd.append(addr)
    cmd.append(code)
    cmd.extend(data)
    cmd.append(CHECK)  # 固定校验码 0x6B
    return cmd