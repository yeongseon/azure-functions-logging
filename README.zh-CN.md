# Azure Functions Logging

[![PyPI](https://img.shields.io/pypi/v/azure-functions-logging.svg)](https://pypi.org/project/azure-functions-logging/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/azure-functions-logging/)
[![CI](https://github.com/yeongseon/azure-functions-logging/actions/workflows/ci-test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging/actions/workflows/ci-test.yml)
[![Release](https://github.com/yeongseon/azure-functions-logging/actions/workflows/release.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging/actions/workflows/release.yml)
[![Security Scans](https://github.com/yeongseon/azure-functions-logging/actions/workflows/security.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/yeongseon/azure-functions-logging/branch/main/graph/badge.svg)](https://codecov.io/gh/yeongseon/azure-functions-logging)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://yeongseon.github.io/azure-functions-logging/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

其他语言: [English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

专为 **Azure Functions Python v2 编程模型** 设计的开发者友好型 logging 助手。

## Why Use It

Azure Functions Python 处理程序通常面临以下 logging 痛点：

- 日志输出过于密集，难以快速浏览
- 错误信息淹没在 INFO 级别的日志中，不够醒目
- 默认格式未针对人类阅读进行优化

`azure-functions-logging` 提供彩色且格式整洁的日志输出，兼容 Python 标准 `logging` 模块，且只需极简配置。

## Scope

- Azure Functions Python **v2 编程模型**
- Python 标准 `logging` 模块
- 彩色及 JSON 格式日志输出
- 调用上下文注入 (Invocation context injection) 及冷启动检测

本项目 **不** 涉及分布式追踪、日志聚合或 OpenTelemetry 集成。

## Features

- 彩色日志级别（DEBUG 灰色，INFO 蓝色，WARNING 黄色，ERROR 红色，CRITICAL 粗体红色）
- 适用于生产和 CI 环境的 JSON 结构化日志输出
- 整洁的 `[TIME] [LEVEL] [LOGGER] message` 格式
- `setup_logging()` 一行式配置
- 便于创建 logger 的 `get_logger(__name__)` 助手
- 自动注入调用上下文 (invocation_id, function_name, trace_id)
- 无需手动埋点的冷启动检测
- 通过 `logger.bind(user_id="abc")` 进行上下文绑定
- `host.json` 日志级别冲突警告
- 友好且易读的异常堆栈轨迹输出
- 兼容 Python 标准 `logging` 模块

## Installation

```bash
pip install azure-functions-logging
```

本地开发用:

```bash
git clone https://github.com/yeongseon/azure-functions-logging.git
cd azure-functions-logging
pip install -e .[dev]
```

## Quick Start

```python
from azure_functions_logging import get_logger, setup_logging

setup_logging()

logger = get_logger(__name__)
logger.info("Processing request")
```

### JSON Output

```python
setup_logging(format="json")

logger = get_logger(__name__)
logger.info("Processing request")
# {"timestamp": "...", "level": "INFO", "logger": "...", "message": "Processing request", ...}
```

### Context Injection

```python
from azure_functions_logging import inject_context

def my_function(req, context):
    inject_context(context)
    logger.info("Handling request")  # includes invocation_id, function_name, trace_id
```

### Context Binding

```python
bound = logger.bind(user_id="abc", operation="checkout")
bound.info("Processing")  # includes user_id + operation in every log line
```

## Documentation

- 完整文档: [yeongseon.github.io/azure-functions-logging](https://yeongseon.github.io/azure-functions-logging/)
- 产品需求文档: `PRD.md`

## Ecosystem

- [azure-functions-validation](https://github.com/yeongseon/azure-functions-validation) — 请求与响应校验
- [azure-functions-openapi](https://github.com/yeongseon/azure-functions-openapi) — OpenAPI 与 Swagger UI
- [azure-functions-doctor](https://github.com/yeongseon/azure-functions-doctor) — 诊断 CLI
- [azure-functions-scaffold](https://github.com/yeongseon/azure-functions-scaffold) — 项目脚手架
- [azure-functions-python-cookbook](https://github.com/yeongseon/azure-functions-python-cookbook) — 食谱与示例

## Disclaimer

本项目是独立的社区项目，与 Microsoft 没有关联，也未获得 Microsoft 的认可或维护。

Azure 和 Azure Functions 是 Microsoft Corporation 的商标。

## License

MIT
