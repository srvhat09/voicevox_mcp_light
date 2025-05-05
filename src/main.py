"""
Voicevox MCP Serverのメインモジュール。

このモジュールは、コマンドライン引数を解析し、MCPサーバーを起動します。
"""

import argparse
import asyncio
import logging
import sys
import traceback

import mcp.server.stdio
from mcp.server.models import InitializationOptions

from src.mcp_server import MCPServer

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def run_server(server):
    """
    サーバーを実行します。

    Args:
        server: MCPServerインスタンス
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Starting MCP server")
        # InitializationOptionsクラスを使用
        init_options = InitializationOptions(
            server_name=server.name,
            server_version="0.1.0",
            capabilities={
                "tools": {
                    "listChanged": False
                },
                "resources": {
                    "listChanged": False,
                    "subscribe": False
                }
            }
        )
        
        await server.run(
            read_stream,
            write_stream,
            init_options,
        )


def main():
    """
    メイン関数。
    
    コマンドライン引数を解析し、MCPサーバーを起動します。
    """
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="Voicevox MCP Server Light")
    parser.add_argument("--host", help="Voicevoxエンジンのホスト名", default=None)
    parser.add_argument("--port", help="Voicevoxエンジンのポート番号", default=None)
    parser.add_argument("--speaker", help="話者ID", default=None)
    
    args = parser.parse_args()
    
    # MCPサーバーの作成と起動
    server = MCPServer(
        host=args.host,
        port=args.port,
        speaker=args.speaker
    )
    
    # サーバーの実行
    try:
        asyncio.run(run_server(server))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
