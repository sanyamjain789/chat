import asyncio
import websockets
import json

async def test_websocket():
    # Test WebSocket connection
    uri = "ws://localhost:8000/ws/chat/684d4049cd33423a20ad2e12"  # Use a real user ID

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")

            # Send a test message
            test_message = {
                "recipient_id": "684d424957c049fb888bab6f",  # Another user ID
                "message": "Hello from test script!"
            }

            await websocket.send(json.dumps(test_message))
            print("✅ Test message sent!")

            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✅ Received response: {response}")
            except asyncio.TimeoutError:
                print("⚠️ No response received within 5 seconds")

    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
