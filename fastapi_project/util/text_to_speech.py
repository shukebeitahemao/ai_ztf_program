"""
阿里云CosyVoice文本转语音服务
"""
import os
import base64
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

logger = logging.getLogger(__name__)

class AlibabaCloudTextToSpeech:
    def __init__(self):
        """初始化阿里云CosyVoice文本转语音客户端"""
        # 从.env文件获取阿里云DashScope API Key
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        
        if not self.api_key:
            logger.warning("阿里云DashScope API Key未配置，请在.env文件中设置 DASHSCOPE_API_KEY")
            logger.warning("将使用模拟语音合成")
            self.client = None
        else:
            try:
                # 导入DashScope SDK
                import dashscope
                from dashscope.audio.tts_v2 import SpeechSynthesizer
                
                # 设置API Key
                dashscope.api_key = self.api_key
                self.dashscope = dashscope
                # 初始化 SpeechSynthesizer 实例，设置模型和音色
                self.speech_synthesizer = SpeechSynthesizer(
                    model='cosyvoice-v1',  # 使用 v1 模型
                    voice='longfei'  # 默认音色
                )
                logger.info("阿里云CosyVoice文本转语音客户端初始化成功")
                self.client = True
            except ImportError as e:
                logger.warning(f"DashScope SDK未安装，使用模拟语音合成: {e}")
                self.client = None
            except Exception as e:
                logger.error(f"CosyVoice客户端初始化失败: {e}")
                self.client = None
    
    def text_to_speech(self, text: str, voice: str = "longwan") -> Optional[Tuple[str, float]]:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            voice: 声音类型，默认为"longwan"
            
        Returns:
            Tuple[base64编码的音频数据, 预估播放时长(秒)] 或 None
        """
        if not self.client:
            # 使用模拟语音合成
            return self._mock_text_to_speech(text)
            
        try:
            # 检查文本长度
            if len(text) > 2000:
                logger.warning(f"文本长度超过限制，将截断到2000字符。原长度: {len(text)}")
                text = text[:2000]
            
            # 调用CosyVoice API
            try:
                # 直接调用，返回二进制音频数据
                audio_data = self.speech_synthesizer.call(text)
                
                if audio_data is not None:
                    # 转换为base64编码
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    # 估算播放时长
                    duration = self._estimate_duration(text)
                    
                    logger.info(f"语音合成成功，文本长度: {len(text)}, 预估时长: {duration}秒")
                    return audio_base64, duration
                else:
                    logger.error("语音合成失败：无法获取音频数据")
                    return self._mock_text_to_speech(text)
            except Exception as api_error:
                logger.error(f"CosyVoice API调用失败: {api_error}")
                return self._mock_text_to_speech(text)
                
        except Exception as e:
            logger.error(f"语音合成异常: {str(e)}")
            return self._mock_text_to_speech(text)
    
    def _estimate_duration(self, text: str) -> float:
        """
        估算文本的语音播放时长
        """
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len([w for w in text.split() if w.isalpha()])
        other_chars = len(text) - chinese_chars - sum(len(w) for w in text.split() if w.isalpha())
        
        # 估算时长：中文字符0.5秒/字，英文单词0.3秒/词，其他字符0.1秒/字符
        duration = chinese_chars * 0.5 + english_words * 0.3 + other_chars * 0.1
        
        # 最小时长1秒
        return max(duration, 1.0)
    
    def _mock_text_to_speech(self, text: str) -> Tuple[str, float]:
        """
        模拟语音合成
        生成一个有效的静音音频文件
        """
        duration = self._estimate_duration(text)
        
        # 生成一个有效的静音WAV文件
        mock_audio_base64 = self._generate_silent_audio(duration)
        
        logger.info(f"模拟语音合成，文本长度: {len(text)}, 预估时长: {duration}秒")
        return mock_audio_base64, duration
    
    def _generate_silent_audio(self, duration: float) -> str:
        """
        生成指定时长的静音音频文件（WAV格式）
        """
        try:
            import struct
            import io
            
            # 音频参数
            sample_rate = 44100
            channels = 1
            bits_per_sample = 16
            
            # 计算样本数
            num_samples = int(sample_rate * duration)
            
            # 创建静音数据
            audio_data = b'\x00\x00' * num_samples  # 16位静音数据
            
            # 构建WAV文件头
            wav_header = struct.pack('<4sI4s', b'RIFF', 36 + len(audio_data), b'WAVE')
            fmt_chunk = struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, channels, sample_rate, 
                                  sample_rate * channels * bits_per_sample // 8, 
                                  channels * bits_per_sample // 8, bits_per_sample)
            data_chunk = struct.pack('<4sI', b'data', len(audio_data))
            
            # 组合完整的WAV文件
            wav_file = wav_header + fmt_chunk + data_chunk + audio_data
            
            # 转换为base64
            return base64.b64encode(wav_file).decode('utf-8')
            
        except Exception as e:
            logger.error(f"生成静音音频失败: {e}")
            # 返回null，前端会跳过音频播放
            return ""


# 创建全局实例
tts_service = AlibabaCloudTextToSpeech()


def synthesize_text(text: str, voice: str = "longwan") -> Optional[Tuple[str, float]]:
    """
    文本转语音的便捷函数
    
    Args:
        text: 要转换的文本
        voice: 声音类型
        
    Returns:
        Tuple[base64编码的音频数据, 预估播放时长(秒)] 或 None
    """
    return tts_service.text_to_speech(text, voice) 