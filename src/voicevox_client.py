"""
voicevox docker版 へのアクセスを提供します

ex.
    from src.voicevox_client import VoicevoxClient
    import io, wave, simpleaudio as sa

    vvc = VoicevoxClient(speaker="8")   # speaker id を`8`を利用する
    query = vvc.audio_query(text=message)   # メッセージデータのみを設定し発音内容に変換
    wav_bytes = vvc.synthesis(query=query)  # wav音声データのバイナリデータを取得
    with io.BytesIO(wav_bytes) as wav_io:
        with wave.open(wav_io, 'rb') as wav_read:
            wave_obj = sa.WaveObject.from_wave_read(wav_read)   # 波形データ変換
            play_obj = wave_obj.play()   # 非同期再生
            # play_obj.wait_done()  # 再生中を待つ場合には有効化
"""

import requests

HOST = "127.0.0.1"
PORT = "50021"
SPEAKER = "3" # Changed from "1" to an available speaker ID (Zundamon Normal)

class VoicevoxClient:

    def __init__(self, host=HOST, port=PORT, speaker=SPEAKER):
        if host is None or len(host) == 0:
            self.host = HOST
        else:
            self.host = host
        if port is None or len(port) == 0:
            self.port = PORT
        else:
            self.port = port
        if speaker is None or len(speaker) == 0:
            self.speaker = SPEAKER
        else:
            self.speaker = speaker

    def audio_query(self, text: str):
        response = requests.post(
            f"http://{self.host}:{self.port}/audio_query",
            params={
                "text": text,
                "speaker": self.speaker,
            }
        )
        return response.json()

    def get_speakers(self):
        """利用可能な話者とそのスタイルを取得します"""
        response = requests.get(
            f"http://{self.host}:{self.port}/speakers"
        )
        response.raise_for_status() # エラーチェック
        return response.json()

    def synthesis(self, query):
        url = f"http://{self.host}:{self.port}/synthesis"
        params = {"speaker": self.speaker}

        # 500になったケースのtryを書く予定
        response = requests.post(
            url,
            params=params,
            json=query
        )
        response.raise_for_status()
        return response.content
