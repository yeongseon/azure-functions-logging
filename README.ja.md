# Azure Functions Logging

[![PyPI](https://img.shields.io/pypi/v/azure-functions-logging-python.svg)](https://pypi.org/project/azure-functions-logging-python/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/azure-functions-logging-python/)
[![CI](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/ci-test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/ci-test.yml)
[![Release](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/release.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/release.yml)
[![Security Scans](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/security.yml/badge.svg)](https://github.com/yeongseon/azure-functions-logging-python/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/yeongseon/azure-functions-logging-python/branch/main/graph/badge.svg)](https://codecov.io/gh/yeongseon/azure-functions-logging-python)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://yeongseon.github.io/azure-functions-logging-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

他の言語: [English](README.md) | [한국어](README.ko.md) | [简体中文](README.zh-CN.md)

**Azure Functions Python v2 プログラミングモデル**向けの、開発者に優しい logging ヘルパーです。

## Why Use It

Azure Functions Python ハンドラーには、共通の logging の課題があります。

- ログ出力が視覚的に密集しており、スキャンが困難
- エラーが INFO レベルのノイズに埋もれて目立たない
- デフォルトのフォーマットが人間にとって読みやすく最適化されていない

`azure-functions-logging-python` は、最小限のセットアップで色分けされ、きれいにフォーマットされたログ出力を提供します。Python の標準 `logging` モジュールと互換性があります。

## Scope

- Azure Functions Python **v2 プログラミングモデル**
- Python 標準の `logging` モジュール
- 色付けおよび JSON 形式のログ出力
- 呼び出しコンテキストの注入 (Invocation context injection) とコールドスタートの検出

このパッケージは、分散トレーシング、ログ集約、または OpenTelemetry との統合を目的としていません。

## Features

- ログレベルの色分け (DEBUG はグレー、INFO は青、WARNING は黄色、ERROR は赤、CRITICAL は太字の赤)
- 本番環境および CI 環境向けの JSON 構造化ログ出力
- すっきりとした `[TIME] [LEVEL] [LOGGER] message` フォーマット
- `setup_logging()` による一行での設定
- 便利な logger 作成のための `get_logger(__name__)` ヘルパー
- 呼び出しコンテキスト (invocation_id, function_name, trace_id) の自動注入
- 手動のインストルメンテーションなしでのコールドスタート検出
- `logger.bind(user_id="abc")` によるコンテキストのバインド
- `host.json` のログレベル競合に関する警告
- 読みやすいスタックトレースを含む例外出力
- Python 標準の `logging` モジュールと互換

## Installation

```bash
pip install azure-functions-logging-python
```

ローカル開発用:

```bash
git clone https://github.com/yeongseon/azure-functions-logging-python.git
cd azure-functions-logging-python
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

- 全ドキュメント: [yeongseon.github.io/azure-functions-logging-python](https://yeongseon.github.io/azure-functions-logging-python/)
- 製品要件: `PRD.md`

## Ecosystem

- [azure-functions-validation-python](https://github.com/yeongseon/azure-functions-validation-python) — リクエストとレスポンスのバリデーション
- [azure-functions-openapi-python](https://github.com/yeongseon/azure-functions-openapi-python) — OpenAPI と Swagger UI
- [azure-functions-doctor-python](https://github.com/yeongseon/azure-functions-doctor-python) — 診断 CLI
- [azure-functions-scaffold-python](https://github.com/yeongseon/azure-functions-scaffold-python) — プロジェクトスキャフォールディング
- [azure-functions-cookbook-python](https://github.com/yeongseon/azure-functions-cookbook-python) — レシピとサンプル

## Disclaimer

このプロジェクトは独立したコミュニティプロジェクトであり、Microsoft と提携・承認・保守関係にはありません。

Azure および Azure Functions は Microsoft Corporation の商標です。

## License

MIT
