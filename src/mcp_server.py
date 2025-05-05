"""
MCPサーバークラスを提供します。

このモジュールは、Model Context Protocol (MCP)に準拠したサーバーを実装し、
voicevoxエンジンを利用して音声合成と再生を行う機能を提供します。
"""

import asyncio
import logging
import os
import wave
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional
import wave, simpleaudio as sa

import sounddevice as sd
from mcp.server import Server

from src.voicevox_client import VoicevoxClient


class MCPServer(Server):
    """
    MCPサーバークラス。
    
    Model Context Protocol (MCP)に準拠したサーバーを実装し、
    voicevoxエンジンを利用して音声合成と再生を行う機能を提供します。
    
    Attributes:
        voicevox_client: VoicevoxClientのインスタンス
        logger: ロギングのためのロガーインスタンス
    """

    def __init__(
        self,
        name: str = "voicevox-mcp-light",
        host: Optional[str] = None,
        port: Optional[str] = None,
        speaker: Optional[str] = None,
    ):
        """
        MCPServerクラスの初期化メソッド。
        
        Args:
            name: サーバー名
            host: voicevoxエンジンのホスト名
            port: voicevoxエンジンのポート番号
            speaker: 話者ID
        """
        super().__init__(name)
        
        # VoicevoxClientの初期化
        self.voicevox_client = VoicevoxClient(host=host, port=port, speaker=speaker)
        
        # ロガーの設定
        self.logger = self._setup_logger()
        
        # ツールの登録
        self._register_tools()
        
        self.logger.info("MCPServer initialized")

    def _setup_logger(self) -> logging.Logger:
        """
        ロガーを設定します。
        
        Returns:
            設定されたロガーインスタンス
        """
        # ログディレクトリの作成
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
        os.makedirs(log_dir, exist_ok=True)
        
        # ロガーの設定
        logger = logging.getLogger("mcp_server")
        logger.setLevel(logging.INFO)
        
        # ファイルハンドラの設定
        log_file = os.path.join(log_dir, f"mcp_server_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # フォーマッタの設定
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # ハンドラの追加
        logger.addHandler(file_handler)
        
        return logger

    def get_capabilities(self, notification_options=None, experimental_capabilities=None):
        """
        サーバーの機能を取得します。
        
        Args:
            notification_options: 通知オプション
            experimental_capabilities: 実験的な機能
            
        Returns:
            サーバーの機能を表す辞書
        """
        from mcp.server.lowlevel import NotificationOptions
        
        if notification_options is None:
            notification_options = NotificationOptions()
            
        if experimental_capabilities is None:
            experimental_capabilities = {}
            
        return {
            "tools": {
                "listChanged": False
            },
            "resources": {
                "listChanged": False,
                "subscribe": False
            },
            "notifications": notification_options.to_dict(),
            "experimental": experimental_capabilities
        }
        
    def _register_tools(self) -> None:
        """
        MCPサーバーにツールを登録します。
        """
        # ツール一覧を提供するハンドラを登録
        @self.list_tools()
        async def handle_list_tools():
            """利用可能なツールの一覧を返します。"""
            from mcp import types
            return [
                types.Tool(
                    name="synthesizeAndPlay",
                    description="テキストを音声合成して再生します",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "音声合成するテキスト"}
                        },
                        "required": ["message"]
                    }
                )
            ]
        
        # synthesizeAndPlayツールの登録
        @self.call_tool()
        async def synthesizeAndPlay(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            """
            テキストを音声合成して再生します。
            
            Args:
                name: ツール名
                arguments: ツールの引数
            
            Returns:
                処理結果を含む辞書
            """
            from mcp import types
            
            # ツール名のチェック
            if name != "synthesizeAndPlay":
                self.logger.warning(f"Unknown tool: {name}")
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
            message = arguments.get("message", "")
            if not message:
                self.logger.warning("Empty message received")
                return [types.TextContent(type="text", text="Message is empty")]
            
            try:
                await self.synthesize_and_play(message)
                return [types.TextContent(type="text", text="音声合成と再生が完了しました")]
            except Exception as e:
                self.logger.error(f"Error in synthesizeAndPlay: {str(e)}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def synthesize_and_play(self, message: str) -> None:
        """
        テキストを音声合成して再生します。
        
        Args:
            message: 音声合成するテキスト
        """
        self.logger.info(f"Synthesizing message: {message}")
        
        # テキストの前処理
        processed_message = self._preprocess_text(message)
        
        # Audio Queryの取得
        query = self.voicevox_client.audio_query(processed_message)
        
        # 音声合成
        wav_bytes = self.voicevox_client.synthesis(query)
        
        # 音声再生
        await self._play_audio(wav_bytes)
        
        self.logger.info("Audio playback completed")

    def _preprocess_text(self, text: str) -> str:
        """
        テキストを前処理します。
        
        改行がある場合、各行の末尾に「。」を追加します。
        
        Args:
            text: 前処理するテキスト
            
        Returns:
            前処理されたテキスト
        """
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                if not line.endswith('。'):
                    line += '。'
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)

    async def _play_audio(self, wav_bytes: bytes) -> None:
        """
        WAVデータを再生します。
        
        Args:
            wav_bytes: 再生するWAVデータのバイト列
        """
        with BytesIO(wav_bytes) as wav_io:
            with wave.open(wav_io, 'rb') as wav_read:
                wave_obj = sa.WaveObject.from_wave_read(wav_read)
                play_obj = wave_obj.play()   # 非同期再生
                play_obj.wait_done()
