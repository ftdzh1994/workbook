from flask import Flask, request
import contextvars
from loguru import logger
import uuid
import time
import sys
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# 创建一个 contextvars 变量来存储请求 ID


request_id = contextvars.ContextVar('request_id', default=None)

# 自定义 loguru 格式，包含 request_id
def formatter(record):
    record["extra"]["request_id"] = request_id.get()
    return "{time} ({file}:{line}) [{level}] |{extra[request_id]}|: {message}\n"

# 配置 loguru
logger.remove()  # 移除默认的处理器
logger.add(sys.stderr, format=formatter)
logger.add("app.log", format=formatter, rotation="500 MB")

# 创建线程池
executor = ThreadPoolExecutor(max_workers=3)

@app.before_request
def before_request():
    # 为每个请求生成唯一的 ID
    request_id.set(str(uuid.uuid4()))
    logger.info(f"Request started: {request_id.get()}")

@app.after_request
def after_request(response):
    logger.info(f"Request completed: {request_id.get()}")
    return response

def slow_operation():
    # 模拟耗时操作
    time.sleep(2)
    # 在函数内记录日志时会自动使用正确的 request_id
    logger.info(f"Slow operation completed for request: {request_id.get()}")
    return "Slow operation result"

@app.route('/')
def hello():
    req_id = request_id.get()
    logger.info(f"Processing request: {req_id}")
    # 使用 contextvars.run 运行耗时操作
    future = executor.submit(contextvars.copy_context().run, slow_operation)
    result = future.result()
    return f"Hello, World! Request ID: {req_id}, Result: {result}"

if __name__ == '__main__':
    app.run(threaded=True)
