import random
import time

import edge_tts
import threading
from playsound import playsound
import os
import sounddevice as sd
import soundfile as sf
import asyncio

# 代理设置
PROXY = "http://192.168.10.66:10707"
use_proxy = False

MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 1  # 每次重试之间的延迟（秒）

def synchronous_text_to_speech(v_num, text, output_path):
    """
    使用 edge_tts 进行同步文本转语音的实现。
    """
    voices = [
        "zh-CN-XiaoxiaoNeural",
        "zh-CN-XiaoyiNeural",
        "zh-CN-YunjianNeural",
        "zh-CN-YunxiNeural",
        "zh-CN-YunxiaNeural",
        "zh-CN-YunyangNeural"
    ]
    voice = voices[v_num]  # 固定选择声音

    for attempt in range(MAX_RETRIES):
        try:
            # 创建一个事件循环用于运行 edge_tts 的异步调用
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tts = edge_tts.Communicate(text, voice, proxy=PROXY if use_proxy else None)
            loop.run_until_complete(tts.save(output_path))
            loop.close()

            if os.path.exists(output_path):
                return  # 成功生成音频文件，退出重试
            else:
                raise FileNotFoundError(f"生成失败: {output_path}")
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {e}")
            if attempt < MAX_RETRIES - 1:  # 如果不是最后一次重试
                print(f"等待 {RETRY_DELAY} 秒后重试...")
                threading.Event().wait(RETRY_DELAY)
            else:
                raise  # 达到最大重试次数，抛出异常

def play_speech_thread(text, output_mp3, v_num):
    try:
        os.makedirs(os.path.dirname(output_mp3), exist_ok=True)
        synchronous_text_to_speech(v_num, text, output_mp3)
        play_audio_with_playsound(output_mp3)
        print(f"语音已生成并播放：{output_mp3}")
    except Exception as e:
        print(f"播放时发生错误: {e}")
    finally:
        try:
            os.remove(output_mp3)
        except OSError as e:
            print(f"删除文件时出错: {e}")

def play_audio_with_playsound(wav_file):
    play_audio(wav_file)

def list_audio_devices():
    """列出所有音频设备"""
    devices = sd.query_devices()
    print("可用音频设备列表:")
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")

def play_audio(wav_file, device_id=42):
    """播放音频文件"""
    try:
        data, samplerate = sf.read(wav_file)
        sd.play(data, samplerate, device=device_id)
        sd.wait()  # 等待播放结束
    except Exception as e:
        print(f"播放音频时出错: {e}")

if __name__ == '__main__':
    txt = "你好，欢迎使用文本转语音系统！"
    output_file = "msic/output.mp3"
    threading.Thread(target=play_speech_thread, args=(txt, output_file)).start()
