# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tomllib
from typing import Annotated

import google.cloud.logging
import vertexai
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models.vertex_search_models import (
    VertexSearchFirstConvRequest,
    VertexSearchFollowupRequest,
)
from routers.cache import router as cache_router
from routers.hello import router as hello_router
from routers.page_content_dispatch import router as content_update_dispatch_router
from routers.vertex_imagen import router as vertex_imagen_router
from routers.vertex_llm import router as vertex_llm_router
from routers.vertex_search import router as vertex_search_router
from routers.vertex_search import trigger_first_search, trigger_followup_search
from utils.content_cache import ContentCache
from utils.content_utils import ContentState
from views.magi import magi_follow_up_controls
from views.offcanvas import offcanvas

origins = ["*"]

with open("./config.toml", "rb") as f:
    config = tomllib.load(f)

PROJECT_ID = config["global"]["project_id"]
LOCATION = config["global"]["location"]

client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging()

cache = ContentCache(config=config)
cache.refresh(refresh_blogs=True, refresh_content=True)

vertexai.init(project=PROJECT_ID, location=LOCATION)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hello_router, prefix="/hello", tags=["hello"])


def get_state_by_action(action: str) -> ContentState:
    if action.lower() == "edit":
        return ContentState.DRAFT
    elif action.lower() == "review":
        return ContentState.REVIEW
    else:
        return ContentState.PRODUCTION


def execute_first_search(thequery: str):
    search_query = VertexSearchFirstConvRequest(search_query=thequery)
    response = trigger_first_search(search_query)
    message_pairs = response.message_pairs
    conversation_name = response.conversation_name
    search_results = response.search_results
    if len(search_results) > 3:
        search_results = search_results[:3]

    return message_pairs, search_results, conversation_name


def execute_follow_up_search(thequery: str, conversation_name: str):
    request = VertexSearchFollowupRequest(
        search_query=thequery, conversation_name=conversation_name
    )
    response = trigger_followup_search(request)
    message_pairs = response.message_pairs
    conversation_name = response.conversation_name
    search_results = response.search_results
    if len(search_results) > 3:
        search_results = search_results[:3]

    return message_pairs, search_results, conversation_name


# UI APIs
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "home_content": cache.get_content("home"),
            "read_only": "true",
        },
    )


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):  # noqa: F811
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "home_content": cache.get_content("home"),
            "read_only": "true",
        },
    )


@app.get("/home/{action}", response_class=HTMLResponse)
async def home_publish(request: Request, action: str):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "home_content": cache.get_webcontent_for_edit("home"),
            "read_only": "true" if action == "publish" else "false",
        },
    )


@app.get("/clear-magi", response_class=HTMLResponse)
async def clear(request: Request):
    return """<input type="text" id="search-bar-query" name="thequery" title="Search" type="search"
                placeholder="Ask ..."
          hx-trigger="keydown[keyCode==13] from:input"
          hx-post="/web/magi"
          hx-indicator="#loading-initial"
          hx-include="#search-bar-query"
          hx-target="#magi-container-target"
          aria-label="Search" />"""


@app.get("/faq", response_class=HTMLResponse)
async def faq(request: Request):
    return templates.TemplateResponse(
        "faq.html",
        {
            "read_only": "true",
            "request": request,
            "faq_content": cache.get_content("faq"),  # static_files_dict['faq']
        },
    )


@app.get("/faq/{action}", response_class=HTMLResponse)
async def faq_action(request: Request, action: str):  # noqa: F811
    state = get_state_by_action(action)
    content = cache.get_webcontent_by_state("faq", state)
    if content is None:
        content = cache.get_webcontent_for_edit("faq")

    return templates.TemplateResponse(
        "faq.html",
        {
            "read_only": "true",  # noqa: F601
            "request": request,
            "faq_content": content,
            "read_only": "true" if action == "publish" else "false",  # noqa: F601
        },
    )


