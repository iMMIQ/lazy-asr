import os
import uuid
from typing import Dict, Any, Optional
from app.core.config import settings
from app.utils.audio_processing import (
    silero_vad_segmentation, 
    export_silero_segments,
    parse_transcription_segments,
    time_string_to_seconds,
    generate_srt_content
)
from plugins.manager import plugin_manager
from app.models.schemas import ASRResponse


class ASRService:
    """Main ASR service that orchestrates the entire process"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def process_audio(self, audio_path: str, asr_method: str = "faster-whisper",
                           vad_options: Optional[Dict[str, Any]] = None,
                           asr_options: Optional[Dict[str, Any]] = None,
                           asr_api_url: Optional[str] = None,
                           asr_api_key: Optional[str] = None,
                           asr_model: Optional[str] = None) -> ASRResponse:
        """
        Process audio file through the complete ASR pipeline
        
        Args:
            audio_path: Path to the audio file
            asr_method: ASR method to use
            vad_options: VAD options
            asr_options: ASR options
            
        Returns:
            ASRResponse with results
        """
        try:
            print(f"🚀 开始Silero VAD自动分段转录流程")
            print("=" * 60)
            print(f"ASR方法: {asr_method}")
            print(f"输出目录: {self.output_dir}")
            
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                print(f"❌ 音频文件不存在: {audio_path}")
                return ASRResponse(
                    success=False,
                    message="❌ 音频文件不存在"
                )
            
            # 创建任务ID和输出目录
            task_id = str(uuid.uuid4())
            task_output_dir = os.path.join(self.output_dir, task_id)
            os.makedirs(task_output_dir, exist_ok=True)
            
            # 1. Silero VAD检测分段
            try:
                speech_timestamps, audio_data, sample_rate = silero_vad_segmentation(
                    audio_path, vad_options or {}
                )
            except Exception as e:
                print(f"❌ Silero VAD检测失败: {e}")
                return ASRResponse(
                    success=False,
                    message=f"❌ Silero VAD检测失败: {e}"
                )
            
            if not speech_timestamps:
                print("❌ 未检测到任何语音段")
                return ASRResponse(
                    success=False,
                    message="❌ 未检测到任何语音段"
                )
            
            # 2. 导出分段音频
            print(f"\n📁 导出语音段文件...")
            segments_output_dir = os.path.join(task_output_dir, "silero_segments")
            exported_segments = export_silero_segments(
                speech_timestamps, audio_data, sample_rate, segments_output_dir
            )
            
            if not exported_segments:
                print("❌ 没有可导出的语音段")
                return ASRResponse(
                    success=False,
                    message="❌ 没有可导出的语音段"
                )
            
            # 3. 获取ASR插件
            plugin = plugin_manager.get_plugin(asr_method)
            if not plugin:
                print(f"❌ 不支持的ASR方法: {asr_method}")
                return ASRResponse(
                    success=False,
                    message=f"❌ 不支持的ASR方法: {asr_method}"
                )
            
            # 更新插件配置
            plugin_config = {}
            if asr_api_url:
                plugin_config['api_url'] = asr_api_url
            if asr_api_key:
                plugin_config['api_key'] = asr_api_key
            if asr_model:
                plugin_config['model'] = asr_model
            
            if plugin_config:
                plugin.update_config(plugin_config)
                print(f"🔧 更新插件配置: {plugin_config}")
            
            # 4. 并发转录
            print(f"\n🎯 开始并发转录...")
            all_subtitles = []
            successful_transcriptions = 0
            failed_segments = 0
            empty_segments = 0
            
            # 使用插件并发转录所有段
            transcription_results = await plugin.transcribe_segments(exported_segments)
            
            for i, result in enumerate(transcription_results):
                segment_info = exported_segments[i]
                print(f"\n[{i+1}/{len(exported_segments)}] 处理语音段:")
                print(f"   文件: {os.path.basename(segment_info['file_path'])}")
                print(f"   时间: {segment_info['start_time']:.2f}s - {segment_info['end_time']:.2f}s")
                print(f"   时长: {segment_info['duration']:.2f}s")
                
                if not result['success']:
                    # 转录失败，跳过此段
                    print(f"   ❌ 转录失败，跳过此段")
                    failed_segments += 1
                    continue
                
                transcription = result['transcription']
                if transcription is None:
                    # 转录无内容，跳过此段
                    print(f"   ⚠️ 转录无内容，跳过此段")
                    empty_segments += 1
                    continue
                
                # 解析转录结果
                adjusted_subtitles = parse_transcription_segments(
                    transcription, 
                    segment_info['start_time'], 
                    segment_info['end_time']
                )
                
                if adjusted_subtitles:
                    all_subtitles.extend(adjusted_subtitles)
                    successful_transcriptions += 1
                    print(f"   ✅ 成功添加 {len(adjusted_subtitles)} 条字幕")
                    
                    # 显示第一条字幕预览
                    if adjusted_subtitles:
                        first_sub = adjusted_subtitles[0]
                        preview_text = first_sub['text'][:50] + "..." if len(first_sub['text']) > 50 else first_sub['text']
                        print(f"   预览: {preview_text}")
                else:
                    print(f"   ⚠️ 转录无内容，跳过此段")
                    empty_segments += 1
            
            # 5. 生成SRT文件
            if all_subtitles:
                # 按时间排序字幕
                all_subtitles.sort(key=lambda x: time_string_to_seconds(x['start'].replace(',', '.')))
                
                srt_content = generate_srt_content(all_subtitles)
                
                base_name = os.path.splitext(os.path.basename(audio_path))[0]
                output_srt_path = os.path.join(task_output_dir, f"{base_name}_silero_subtitles.srt")
                
                with open(output_srt_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                
                # 生成统计信息
                stats = {
                    "total_segments": len(exported_segments),
                    "successful_transcriptions": successful_transcriptions,
                    "failed_segments": failed_segments,
                    "empty_segments": empty_segments,
                    "total_subtitles": len(all_subtitles)
                }
                
                print(f"\n✅ 处理完成!")
                print(f"💾 SRT文件已保存: {output_srt_path}")
                print(f"📊 统计信息:")
                print(f"   总语音段数: {len(exported_segments)}")
                print(f"   成功转录段数: {successful_transcriptions}")
                print(f"   失败段数: {failed_segments}")
                print(f"   无内容段数: {empty_segments}")
                print(f"   总字幕数: {len(all_subtitles)}")
                
                # 预览前几条字幕
                preview_text = "🎯 字幕预览:\n" + "=" * 50 + "\n"
                for i, subtitle in enumerate(all_subtitles[:5]):
                    preview_text += f"{i+1}\n"
                    preview_text += f"{subtitle['start']} --> {subtitle['end']}\n"
                    preview_text += f"{subtitle['text']}\n\n"
                
                return ASRResponse(
                    success=True,
                    message=f"✅ 处理完成! SRT文件已保存: {output_srt_path}",
                    srt_file_path=output_srt_path,
                    segments=[s for s in all_subtitles[:10]],  # 只返回前10条字幕
                    stats=stats
                )
            else:
                error_msg = "❌ 没有生成任何字幕"
                print(error_msg)
                return ASRResponse(
                    success=False,
                    message=error_msg
                )
                
        except Exception as e:
            print(f"❌ 处理过程中发生错误: {e}")
            return ASRResponse(
                success=False,
                message=f"❌ 处理过程中发生错误: {e}"
            )
