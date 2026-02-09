import socketio
import requests
import json
import time
import uuid

# 配置
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1/copywriting/generate"
AUTH_URL = f"{BASE_URL}/api/v1/auth"
# Socket.IO 使用 ASGIApp 包装 FastAPI，默认路径 /socket.io
WS_URL = BASE_URL
WS_PATH = "/socket.io"

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print("✅ Connected to WebSocket")

@sio.on('agent:thought')
def on_thought(data):
    # 验证 Story 2-3 的关键点：node_name 和 content
    node = data.get('data', {}).get('node_name', 'UNKNOWN')
    content = data.get('data', {}).get('content', '')
    print(f"🤔 [{node}] {content[:50]}..." if len(content) > 50 else f"🤔 [{node}] {content}")

@sio.on('agent:result')
def on_result(data):
    print(f"\n🎉 Workflow Completed!")
    final_copy = data.get('finalCopy', data.get('data', {}).get('finalCopy', ''))
    if final_copy:
        print(f"Final Copy Preview: {final_copy[:100]}...")
    sio.disconnect()

@sio.on('agent:error')
def on_error(data):
    print(f"❌ Error: {data}")
    sio.disconnect()

@sio.on('connect_error')
def on_connect_error(data):
    print(f"❌ Connection Error: {data}")


def get_auth_token():
    """获取 JWT 访问令牌（注册新用户或使用测试用户）"""
    # 生成随机测试用户
    test_email = f"test_{uuid.uuid4().hex[:8]}@test.com"
    test_password = "TestPassword123!"
    
    # 尝试注册
    register_data = {
        "email": test_email,
        "password": test_password,
        "username": f"testuser_{uuid.uuid4().hex[:6]}"
    }
    
    print(f"🔐 Registering test user: {test_email}")
    try:
        # 修正：使用 /signup 端点，而不是 /register
        resp = requests.post(f"{AUTH_URL}/signup", json=register_data)
        if resp.status_code == 201 or resp.status_code == 200:
            print("✅ User registered successfully")
        else:
            print(f"⚠️ Registration response: {resp.status_code} - {resp.text[:100]}")
    except Exception as e:
        print(f"⚠️ Registration failed: {e}")
    
    # 登录获取 token
    print("🔑 Logging in...")
    # 修正：后端使用 UserLoginRequest (JSON)，而不是 OAuth2 表单
    login_data = {
        "email": test_email,
        "password": test_password
    }
    try:
        resp = requests.post(
            f"{AUTH_URL}/login",
            json=login_data
        )
        if resp.status_code == 200:
            token = resp.json().get("accessToken") # 注意：Pydantic 使用驼峰命名 access_token -> accessToken
            print("✅ Login successful, got token")
            return token
        else:
            print(f"❌ Login failed: {resp.status_code} - {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None


def main():
    # 0. 获取认证令牌
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # 1. 连接 WebSocket（带认证）
    print("🔌 Connecting to WebSocket...")
    try:
        sio.connect(
            WS_URL,
            transports=['polling', 'websocket'],
            socketio_path=WS_PATH,
            auth={"token": token}  # 传递 JWT token
        )
    except Exception as e:
        print(f"Failed to connect to WS: {e}")
        return

    # 2. 触发 API
    print("🚀 Triggering Workflow via API...")
    payload = {
        "product_name": "未来派悬浮滑板",
        "features": ["磁悬浮技术", "时速 80km/h", "无线充电"]
    }
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(API_URL, json=payload, headers=headers)
        print(f"API Response: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Failed to call API: {e}")
        return

    # 3. 等待事件
    print("👂 Listening for events (Press Ctrl+C to stop)...")
    sio.wait()

if __name__ == "__main__":
    main()