@app.get("/allblog", response_class=HTMLResponse)
async def allblog(request: Request):  # noqa: F811
    # print(static_files_dict['allblog'])
    return templates.TemplateResponse(
        "allblog.html",
        {
            "read_only": "true",
            "request": request,
            "all_blog_content": cache.get_content("allblog"),
        },
    )


@app.get("/allblog/{action}", response_class=HTMLResponse)
async def allblog_action(request: Request, action: str):  # noqa: F811
    # print(static_files_dict['allblog'])
    state = get_state_by_action(action)
    content = cache.get_webcontent_by_state("allblog", state)
    if content is None:
        content = cache.get_webcontent_for_edit("allblog")
    state = get_state_by_action(action)
    return templates.TemplateResponse(
        "allblog.html",
        {
            "request": request,
            "all_blog_content": content,
            "read_only": "true" if action == "publish" else "false",
        },
    )


@app.get("/blog/{blog_id}", response_class=HTMLResponse)
async def get_blog_content(request: Request, blog_id: int):
    blog_content = cache.get_blog(blog_id=f"{blog_id}")

    return templates.TemplateResponse(
        "blog.html",
        {
            "request": request,
            "offcanvas": offcanvas,
            "read_only": "true",
            "blogs_content": blog_content,
        },
    )


# Edit / Read-only Mode
@app.get("/blog/{blog_id}/{action}", response_class=HTMLResponse)
async def get_blog_content_action(
    request: Request, blog_id: int, action: str
):  # noqa: F811
    state = get_state_by_action(action=action)
    blog_content = cache.get_blog_by_state(content_id=str(blog_id), state=state)

    if blog_content is None:
        blog_content = cache.get_blog_for_edit(blog_id=str(blog_id))

    return templates.TemplateResponse(
        "blog.html",
        {
            "request": request,
            "offcanvas": offcanvas,
            "blogs_content": blog_content,
            "read_only": "true" if action == "publish" else "false",
        },
    )


@app.post("/web/magi", response_class=HTMLResponse)
async def search(request: Request, thequery: Annotated[str, Form()]):
    messages, search_results, conversation_name = execute_first_search(thequery)

    return templates.TemplateResponse(
        "magi.html",
        {
            "request": request,
            "magi_follow_up_controls": magi_follow_up_controls,
            "messages": messages,
            "search_results": search_results,
            "conversation_name": conversation_name,
        },
    )


@app.post("/web/magi-follow", response_class=HTMLResponse)
async def search_follow_up(
    request: Request, thequery: Annotated[str, Form()], conversation_name: str
):
    print(f"CONV {conversation_name}")
    messages, search_results, conversation_name = execute_follow_up_search(
        thequery, conversation_name
    )

    return templates.TemplateResponse(
        "magi.html",
        {
            "request": request,
            "magi_follow_up_controls": magi_follow_up_controls,
            "messages": messages,
            "search_results": search_results,
            "conversation_name": conversation_name,
        },
    )


@app.get("/test", response_class=HTMLResponse)
async def test_read_only(request: Request):
    test_content = cache.get_content("test")
    return templates.TemplateResponse(
        "test.html",
        {
            "request": request,
            "test_content": test_content,
            "read_only": "true",
        },
    )


@app.get("/test/{action}", response_class=HTMLResponse)
async def test_editing(request: Request, action: str):
    state = get_state_by_action(action)
    content = cache.get_webcontent_by_state("test", state)
    if content is None:
        content = cache.get_webcontent_for_edit("test")
    return templates.TemplateResponse(
        "test.html",
        {
            "request": request,
            "test_content": content,
            "read_only": "true" if action == "publish" else "false",
        },
    )


# include backend routers
app.include_router(hello_router, prefix="/hello", tags=["hello"])
app.include_router(vertex_imagen_router, prefix="/imagen", tags=["imagen"])
app.include_router(
    vertex_search_router, prefix="/vertex-search", tags=["vertex-search"]
)
app.include_router(vertex_llm_router, prefix="/vertex-llm", tags=["vertex-llm"])
app.include_router(
    content_update_dispatch_router, prefix="/web-edit", tags=["webcontent"]
)
app.include_router(cache_router, prefix="/cache", tags=["cache"])
