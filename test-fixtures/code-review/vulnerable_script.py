# -*- coding: utf-8 -*-
"""
有漏洞的 Python 脚本 - 用于集成测试

这个文件故意包含多个安全和质量问题,用于验证 PythonScriptAnalyzer
"""

import subprocess
import pickle

# PY-SEC-004: 硬编码敏感数据
API_KEY = "sk-1234567890abcdefghijklmnop"
password = "admin123"

# PY-QUAL-001: 缺少文档字符串的函数
def execute_command(user_cmd):
    # PY-SEC-001: 命令注入风险
    subprocess.call(user_cmd, shell=True)

# PY-QUAL-004: 参数过多
def complex_function(a, b, c, d, e, f, g, h):
    return a + b + c + d + e + f + g + h

# PY-QUAL-006: 裸 except
try:
    risky_operation()
except:
    pass

# PY-QUAL-010: 调试 print
def process_data(data):
    print("debug: processing", data)
    return data

# PY-SEC-003: SQL 注入
def get_user(username):
    cursor.execute("SELECT * FROM users WHERE name = '" + username + "'")

# PY-SEC-005: 不安全的反序列化
def load_data(data):
    return pickle.loads(data)

# PY-QUAL-002: 函数过长 (>50行)
def very_long_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    line9 = 9
    line10 = 10
    line11 = 11
    line12 = 12
    line13 = 13
    line14 = 14
    line15 = 15
    line16 = 16
    line17 = 17
    line18 = 18
    line19 = 19
    line20 = 20
    line21 = 21
    line22 = 22
    line23 = 23
    line24 = 24
    line25 = 25
    line26 = 26
    line27 = 27
    line28 = 28
    line29 = 29
    line30 = 30
    line31 = 31
    line32 = 32
    line33 = 33
    line34 = 34
    line35 = 35
    line36 = 36
    line37 = 37
    line38 = 38
    line39 = 39
    line40 = 40
    line41 = 41
    line42 = 42
    line43 = 43
    line44 = 44
    line45 = 45
    line46 = 46
    line47 = 47
    line48 = 48
    line49 = 49
    line50 = 50
    line51 = 51
    line52 = 52
    return line52
