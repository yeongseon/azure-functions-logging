# Azure Functions Logging

[![PyPI](https://img.shields.io/pypi/v/azure-functions-logging.svg)](https://pypi.org/project/azure-functions-logging/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/azure-functions-logging/)
[![CI](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/ci-test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/ci-test.yml)
[![Release](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/release.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/release.yml)
[![Security Scans](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/security.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/yeongseon/azure-functions-logging-python/branch/main/graph/badge.svg)](https://codecov.io/gh/yeongseon/azure-functions-logging-python)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://yeongseon.github.io/azure-functions-logging-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

다른 언어: [English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

**Azure Functions Python v2 프로그래밍 모델**을 위한 개발자 친화적인 logging 헬퍼입니다.

## Why Use It

Azure Functions Python 핸들러는 다음과 같은 logging 관련 불편함이 있습니다:

- 로그 출력이 시각적으로 조밀하여 훑어보기 어려움
- 에러가 일반 info 레벨 로그 사이에서 잘 눈에 띄지 않음
- 기본 포맷이 사람이 읽기에 최적화되어 있지 않음

`azure-functions-logging`은 Python의 표준 `logging` 모듈과 호환되며, 최소한의 설정으로 색상이 적용되고 깔끔하게 포맷된 로그 출력을 제공합니다.

## Scope

- Azure Functions Python **v2 프로그래밍 모델**
- Python 표준 `logging` 모듈
- 색상 적용 및 JSON 로그 출력
- Invocation context 주입 및 cold start 감지

이 패키지는 분산 트레이싱, 로그 수집 또는 OpenTelemetry 통합을 대상으로 하지 않습니다.

## Features

- 로그 레벨별 색상 적용 (DEBUG 회색, INFO 파란색, WARNING 노란색, ERROR 빨간색, CRITICAL 굵은 빨간색)
- 프로덕션 및 CI 환경을 위한 JSON 구조화된 로그 출력
- 깔끔한 `[TIME] [LEVEL] [LOGGER] message` 포맷
- 한 줄의 코드로 설정 가능한 `setup_logging()`
- 편리한 logger 생성을 위한 `get_logger(__name__)` 헬퍼
- invocation_id, function_name, trace_id 등 호출 context 자동 주입
- 별도의 코드 삽입 없이 cold start 감지
- `logger.bind(user_id="abc")`를 통한 context 바인딩
- `host.json` 로그 레벨 충돌 경고
- 가독성 좋은 스택 트레이스를 포함한 예외 출력
- Python 표준 `logging` 모듈과 호환

## Installation

```bash
pip install azure-functions-logging
```

로컬 개발용:

```bash
git clone https://github.com/yeongseon/azure-functions-logging-python.git
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

- 전체 문서: [yeongseon.github.io/azure-functions-logging-python](https://yeongseon.github.io/azure-functions-logging-python/)
- 제품 요구 사항: `PRD.md`

## Ecosystem

- [azure-functions-validation](https://github.com/yeongseon/azure-functions-validation) — 요청 및 응답 검증
- [azure-functions-openapi](https://github.com/yeongseon/azure-functions-openapi) — OpenAPI 및 Swagger UI
- [azure-functions-langgraph](https://github.com/yeongseon/azure-functions-langgraph) — LangGraph 배포 어댑터
- [azure-functions-doctor](https://github.com/yeongseon/azure-functions-doctor) — 진단 CLI
- [azure-functions-scaffold](https://github.com/yeongseon/azure-functions-scaffold) — 프로젝트 스캐폴딩
- [azure-functions-durable-graph](https://github.com/yeongseon/azure-functions-durable-graph) — Durable Functions 기반 그래프 런타임 *(계획)*
- [azure-functions-python-cookbook](https://github.com/yeongseon/azure-functions-python-cookbook) — 레시피 및 예제

## Disclaimer

이 프로젝트는 독립적인 커뮤니티 프로젝트이며 Microsoft와 제휴되어 있지 않고, Microsoft의 후원이나 유지보수를 받지 않습니다.

Azure 및 Azure Functions는 Microsoft Corporation의 상표입니다.

## License

MIT
