#!/usr/bin/env python3
"""
解析JWT Token
"""

import base64
import json

def decode_jwt(token):
    """解析JWT token"""
    try:
        # JWT格式: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ 不是有效的JWT格式")
            return None
        
        # 解析header
        header = parts[0]
        # 添加padding
        header += '=' * (4 - len(header) % 4)
        header_decoded = base64.b64decode(header)
        header_json = json.loads(header_decoded)
        
        # 解析payload
        payload = parts[1]
        # 添加padding
        payload += '=' * (4 - len(payload) % 4)
        payload_decoded = base64.b64decode(payload)
        payload_json = json.loads(payload_decoded)
        
        return {
            "header": header_json,
            "payload": payload_json
        }
    except Exception as e:
        print(f"❌ 解析JWT失败: {e}")
        return None

def main():
    token = "eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiJhY2MiLCJhdWQiOiLnmb7luqbnu5_orqEiLCJ1aWQiOjI0NTk4OTkzLCJhcHBJZCI6IjEzYmQ1MDQ5YTY3NmQxMDczNzk1OTkzMjEwMmVjNTU3IiwiaXNzIjoi5ZWG5Lia5byA5Y-R6ICF5Lit5b-DIiwicGxhdGZvcm1JZCI6IjQ5NjAzNDU5NjU5NTg1NjE3OTQiLCJleHAiOjE3NjA0NDcyNzAsImp0aSI6Ii04Mzk3MzE5MjkzMTc2MjU4NTA0In0.oOkSqxODhCqNUKpTtpwjwVBFyReTkUFXTww7RuklaeIwazIRHHWu9CdDXJR1FtfR"
    
    print("解析JWT Token:")
    print("=" * 50)
    
    result = decode_jwt(token)
    if result:
        print("Header:")
        print(json.dumps(result["header"], indent=2, ensure_ascii=False))
        
        print("\nPayload:")
        print(json.dumps(result["payload"], indent=2, ensure_ascii=False))
        
        # 检查过期时间
        exp = result["payload"].get("exp")
        if exp:
            import datetime
            exp_time = datetime.datetime.fromtimestamp(exp)
            print(f"\nToken过期时间: {exp_time}")
            
            if exp_time < datetime.datetime.now():
                print("❌ Token已过期")
            else:
                print("✅ Token仍然有效")
        
        # 提取有用信息
        print(f"\n用户ID: {result['payload'].get('uid')}")
        print(f"应用ID: {result['payload'].get('appId')}")
        print(f"平台ID: {result['payload'].get('platformId')}")

if __name__ == "__main__":
    main()

