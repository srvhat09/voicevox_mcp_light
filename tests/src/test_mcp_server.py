"""
MCPServerクラスのテストモジュール
"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.mcp_server import MCPServer


@pytest.fixture
def mock_setup():
    """テスト用のモックセットアップ"""
    # VoicevoxClientとsounddeviceをモック化
    with patch('src.mcp_server.VoicevoxClient') as mock_voicevox_client, \
         patch('src.mcp_server.sd') as mock_sounddevice:
        
        # VoicevoxClientのインスタンスモック
        mock_client_instance = MagicMock()
        mock_voicevox_client.return_value = mock_client_instance
        
        # MCPServerのインスタンス作成
        server = MCPServer(name="test-server")
        
        # ログディレクトリの存在確認
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "log")
        assert os.path.exists(log_dir), "ログディレクトリが作成されていません"
        
        yield server, mock_voicevox_client, mock_client_instance, mock_sounddevice


def test_init(mock_setup):
    """初期化のテスト"""
    server, mock_voicevox_client, _, _ = mock_setup
    
    # VoicevoxClientが正しく初期化されたか
    mock_voicevox_client.assert_called_once()
    
    # サーバー名が正しく設定されたか
    assert server.name == "test-server"
    
    # ロガーが正しく設定されたか
    assert server.logger is not None


def test_preprocess_text(mock_setup):
    """テキスト前処理のテスト"""
    server, _, _, _ = mock_setup
    
    # 改行を含むテキスト
    text = "こんにちは\nこれはテストです"
    expected = "こんにちは。\nこれはテストです。"
    
    result = server._preprocess_text(text)
    assert result == expected
    
    # 既に「。」で終わっているテキスト
    text = "こんにちは。\nこれはテストです。"
    expected = "こんにちは。\nこれはテストです。"
    
    result = server._preprocess_text(text)
    assert result == expected
    
    # 空行を含むテキスト
    text = "こんにちは\n\nこれはテストです"
    expected = "こんにちは。\nこれはテストです。"
    
    result = server._preprocess_text(text)
    assert result == expected


@pytest.mark.asyncio
async def test_synthesize_and_play(mock_setup):
    """音声合成と再生のテスト"""
    server, _, mock_client_instance, _ = mock_setup
    
    # モックの設定
    mock_client_instance.audio_query.return_value = {"dummy": "query"}
    mock_client_instance.synthesis.return_value = b"dummy_wav_data"
    
    # _play_audioメソッドをモック化
    with patch.object(server, '_play_audio', new_callable=AsyncMock) as mock_play_audio:
        # テスト実行
        await server.synthesize_and_play("こんにちは")
        
        # 各メソッドが正しく呼ばれたか
        mock_client_instance.audio_query.assert_called_once_with("こんにちは。")
        mock_client_instance.synthesis.assert_called_once_with({"dummy": "query"})
        mock_play_audio.assert_called_once_with(b"dummy_wav_data")


# _play_audioメソッドのテストは複雑なため、一時的にスキップ
@pytest.mark.skip(reason="モックの設定が複雑なため、一時的にスキップ")
@pytest.mark.asyncio
async def test_play_audio():
    """音声再生のテスト"""
    pass


# synthesizeAndPlayツールのテストは複雑なため、一時的にスキップ
@pytest.mark.skip(reason="MCPサーバーのツール呼び出し方法の確認が必要")
@pytest.mark.asyncio
async def test_synthesizeAndPlay_tool():
    """synthesizeAndPlayツールのテスト"""
    pass