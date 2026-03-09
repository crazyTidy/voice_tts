#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import logging
import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from .middlewares.session_middleware import SessionMiddleware
from .routers import hello_world_router, swagger_router, tts_router, tts_stream_router, asr_router, preset_router
from .settings import directory_config, environment_config, file_config, config
from .utils import log_util


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 开始
    log_util.set_log(debug=True)
    yield
    # 结束


app = FastAPI(
    dependencies=None,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
)

# 初始化 prometheus
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# 配置中间件
# 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(SessionMiddleware)

# 挂载静态文件目录
app.mount(
    "/statics",
    StaticFiles(directory=directory_config.CONST_STATIC_DIRECTORY),
    name="statics",
)
# 添加 router
# swagger 调试 router，不要删除
app.include_router(swagger_router.router)
# 其它用户自定义 router
app.include_router(hello_world_router.router)
# TTS/ASR/Preset routers
app.include_router(tts_router.router)
app.include_router(tts_stream_router.router)
app.include_router(asr_router.router)
app.include_router(preset_router.router)


@app.on_event("startup")
async def startup_event():
    log_util.set_log(debug=True)


@app.on_event("shutdown")
def shutdown_event():
    log_util.set_log(debug=True)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exception: Exception):
    """全局异常处理。"""
    logging.error(traceback.format_exc())
    body_json = {
        "code": 500,
        "message": "服务器出错，请重新请求。",
    }
    return JSONResponse(content=body_json, status_code=500)


def run_as_http_server():
    """以 http 启动服务。"""
    uvicorn.run(
        app=f"{__package__}.app:app",
        host=environment_config.HOST,
        port=environment_config.PORT,
        reload=environment_config.RELOAD,
        workers=environment_config.WORKERS,
    )


def run_as_https_server():
    """以 https 单向认证启动服务。"""
    uvicorn.run(
        app=f"{__package__}.app:app",
        host=environment_config.HOST,
        port=environment_config.PORT,
        reload=environment_config.RELOAD,
        workers=environment_config.WORKERS,
        ssl_keyfile=file_config.CONST_SERVER_PRIVATE_KEY,
        ssl_certfile=file_config.CONST_SERVER_CERTIFICATE,
    )


def run_as_https_server_client():
    """以 https 双向认证启动服务。"""
    uvicorn.run(
        app=f"{__package__}.app:app",
        host=environment_config.HOST,
        port=environment_config.PORT,
        reload=environment_config.RELOAD,
        workers=environment_config.WORKERS,
        ssl_keyfile=file_config.CONST_SERVER_PRIVATE_KEY,
        ssl_certfile=file_config.CONST_SERVER_CERTIFICATE,
        ssl_ca_certs=file_config.CONST_CA_CERTIFICATE,
        ssl_cert_reqs=2,
    )


def main():
    # 启动入口
    if environment_config.HTTPS == 0:
        run_as_http_server()
    elif environment_config.HTTPS == 1:
        run_as_https_server()
    elif environment_config.HTTPS == 2:
        run_as_https_server_client()
    else:
        raise Exception(f"wrong HTTPS value {environment_config.HTTPS}")


if __name__ == "__main__":
    main()
