
# 要件・設計書

## 1. 要件定義

### 1.1 基本情報
- ソフトウェア名称: Voicevox MCP Server
- リポジトリ名: voicevox-mcp-srver

### 1.2 プロジェクト概要

本プロジェクトは、voicevoxの公式voicevox_engineが提供しているdockerイメージを利用しHTTP経由でアクセスし音声を取得し再生まで行う非公式のMCPサーバーを構築することを目的とする。

### 1.3 機能要件

#### 1.3.1 Text → Audio Query
- speaker idはデフォルト値を用意しますが、変更された場合はリクエストパラメタを変更する
- 入力テキストの改行情報がある場合、末尾に必ず「。」を挿入しておく。これは、voicevox再生時の切り替えの間を空けるためです。
- 加工されたテキストをvoicevoxの音声データ用に変換するqueryにvoicevox_engineのAPIを利用し取得
- Audio Query を返却

#### 1.3.2 Audio Query → Wave
- speaker idはデフォルト値を用意しますが、変更された場合はリクエストパラメタを変更する
- 1.3.1で作成したAudio Queryからwavフォーマットに変換を行う
- wavフォーマットを返却

#### 1.3.3 MCPサーバー対応
- Model Context Protocol（MCP）に準拠
- CursorやClineなどのAIツールから呼び出し可能なエンドポイントを提供
- `python-sdk` を利用した JSON-RPC over stdio ベースで動作
- 1.3.2 で作成したwavデータを `sounddevice` と `asyncio` を利用して非同期でPCスピーカーから鳴らす

### 1.4 非機能要件

- 迅速なレスポンス（LLMを使用しないため）
- シンプルな構成とメンテナンス性重視
- log吐き出し処理として `voicevox_client.py` に実装
  - MCP環境である関係で、stdoutを使わないように実装する
  - log吐き出しディレクトリはソース当該ディレクトリ中の `log` ディレクトリ（無ければ作成）とし、linux ログと似た構造（日付時刻 + メッセージタイプ + メッセージ）を入れてください

### 1.5 制約条件

- Python 3.10以上で動作
- ファイルインタフェースを使わないで処理することで応答性をあげる

### 1.6 開発環境

- 言語: Python
- フレームワーク: FastAPI（または標準JSON-RPC）
- 外部ライブラリ:
  - `python-sdk`
- 内部ライブラリ:
  - ``
- voicevox HTTPリクエスト
  - `voicevox_client.py`
- 仮想環境、パッケージ管理: uv
  - ライブラリのインストール確認には `uv pip list` で行ってください

### 1.7 成果物

- Python製MCPサーバースクリプト
- ドキュメント変換ユーティリティ
- README / 利用手順
- 設計書

## 2. システム設計

### 2.1 システム概要設計

#### 2.1.1 システムアーキテクチャ
```
[MCPクライアント(Cline, Cursor)] <-> [MCPサーバー (Python, python-sdk)] <-> [HTTP リクエスト (httpx)]
                                            |
                                       [wav再生 (sounddevice, asyncio)]
```

#### 2.1.2 主要コンポーネント
- **main**
  - 起動オプション管理（IPアドレス、ポート、話者idの各変更値取得）
  - MCPサーバー起動
- **MCPサーバー (`VoicevoxServer`, `python-sdk` の `Server` ベース)**
  - JSON-RPC over stdio をリッスンし、MCPリクエストを処理
  - Voicevoxクライアント管理
  - wavデータ再生
  - ログ管理
- **Voicevoxクライアント (`VoicevoxClient`, `httpx` 利用)**
  - voicevox_engine への非同期HTTPリクエストを実行

### 2.2 詳細設計

#### 2.2.1 クラス設計

##### `MCPServer`
```python
class MCPServer
    def synthesize_and_play(message: str) -> None
```

##### `VoicevoxClient`
```python
class VoicevoxClient:
    def __init__(self, host=HOST, port=PORT, speaker=SPEAKER):
        # 実装は `voicevox_client.py` ソースを確認のこと

    async def audio_query(self, text: str) -> dict:
        """テキストから Audio Query を取得する"""
        # 実装は `voicevox_client.py` ソースを確認のこと

    async def synthesis(self, query: dict) -> bytes:
        """Audio Query から wav データを生成する"""
        # 実装は `voicevox_client.py` ソースを確認のこと
```

### 2.3 インターフェース設計

- JSON-RPCエンドポイント:
  - `synthesizeAndPlay`: メッセージ → wavデータ再生
  
### 2.4 セキュリティ設計

- 外部からの直接アクセスは制限（ローカル環境前提）

### 2.5 テスト設計

- 単体テスト
  - audio queryの正確性
  - synthesisの正確性
  - 音声再生可否
- 統合テスト
  - テキストから音声再生までの動作
  - MCPリクエストを模擬した動作確認

### 2.6 開発環境・依存関係

- Python 3.10+
- `python-sdk` (MCP)
- `requests` (HTTPリクエスト)
- `simpleaudio` (音声再生)
- `argparse` (mcp config 起動オプション)

### 2.7 開発工程

| フェーズ | 内容 | 期間 |
|---------|------|------|
| 要件定義 | 本仕様書作成 | 第1週 |
| 設計 | アーキテクチャ・モジュール設計 | 第1週 |
| 実装 | 各モジュールの開発 | 第2-3週 |
| テスト | 単体・統合テスト | 第4週 |
| リリース | ドキュメント整備・デプロイ対応 | 第5週 |
