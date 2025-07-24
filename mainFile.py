import os
from dotenv import load_dotenv
from datetime import datetime
import time

from EmoRobots.core.cortex import Cortex
    
class EmotionMetrics:
    def __init__(self):
        # 核心情绪指标
        self.engagement = 0.0      # 专注度 (0-1)
        self.excitement = 0.0      # 兴奋度 (0-1)
        self.stress = 0.0          # 压力水平 (0-1)
        self.relaxation = 0.0      # 放松度 (0-1)
        self.interest = 0.0        # 兴趣度 (0-1)
        self.focus = 0.0           # 集中度 (0-1)
        
        # 设备状态指标
        self.signal_quality = 0    # 信号质量 (1-5, 1=最佳)
        self.battery_level = 0     # 电池电量 (0-100%)
        self.last_update = None    # 最后更新时间
        
    def update_from_met_data(self, met_data):
        """
        从性能指标数据流更新情绪指标
        """
        metrics = met_data['met']
        self.engagement = metrics[0]  # 专注度
        self.excitement = metrics[1]  # 兴奋度
        # longExcitement = metrics[2] # 长期兴奋度 (可选)
        self.stress = metrics[3]      # 压力水平
        self.relaxation = metrics[4]  # 放松度
        self.interest = metrics[5]    # 兴趣度
        self.focus = metrics[6]       # 集中度
        self.last_update = datetime.fromtimestamp(met_data['time'])
        
    def update_from_dev_data(self, dev_data):
        """
        从设备状态数据流更新设备指标
        """
        self.signal_quality = dev_data['signal']  # 信号质量 (1-5)
        self.battery_level = dev_data['batteryPercent']  # 电池百分比
        
    def get_summary(self):
        """
        获取情绪状态摘要
        """
        return {
            "专注状态": f"{self.engagement:.2f} ({'高' if self.engagement > 0.7 else '低'})",
            "压力水平": f"{self.stress:.2f} ({'高' if self.stress > 0.5 else '正常'})",
            "整体情绪": self._get_mood_summary(),
            "信号质量": f"{self.signal_quality}/5",
            "电池电量": f"{self.battery_level}%"
        }
    
    def _get_mood_summary(self):
        """综合情绪分析"""
        if self.excitement > 0.7 and self.stress < 0.3:
            return "积极兴奋"
        elif self.relaxation > 0.6 and self.stress < 0.4:
            return "平静放松"
        elif self.stress > 0.6:
            return "压力状态"
        else:
            return "中性状态"
    def other(self):
        pass
        #补充其他 f:数据->指令
        
        

class EmotionTracker():
    def __init__(self, client_id, client_secret):
        self.emotion_metrics = EmotionMetrics()
        self.cortex = Cortex(client_id, client_secret, debug_mode=False)
        # self.user.do_prepare_steps()
        
         # 绑定事件处理器
        self.cortex.bind(new_met_data=self._on_met_data)
        self.cortex.bind(new_dev_data=self._on_dev_data)
        self.cortex.bind(create_session_done=self._on_connected)
        self.cortex.bind(inform_error=self._on_error)
        
    def start(self):
        """启动情绪追踪"""
        print("启动Emotiv设备连接...")
        self.cortex.open()
        
    def _on_connected(self, *args, **kwargs):
        """会话创建成功回调"""
        session_id = kwargs.get('data')
        print(f"会话已创建: {session_id}")
        # 订阅情绪指标和设备状态流
        self.cortex.sub_request(['met', 'dev'])
        
    def _on_met_data(self, data):
        """处理性能指标数据"""
        print("收到新数据:", data)
        self.emotion_metrics.update_from_met_data(data)
        self.print_summary()
        
    def _on_dev_data(self, data):
        """处理设备状态数据"""
        self.emotion_metrics.update_from_dev_data(data)
        
    def _on_error(self, error_data):
        """错误处理"""
        print(f"API错误: {error_data.get('message', '未知错误')}")
        if error_data.get('code') == -32046:
            print("请检查您的API权限设置")
            
    def print_summary(self):
        print("print_summary called, last_update:", self.emotion_metrics.last_update)
        if self.emotion_metrics.last_update:
            elapsed = (datetime.now() - self.emotion_metrics.last_update).seconds
            print("elapsed:", elapsed)
            if elapsed >= 1:
                print("\n=== 实时情绪指标 ===")
                summary = self.emotion_metrics.get_summary()
                for key, value in summary.items():
                    print(f"{key}: {value}")

    def stop(self):
        """停止追踪并清理资源"""
        self.cortex.unsub_request(['met', 'dev'])
        self.cortex.close_session()
        self.cortex.close()


        

if __name__ == "__main__":
    load_dotenv("emotiv_config.env")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    tracker = EmotionTracker(CLIENT_ID, CLIENT_SECRET)
    
    try:
        tracker.start()
        while True:
            print("主循环运行中，last_update:", tracker.emotion_metrics.last_update)
            time.sleep(10)
    except KeyboardInterrupt:
        tracker.stop()
        print("\n情绪追踪已停止")


# class EmotionMetrics:
#     def __init__(self):
#         #核心数据 情绪
#         self.timestamp = 0.0
#         self.attention_validity = False
#         self.attention = 0.0
#         self.engagement_validity = False
#         self.engagement = 0.0
#         self.excitement_validity = False
#         self.excitement = 0.0
#         self.cognitive_load = 0.0 #lex
#         self.stress_validity = False
#         self.stress = 0.0
#         self.relaxation_validity = False
#         self.relaxation = 0.0
#         self.interest_validity = False
#         self.interest = 0.0
        
#         #设备数据
#         self.AF3 = 0.0
#         self.T7 = 0
#         self.pz = 0
#         self.T8 = 0
#         self.AF4 = 0
#         self.OVERALL = 0
#         self.dev_4 = self.dev_5 = self.dev_6 = self.dev_7 = self.dev_8 = self.dev_9 = 0
#          # 设备状态指标
#         self.signal_quality = 0    # 信号质量 (1-5, 1=最佳)
#         self.battery_level = 0     # 电池电量 (0-100%)
#         self.last_update = None
        
#     def update_from_met_data(self, data):
#         metrics = data['met']
#         self.timestamp = metrics[0]
#         self.attention_validity = metrics[1]
#         self.attention = metrics[2]
#         self.engagement_validity = metrics[3]
#         self.engagement = metrics[4]
#         self.excitement_validity = metrics[5]
#         self.excitement = metrics[6]
#         self.cognitive_load = metrics[7]
#         self.stress_validity = metrics[8]
#         self.stress = metrics[9]
#         self.relaxation_validity = metrics[10]
#         self.relaxation = metrics[11]
#         self.interest_validity = metrics[12]
#         self.interest = metrics[13]
#         self.last_update = datetime.fromtimestamp(self.timestamp)
        
#     def update_from_dev_data(self, dev_data):
#         """
#         从设备状态数据流更新设备指标
#         """
#         self.signal_quality = dev_data['signal']  # 信号质量 (1-5)
#         self.battery_level = dev_data['batteryPercent']  # 电池百分比
