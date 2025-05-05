# Voicevox MCP Server

Model Context Protocol (MCP)に準拠したVoicevoxクライアントサーバー

## 概要

このプロジェクトは、Voicevox Engineを利用して音声合成を行い、その結果を再生するMCPサーバーを提供します。CursorやClineなどのAIツールから呼び出し可能なエンドポイントを提供し、テキストを音声に変換して再生する機能を実現します。
注意）voicevoxのデフォルト仕様ですが、英単語や全て英文字一字毎にアルファベットを発声します。回避するには、独自辞書を用意し登録する場合と、投入するテキストに単語をカタカナ化する方法の2通り存在します。
LLMに指示しても現時点では全ては上手くはいかないかと思います。独自辞書作成インタフェースは現時点では未実装です。

## 機能

- テキストから音声クエリ（Audio Query）への変換
- 音声クエリからWAVデータへの変換
- 生成した音声データの再生
- MCPプロトコルに準拠したJSON-RPC over stdioインターフェース

## 必要条件

- Python 3.10以上
- Voicevox Engine（ローカルまたはリモートで実行中）
- 必要なPythonパッケージ（requirements.txtを参照）

## インストール

1. リポジトリをクローン
   ```bash
   git clone https://github.com/yourusername/voicevox-mcp-vc1.git
   cd voicevox-mcp-vc1
   ```

2. 依存関係のインストール
   ```bash
   uv sync
   ```

3. Voicevox Engineの起動
   ```bash
   # CPU版 Dockerを使用する場合
   docker pull voicevox/voicevox_engine:cpu-latest
   docker run --rm -p '127.0.0.1:50021:50021' voicevox/voicevox_engine:cpu-latest
   ```
   ```bash
   # GPU版 Dockerを使用する場合
   docker pull voicevox/voicevox_engine:nvidia-latest
   docker run --rm --gpus all -p '127.0.0.1:50021:50021' voicevox/voicevox_engine:nvidia-latest
   ```

## 使用方法

### CLINE / Roo code
- デフォルト起動の場合（http://127.0.0.1:50021 spaker id:1）
```json
{
  "mcpServers": {
    "voicevox-mcp-light": {
      "disabled": false,
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/full path/voicevox_mcp_light/",
        "python",
        "-m",
        "src.main"
      ],
      "transportType": "stdio",
      "alwaysAllow": [],
      "env": {
        "PULSE_SERVER": "/run/user/1000/pulse/native"
      }
    }
  }
}
```

```json
    "voicevox-mcp-light": {
      "disabled": false,
      "command": "/full path/uv",
      "args": [
        "run",
        "--directory",
        "/full path/voicevox_mcp_light/",
        "python",
        "-m",
        "src.main",
        "--speaker",
        "8"
      ],
      "transportType": "stdio",
      "alwaysAllow": [],
      "env": {
        "PULSE_SERVER": "/run/user/1000/pulse/native"
      }
    }
```
- PULSE_SERVER の内容は下記コマンドで調べた結果を転記してください
``` bash
# パルスオーディオのステータスを確認
pactl info
```

Windows / Mac の場合は env の中身は不要とClaude回答でした。現在未テストです。
Ubuntu 22.04 で開発テストを実施。

Roo codeの場合、MCP CLientがDEBUG情報を吐き出します。これは開発時にデバッグ情報をLLMに埋め込ませたことによるもので、放置していますのでご容赦ください。CLINEでは表示されません。
Claude Desktopでは現時点未検証です。

#### オプション

- `--host`: Voicevox EngineのホストIPアドレス（デフォルト: 127.0.0.1）
- `--port`: Voicevox Engineのポート番号（デフォルト: 50021）
- `--speaker`: 音声モデルID（デフォルト: 3）
[音声モデルID](https://github.com/VOICEVOX/voicevox_vvm/blob/main/README.md#%E9%9F%B3%E5%A3%B0%E3%83%A2%E3%83%87%E3%83%ABvvm%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%A8%E5%A3%B0%E3%82%AD%E3%83%A3%E3%83%A9%E3%82%AF%E3%82%BF%E3%83%BC%E3%82%B9%E3%82%BF%E3%82%A4%E3%83%AB%E5%90%8D%E3%81%A8%E3%82%B9%E3%82%BF%E3%82%A4%E3%83%AB-id-%E3%81%AE%E5%AF%BE%E5%BF%9C%E8%A1%A8) を参照してください。

### MCPクライアントからの使用

このサーバーは、MCPプロトコルに準拠したJSON-RPC over stdioインターフェースを提供します。
Claude DesktopやCursorなどのMCPクライアントから以下のように使用できます：

```
# MCPサーバーのインストール（Claude Desktopの場合）
mcp install src/main.py

# ツールの呼び出し例
synthesizeAndPlay(message="こんにちは、世界！")
```

## 開発

### テストの実行

```bash
python -m pytest
```

### コードスタイル

このプロジェクトはPEP 8コーディング規約に従っています。

## ライセンス

[MITライセンス](LICENSE)

## 謝辞

- [VOICEVOX](https://voicevox.hiroshiba.jp/) - 高品質な音声合成エンジン
- [VOICEVOX Engine Github](https://github.com/VOICEVOX/voicevox_engine)
- [Model Context Protocol](https://modelcontextprotocol.io/) - LLMとのコンテキスト共有のための標準プロトコル
- [Model Context Protocol (MCP) サーバを使ってみた・作ってみた](https://zenn.dev/karaage0703/articles/42f7b0655a6af8) - MCP全般の基礎として 
- [notion-mcp-light](https://github.com/karaage0703/notion-mcp-light) - NotionMCP Light 構造解析し Vibe Coding に
- [PythonとVOICEVOXで音声合成](https://zenn.dev/karaage0703/articles/0187d1d1f4d139) - voicevox の知識として