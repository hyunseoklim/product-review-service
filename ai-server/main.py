from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from api.recommend import router as recommend_router
from redis.asyncio import Redis
import json
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Recommendation Server")

# Redis 연결 설정 (Docker 서비스명 'redis' 사용)
REDIS_URL = "redis://redis:6379/0"

app.include_router(recommend_router)


@app.get("/")
def root():
    return {"message": "AI server is running"}


@app.websocket("/ws/task/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    클라이언트가 task_id를 가지고 웹소켓에 접속하면,
    해당 task의 완료 알림을 Redis에서 기다렸다가 전송합니다.
    """
    logger.info(f"[WS CONNECT] task_id={task_id}")

    await websocket.accept()

    redis = Redis.from_url(REDIS_URL)
    pubsub = redis.pubsub()
    channel_name = f"task_result_{task_id}"

    logger.info(f"[REDIS SUBSCRIBE] channel={channel_name}")

    await pubsub.subscribe(channel_name)

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            raw_data = message["data"]

            if isinstance(raw_data, bytes):
                raw_data = raw_data.decode("utf-8")

            logger.info(f"[REDIS RECEIVE] task_id={task_id}")

            data = json.loads(raw_data)

            logger.info(f"[WS SEND] task_id={task_id} status={data.get('status')}")

            await websocket.send_json(data)

            # 결과 전송 후 연결 종료 (1회성 알림)
            break

    except WebSocketDisconnect:
        logger.warning(f"[WS DISCONNECT] task_id={task_id}")

    except Exception as e:
        logger.exception(f"[WS ERROR] task_id={task_id} error={str(e)}")

    finally:
        logger.info(f"[WS CLEANUP] task_id={task_id}")

        await pubsub.unsubscribe(channel_name)
        await pubsub.close()
        await redis.close()

        try:
            await websocket.close()
        except Exception:
            pass