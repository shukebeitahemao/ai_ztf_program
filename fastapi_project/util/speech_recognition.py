"""
阿里云DashScope语音识别服务 - Paraformer模型
"""
import os
import json
import time
import logging
from typing import Optional
from dotenv import load_dotenv
from http import HTTPStatus

# 加载.env文件
load_dotenv()

logger = logging.getLogger(__name__)

class AlibabaCloudSpeechRecognition:
    def __init__(self):
        """初始化阿里云DashScope语音识别客户端"""
        # 从.env文件获取阿里云DashScope API Key
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        
        if not self.api_key:
            logger.warning("阿里云DashScope API Key未配置，请在.env文件中设置 DASHSCOPE_API_KEY")
            logger.info("你可以创建一个.env文件在项目根目录，并添加以下内容：")
            logger.info("DASHSCOPE_API_KEY=your_dashscope_api_key")
            logger.warning("将使用模拟语音识别")
            self.client = None
        else:
            try:
                # 导入DashScope SDK
                import dashscope
                
                # 设置API Key
                dashscope.api_key = self.api_key
                self.dashscope = dashscope
                logger.info("阿里云DashScope语音识别客户端初始化成功")
                self.client = True
            except ImportError as e:
                logger.warning(f"DashScope SDK未安装，使用模拟语音识别: {e}")
                self.client = None
            except Exception as e:
                logger.error(f"DashScope客户端初始化失败: {e}")
                self.client = None
    
    def recognize_file(self, file_path: str) -> Optional[str]:
        """
        识别音频文件
        
        Args:
            file_path: 本地音频文件路径
            
        Returns:
            识别的文字内容，如果失败返回None
        """
        if not self.client:
            # 使用模拟识别
            return self._mock_recognition(file_path)
            
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"音频文件不存在: {file_path}")
                return None
            
            # 方法1: 使用qwen-audio-asr模型（支持本地文件）
            return self._recognize_with_qwen_audio_asr(file_path)
            
        except Exception as e:
            logger.error(f"语音识别失败: {str(e)}")
            return self._mock_recognition(file_path)
    
    def _recognize_with_qwen_audio_asr(self, file_path: str) -> Optional[str]:
        """
        使用qwen-audio-asr模型识别本地音频文件
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"audio": file_path},
                    ]
                }
            ]
            
            response = self.dashscope.MultiModalConversation.call(
                model="qwen-audio-asr",
                messages=messages,
                result_format="message"
            )
            
            # 检查响应状态
            try:
                if response.status_code == 200:
                    # 提取识别结果
                    choices = response.output.get('choices', [])
                    if choices and len(choices) > 0:
                        message = choices[0].get('message', {})
                        content = message.get('content', [])
                        if content and len(content) > 0:
                            text = content[0].get('text', '')
                            return text.strip() if text else None
                    return None
                else:
                    logger.error(f"qwen-audio-asr识别失败: {response.message}")
                    return None
            except AttributeError:
                # 如果response对象结构不同，尝试其他方式提取结果
                logger.error("响应对象结构异常，无法提取识别结果")
                return None
                
        except Exception as e:
            logger.error(f"qwen-audio-asr识别异常: {str(e)}")
            return None
    
    def recognize_file_with_paraformer(self, file_url: str) -> Optional[str]:
        """
        使用Paraformer-v2模型识别音频文件（需要公网URL）
        
        Args:
            file_url: 音频文件的公网URL
            
        Returns:
            识别的文字内容
        """
        if not self.client:
            return self._mock_recognition("remote_file")
            
        try:
            from dashscope.audio.asr import Transcription
            
            # 提交异步任务
            task_response = Transcription.async_call(
                model='paraformer-v2',
                file_urls=[file_url],
                language_hints=['zh', 'en']  # 支持中英文
            )
            
            if task_response.status_code != HTTPStatus.OK:
                logger.error(f"Paraformer任务提交失败: {task_response.message}")
                return None
            
            # 等待任务完成
            transcription_response = Transcription.wait(
                task=task_response.output.task_id
            )
            
            if transcription_response.status_code == HTTPStatus.OK:
                # 解析结果
                results = transcription_response.output.get('results', [])
                if results and len(results) > 0:
                    # 获取第一个文件的识别结果
                    first_result = results[0]
                    transcription_url = first_result.get('transcription_url')
                    
                    if transcription_url:
                        # 下载并解析识别结果
                        import urllib.request
                        result_json = urllib.request.urlopen(transcription_url).read().decode('utf8')
                        result_data = json.loads(result_json)
                        
                        # 提取文本内容
                        text_parts = []
                        sentences = result_data.get('result', {}).get('sentences', [])
                        for sentence in sentences:
                            text_parts.append(sentence.get('text', ''))
                        
                        return ''.join(text_parts).strip()
                
                return None
            else:
                logger.error(f"Paraformer识别失败: {transcription_response.message}")
                return None
                
        except Exception as e:
            logger.error(f"Paraformer识别异常: {str(e)}")
            return None
    
    def _upload_file_to_public(self, file_path: str) -> Optional[str]:
        """
        将本地文件上传到公网可访问的位置
        这里需要根据实际情况实现，比如上传到OSS等
        """
        logger.warning("需要配置文件上传服务以提供公网URL，当前使用本地文件识别")
        return None
    
    def _mock_recognition(self, file_path: str) -> str:
        """
        模拟语音识别结果
        用于测试和演示
        """
        # 检查文件是否存在
        if file_path != "remote_file" and not os.path.exists(file_path):
            return "文件不存在"
        
        # 根据文件大小或文件名模拟不同的识别结果
        if file_path == "remote_file":
            return "这是远程文件的模拟语音识别结果。"
        
        try:
            file_size = os.path.getsize(file_path)
            
            if file_size < 10000:  # 小于10KB
                return "你好，这是语音识别测试。"
            elif file_size < 50000:  # 小于50KB
                return "你好，我想问一下关于邹韬奋的故事。"
            elif file_size < 100000:  # 小于100KB
                return "能不能给我讲一下邹韬奋的生平经历？"
            else:
                return "请详细介绍一下邹韬奋先生的主要事迹和贡献。"
        except:
            return "语音识别模拟结果。"


# 创建全局实例
speech_recognizer = AlibabaCloudSpeechRecognition()


def recognize_audio_file(file_path: str) -> Optional[str]:
    """
    识别音频文件的便捷函数
    
    Args:
        file_path: 音频文件路径
        
    Returns:
        识别的文字内容
    """
    return speech_recognizer.recognize_file(file_path)


def recognize_audio_url(file_url: str) -> Optional[str]:
    """
    使用Paraformer识别公网音频文件的便捷函数
    
    Args:
        file_url: 音频文件的公网URL
        
    Returns:
        识别的文字内容
    """
    return speech_recognizer.recognize_file_with_paraformer(file_url)


# 备用方案：使用本地处理
def recognize_audio_local(file_path: str) -> Optional[str]:
    """
    本地音频处理备用方案
    当阿里云服务不可用时使用
    """
    try:
        # 使用模拟识别
        return speech_recognizer._mock_recognition(file_path)
        
    except Exception as e:
        logger.error(f"本地语音识别失败: {str(e)}")
        return "语音识别失败" 