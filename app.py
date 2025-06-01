# app.py - LLM100人に聞きました GPT-4o-mini版（PDF出力対応完全版）
# Part 1: ライブラリインポートとクラス定義
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import json
import asyncio
import time
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import re
from collections import Counter

# オプショナルインポート
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # バックエンドを設定
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ページ設定
st.set_page_config(
    page_title="LLM100人に聞きました - PDF出力対応版",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class PersonaProfile:
    id: int
    age: int
    gender: str
    prefecture: str
    occupation: str
    education: str
    income_level: str
    family_status: str
    political_leaning: str
    urban_rural: str
    generation: str

class JapanDemographicsDB:
    def __init__(self):
        self.setup_demographics_data()
    
    def setup_demographics_data(self):
        self.age_distribution = {
            (0, 14): 11.2, (15, 24): 9.8, (25, 34): 12.1, (35, 44): 14.2,
            (45, 54): 13.8, (55, 64): 13.9, (65, 74): 12.5, (75, 100): 16.8
        }
        
        self.prefecture_distribution = {
            '東京都': 11.4, '神奈川県': 7.5, '大阪府': 7.1, '愛知県': 6.1,
            '埼玉県': 5.9, '千葉県': 5.1, '兵庫県': 4.4, '北海道': 4.2,
            '福岡県': 4.1, '静岡県': 3.0, 'その他': 40.7
        }
        
        self.occupation_distribution = {
            '会社員（事務系）': 23.1, '会社員（技術系）': 15.8, 'サービス業': 12.6,
            '営業・販売': 11.0, '製造業': 13.9, '建設業': 6.7, '公務員': 3.2,
            '自営業': 8.5, '学生': 4.2, '無職・年金': 12.8, 'その他': 14.7
        }
        
        self.education_distribution = {
            '中学校卒業': 8.2, '高校卒業': 35.4, '専門学校卒業': 18.7,
            '短大卒業': 9.1, '大学卒業': 24.8, '大学院卒業': 3.8
        }
        
        self.income_distribution = {
            '200万円未満': 15.3, '200-300万円': 18.7, '300-400万円': 16.9,
            '400-500万円': 14.2, '500-600万円': 11.8, '600-800万円': 12.4,
            '800-1000万円': 6.8, '1000万円以上': 3.9
        }
        
        self.family_status_distribution = {
            '単身': 28.8, '夫婦のみ': 20.3, '二世代家族': 29.5,
            '三世代家族': 8.7, 'ひとり親': 7.2, 'その他': 5.5
        }
        
        self.political_base = {
            '保守': 35.2, '中道': 42.1, 'リベラル': 15.8, '無関心': 6.9
        }

class PersonaGenerator:
    def __init__(self, demographics_db: JapanDemographicsDB):
        self.db = demographics_db
        
    def generate_weighted_choice(self, distribution: Dict[str, float]) -> str:
        choices = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(choices, weights=weights)[0]
    
    def get_generation_label(self, age: int) -> str:
        if age <= 24:
            return 'Z世代'
        elif age <= 39:
            return 'ミレニアル世代'
        elif age <= 54:
            return 'X世代'
        elif age <= 64:
            return 'バブル世代'
        else:
            return '団塊・シニア世代'
    
    def adjust_by_demographics(self, base_persona: PersonaProfile) -> PersonaProfile:
        if base_persona.age <= 29:
            political_choices = ['保守', '中道', 'リベラル', '無関心']
            political_weights = [25.0, 35.0, 20.0, 20.0]
        elif base_persona.age >= 65:
            political_choices = ['保守', '中道', 'リベラル', '無関心']
            political_weights = [50.0, 35.0, 12.0, 3.0]
        else:
            political_choices = list(self.db.political_base.keys())
            political_weights = list(self.db.political_base.values())
        
        base_persona.political_leaning = random.choices(political_choices, weights=political_weights)[0]
        
        urban_prefectures = ['東京都', '神奈川県', '大阪府', '愛知県', '埼玉県', '千葉県']
        base_persona.urban_rural = '都市部' if base_persona.prefecture in urban_prefectures else '地方'
        
        return base_persona
    
    def generate_persona(self, persona_id: int) -> PersonaProfile:
        age_ranges = list(self.db.age_distribution.keys())
        age_weights = list(self.db.age_distribution.values())
        selected_range = random.choices(age_ranges, weights=age_weights)[0]
        age = random.randint(selected_range[0], selected_range[1])
        
        # 20歳以下は学生に固定
        if age <= 20:
            occupation = '学生'
        else:
            occupation = self.generate_weighted_choice(self.db.occupation_distribution)
        
        persona = PersonaProfile(
            id=persona_id,
            age=age,
            gender=random.choice(['男性', '女性']),
            prefecture=self.generate_weighted_choice(self.db.prefecture_distribution),
            occupation=occupation,
            education=self.generate_weighted_choice(self.db.education_distribution),
            income_level=self.generate_weighted_choice(self.db.income_distribution),
            family_status=self.generate_weighted_choice(self.db.family_status_distribution),
            political_leaning='',
            urban_rural='',
            generation=self.get_generation_label(age)
        )
        
        return self.adjust_by_demographics(persona)

class WebSearchProvider:
    def __init__(self):
        pass
        
    def search_recent_info(self, query: str, num_results: int = 10) -> List[Dict]:
        if DDGS_AVAILABLE:
            try:
                ddgs = DDGS()
                search_results = []
                
                results = ddgs.text(
                    keywords=f"{query} 日本 2025",
                    region='jp-jp',
                    max_results=num_results
                )
                
                for result in results:
                    search_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('body', '')[:200] + '...',
                        'url': result.get('href', ''),
                        'date': '2025年最新'
                    })
                
                return search_results if search_results else self._get_demo_results(query, num_results)
                
            except Exception as e:
                st.warning(f"検索エラー: {e}")
                return self._get_demo_results(query, num_results)
        else:
            return self._get_demo_results(query, num_results)
    
    def _get_demo_results(self, query: str, num_results: int = 10) -> List[Dict]:
        demo_results = []
        for i in range(min(num_results, 5)):  # デモは最大5件
            demo_results.append({
                'title': f'{query}に関する最新情報 {i+1}',
                'snippet': f'{query}について、政府や専門家が新しい見解を示しています。市民の関心も高まっており、様々な議論が展開されています。',
                'url': f'https://example{i+1}.com',
                'date': '2025年最新'
            })
        return demo_results

class CostTracker:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.gpt4o_mini_input_cost = 0.00015
        self.gpt4o_mini_output_cost = 0.0006
        self.requests_count = 0
        
    def add_usage(self, input_tokens: int, output_tokens: int):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.requests_count += 1
    
    def get_total_cost(self) -> float:
        input_cost = (self.total_input_tokens / 1000) * self.gpt4o_mini_input_cost
        output_cost = (self.total_output_tokens / 1000) * self.gpt4o_mini_output_cost
        return input_cost + output_cost
    
    def get_cost_summary(self) -> Dict:
        total_cost_usd = self.get_total_cost()
        return {
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'requests_count': self.requests_count,
            'total_cost_usd': total_cost_usd,
            'total_cost_jpy': total_cost_usd * 150,
        }

class EnhancedPromptGenerator:
    def __init__(self):
        if OPENAI_AVAILABLE and TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")
            except:
                self.encoding = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoding = None
    
    def create_detailed_persona_prompt(self, persona: Dict, question: str, context_info: str = "") -> str:
        context_section = f"\n【参考情報】\n{context_info}\n" if context_info else ""
        
        prompt = f"""【プロフィール】
{persona['age']}歳、{persona['gender']}、{persona['prefecture']}在住
職業：{persona['occupation']} / 世代：{persona['generation']}
政治的傾向：{persona['political_leaning']} / 居住環境：{persona['urban_rural']}
{context_section}
【質問】{question}

【回答指示】
上記のプロフィールに基づいて、100文字以内で簡潔に回答してください。
- その年代・職業らしい語調で
- 100文字を絶対に超えない
"""
        return prompt
    
    def create_search_summary_prompt(self, search_results: List[Dict], question: str) -> str:
        """検索結果要約用プロンプト"""
        search_content = "\n".join([
            f"【記事{i+1}】{result['title']}\n{result['snippet']}"
            for i, result in enumerate(search_results[:10])
        ])
        
        prompt = f"""【質問】{question}

【検索結果】
{search_content}

【要約指示】
上記の検索結果を300文字以内で要約してください：
1. {question}に関する最新の動向
2. 主要な論点や議論
3. 政府・専門家の見解
4. 市民の反応や世論

簡潔で分かりやすい要約を作成してください。
"""
        return prompt
    
    def create_analysis_prompt(self, responses: List[str], question: str) -> str:
        all_responses = "\n".join([f"{i+1}: {resp}" for i, resp in enumerate(responses)])
        
        prompt = f"""【質問】{question}

【回答】
{all_responses}

【分析指示】
2400文字以内で以下を詳細かつ創造的に分析してください：

1. **主要論点の整理**（500文字程度）
   - 回答に現れた主要な論点を3-7個に整理
   - 各論点の支持状況、特徴、背景要因
   - 論点間の相互関係や対立構造

2. **世代間・立場間の対立軸**（500文字程度）
   - 明確な意見の対立がある論点の詳細分析
   - 世代、職業、地域による意見の違いとその背景
   - 価値観の根本的な違いとその社会的意味

3. **感情的傾向と心理的背景**（400文字程度）
   - ポジティブ・ネガティブ・中立の詳細分析
   - 不安、期待、諦め、希望などの具体的感情
   - 感情の背景にある社会状況や個人体験

4. **重要キーワードと文脈的意味**（400文字程度）
   - 頻出する重要キーワードとその深層的意味
   - 特徴的な表現や隠喩の社会的背景
   - 言葉に込められた潜在的メッセージ

5. **社会的ダイナミクスと変化の兆し**（300文字程度）
   - 回答から読み取れる社会の動的変化
   - 新しい価値観や思考パターンの萌芽
   - 従来の枠組みでは捉えきれない現象

6. **政策提言と社会設計への示唆**（300文字程度）
   - 回答から導かれる具体的な政策提言
   - 社会制度設計への創造的アイデア
   - 未来の社会像への建設的ビジョン

創造的で洞察に富む分析を2400文字で作成してください。固定観念にとらわれず、新しい視点や発見を重視してください。
"""
        return prompt
    
    def count_tokens(self, text: str) -> int:
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            return len(text) // 3



class GPT4OMiniProvider:
    def __init__(self, api_key: str):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAIライブラリが必要です")
            
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.prompt_generator = EnhancedPromptGenerator()
        self.cost_tracker = CostTracker()
        
    async def generate_response(self, persona: Dict, question: str, context_info: str = "") -> Dict:
        prompt = self.prompt_generator.create_detailed_persona_prompt(persona, question, context_info)
        input_tokens = self.prompt_generator.count_tokens(prompt)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.9,
                timeout=45
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # 100文字制限を強制
            if len(response_text) > 100:
                response_text = response_text[:97] + "..."
            
            output_tokens = self.prompt_generator.count_tokens(response_text)
            self.cost_tracker.add_usage(input_tokens, output_tokens)
            
            return {
                'success': True,
                'response': response_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost_usd': (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000
            }
            
        except Exception as e:
            self.cost_tracker.add_usage(input_tokens, 0)
            
            return {
                'success': False,
                'response': f"APIエラー: {str(e)[:50]}...",
                'input_tokens': input_tokens,
                'output_tokens': 0,
                'cost_usd': input_tokens * 0.00015 / 1000,
                'error': str(e)
            }
    
    async def summarize_search_results(self, search_results: List[Dict], question: str) -> Dict:
        """検索結果を要約"""
        prompt = self.prompt_generator.create_search_summary_prompt(search_results, question)
        input_tokens = self.prompt_generator.count_tokens(prompt)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3,
                timeout=45
            )
            
            summary_text = response.choices[0].message.content.strip()
            
            # 300文字制限を強制
            if len(summary_text) > 300:
                summary_text = summary_text[:297] + "..."
            
            output_tokens = self.prompt_generator.count_tokens(summary_text)
            self.cost_tracker.add_usage(input_tokens, output_tokens)
            
            return {
                'success': True,
                'summary': summary_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost_usd': (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000
            }
            
        except Exception as e:
            self.cost_tracker.add_usage(input_tokens, 0)
            
            return {
                'success': False,
                'summary': f"要約エラー: {str(e)[:50]}...",
                'input_tokens': input_tokens,
                'output_tokens': 0,
                'cost_usd': input_tokens * 0.00015 / 1000,
                'error': str(e)
            }
    
    async def analyze_responses(self, responses: List[str], question: str) -> Dict:
        prompt = self.prompt_generator.create_analysis_prompt(responses, question)
        input_tokens = self.prompt_generator.count_tokens(prompt)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.3,
                timeout=60
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # 2400文字制限を強制
            if len(analysis_text) > 3600:
                analysis_text = analysis_text[:3597] + "..."
            
            output_tokens = self.prompt_generator.count_tokens(analysis_text)
            self.cost_tracker.add_usage(input_tokens, output_tokens)
            
            return {
                'success': True,
                'analysis': analysis_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost_usd': (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000
            }
            
        except Exception as e:
            self.cost_tracker.add_usage(input_tokens, 0)
            
            return {
                'success': False,
                'analysis': f"分析エラー: {str(e)[:50]}...",
                'input_tokens': input_tokens,
                'output_tokens': 0,
                'cost_usd': input_tokens * 0.00015 / 1000,
                'error': str(e)
            }

class ResponseAnalyzer:
    def __init__(self):
        self.stop_words = {'の', 'は', 'が', 'を', 'に', 'で', 'と', 'から', 'も'}
    
    def extract_keywords(self, responses: List[str]) -> List[Dict]:
        all_text = ' '.join(responses)
        words = re.findall(r'[ぁ-ゟ]+|[ァ-ヿ]+|[一-龯]+', all_text)
        filtered_words = [word for word in words if len(word) > 1 and word not in self.stop_words]
        word_freq = Counter(filtered_words)
        return [{'word': word, 'count': count} for word, count in word_freq.most_common(15)]
    
    def analyze_sentiment(self, responses: List[str]) -> Dict:
        positive_words = ['良い', '期待', '希望', '賛成', '支持']
        negative_words = ['悪い', '不安', '心配', '反対', '問題']
        
        positive_count = negative_count = neutral_count = 0
        
        for response in responses:
            pos_score = sum(response.count(word) for word in positive_words)
            neg_score = sum(response.count(word) for word in negative_words)
            
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(responses)
        return {
            'positive': positive_count / total * 100,
            'negative': negative_count / total * 100,
            'neutral': neutral_count / total * 100
        }

class SimulationProvider:
    def __init__(self):
        self.cost_tracker = CostTracker()
        
        self.response_patterns = {
            'Z世代': {
                'positive': [
                    "SNSで見てるけど、これは必要な変化だと思う。私たちの世代が未来を作らないと。",
                    "環境を考えると、新しいアプローチが必要。友達も関心持ってる。",
                    "デジタル化で効率的に解決できそう。年上とは違う視点で考えたい。"
                ],
                'negative': [
                    "正直、将来が不安で今の状況では難しい。就職も心配だし、経済的に厳しい。",
                    "理想論は分かるけど、現実的に考えると厳しい。若い世代の声を聞いて。",
                    "大人が決めた影響を受けるのは私たちなのに、意見を聞かれない。"
                ],
                'neutral': [
                    "よく分からないけど、情報を集めて考えてみたい。まだ勉強不足かも。",
                    "色々な意見があって迷う。もう少し時間をかけて考える必要がある。"
                ]
            },
            'ミレニアル世代': {
                'positive': [
                    "子どもの将来を考えると必要だと思う。働きながらでも参加できると良い。",
                    "現実的で実現可能なら支持したい。家計への影響も考慮してほしい。",
                    "職場の経験を活かして、建設的な意見を出していきたい。"
                ],
                'negative': [
                    "育児と仕事で忙しく、これ以上負担が増えるのは困る。現実的な解決策が必要。",
                    "理想は分かるが、実際の生活への影響を考えると反対せざるを得ない。",
                    "中間世代として上下の意見を聞いているが、なかなか難しい問題。"
                ],
                'neutral': [
                    "メリット・デメリットを慎重に検討したい。子どもへの影響も含めて判断。",
                    "職場でも議論になっているが、まだ結論は出ていない。情報がほしい。"
                ]
            },
            'X世代': {
                'positive': [
                    "長期的な視点で考えると、今行動することが重要だと思う。経験も活かしたい。",
                    "これまでの社会変化を見てきた立場として、慎重だが前向きに検討したい。"
                ],
                'negative': [
                    "現実的な課題を考えると、簡単ではない。もっと具体的な検討が必要。",
                    "理想と現実のギャップが大きすぎる。段階的なアプローチが必要。"
                ],
                'neutral': [
                    "様々な立場の意見を聞いて、バランスの取れた判断をしたい。",
                    "慎重に検討する必要がある。急いで決めるべきではない。"
                ]
            },
            'バブル世代': {
                'positive': [
                    "これまでの経験を活かして、建設的な提案をしていきたい。",
                    "安定した方向性を保ちながら、必要な変化には対応すべき。"
                ],
                'negative': [
                    "拙速な変化よりも、慎重な検討が必要。リスクを十分考慮すべき。",
                    "これまでの制度との整合性を考えると、課題が多い。"
                ],
                'neutral': [
                    "長期的な影響を慎重に検討したい。次世代への配慮も重要。",
                    "安定性と革新性のバランスを取ることが大切。"
                ]
            },
            '団塊・シニア世代': {
                'positive': [
                    "次世代のために、今できることはやっておきたい。経験を活かして貢献したい。",
                    "長い人生経験から言うと、時代に合わせた変化は必要だと思う。"
                ],
                'negative': [
                    "急激な変化には不安がある。もっと慎重に進めるべき。",
                    "これまでの制度の良さも考慮して、検討してほしい。"
                ],
                'neutral': [
                    "次世代への影響を考えて、責任を持って判断したい。",
                    "社会全体のバランスを考えて、慎重に検討すべき。"
                ]
            }
        }
    
    async def generate_response(self, persona: Dict, question: str, context_info: str = "") -> Dict:
        await asyncio.sleep(0.1)
        
        generation = persona.get('generation', 'X世代')
        political_leaning = persona.get('political_leaning', '中道')
        
        if political_leaning == '無関心':
            response = random.choice([
                "あまり政治的なことは分からないので、専門家に任せたい。",
                "普段の生活に直接関係する部分だけ考えています。",
                "詳しくないので、特に強い意見はありません。"
            ])
        else:
            if any(word in question for word in ['対策', '改善', '支援', '促進']):
                sentiment = 'positive'
            elif any(word in question for word in ['問題', '課題', '困難', '不安']):
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            patterns = self.response_patterns.get(generation, self.response_patterns['X世代'])
            response_list = patterns.get(sentiment, patterns['neutral'])
            response = random.choice(response_list)
        
        input_tokens = len(question) // 3 + 100
        output_tokens = len(response) // 3
        
        self.cost_tracker.add_usage(input_tokens, output_tokens)
        
        return {
            'success': True,
            'response': response,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': 0.0
        }
    
    async def summarize_search_results(self, search_results: List[Dict], question: str) -> Dict:
        """検索結果を要約（シミュレーション版）"""
        summary = f"""【{question}に関する最新動向】

政府は新しい政策方針を発表し、専門家の間では慎重な検討が必要との声が多く聞かれています。市民の意見は世代間で大きく分かれており、特に若年層では変化への期待が高い一方、高齢層では安定性を重視する傾向が見られます。

最新の調査によると、経済的影響への懸念が共通して表明されており、実現可能性について具体的な検討が求められています。専門家は段階的なアプローチの重要性を指摘しています。"""
        
        return {
            'success': True,
            'summary': summary.strip(),
            'input_tokens': 50,
            'output_tokens': 100,
            'cost_usd': 0.0
        }
    
    async def analyze_responses(self, responses: List[str], question: str) -> Dict:
        analysis = """【LLM分析レポート - 創造的詳細版】

**主要論点の整理**
今回の調査から浮かび上がる主要論点は、世代間の価値観の根本的対立、経済的現実への懸念、そして変化への期待と不安の複雑な共存である。特にZ世代とシニア世代の間では、理想主義対現実主義の対立軸が明確に表れており、Z世代の「環境重視・多様性受容」と、シニア世代の「安定性・伝統的価値重視」が鮮明なコントラストを見せている。

ミレニアル世代は独特の立ち位置を示しており、理想への共感と現実的制約への懸念を同時に抱える「挟まれ世代」として、家計への直接的影響を最優先に考える実用主義的アプローチが特徴的である。この世代の回答からは、子育て世代としての責任感と、経済的不安定性への警戒心が強く読み取れる。

**世代間・立場間の深層的対立軸**
単なる年齢差を超えた価値体系の根本的相違が観察される。Z世代の「変化への積極性」は、デジタルネイティブとしての柔軟性と、気候変動など地球規模の課題への危機意識に根ざしている。一方で「経済的制約への不安」も同時に表明しており、理想と現実の板挟み状態が浮き彫りになっている。

X世代以上に見られる「慎重論」は、バブル崩壊やリーマンショックなどの経済的混乱を経験した世代特有の「変化への警戒心」として理解できる。彼らの求める「段階的アプローチ」は、急激な変化がもたらすリスクへの深い理解に基づいている。

**感情的傾向と心理的背景の詳細分析**
全体として「慎重な現実主義」が支配的な感情傾向として現れているが、これは日本社会特有の「和」を重視する文化的背景と、長期的な経済停滞への集合的記憶が複合的に作用した結果と考えられる。

若い世代に見られる「将来への不安」は、終身雇用制の崩壊、年金制度への不信、気候変動への危機感など、多層的な不安要素が重なり合った現代特有の心理状態を反映している。シニア世代の「変化への警戒」は、高度経済成長期の成功体験と、その後の長期停滞期の挫折感が織り交ざった複雑な心境を表している。

**重要キーワードの文脈的意味と社会的含意**
「将来」「不安」「現実的」「慎重」「検討」「負担」「変化」などの頻出キーワードは、現代日本社会の集合的無意識を映し出している。特に「段階的」「バランス」というキーワードが示すのは、日本的合意形成文化の現代的表れであり、急激な変化よりも漸進的改革を好む国民性の反映である。

「負担」という言葉の頻出は、個人レベルでの経済的圧迫感と、社会全体での責任分散への願望を同時に表現している。「検討」「慎重」といった表現は、決断回避の傾向というより、多角的視点からの熟慮を重視する文化的特性の現れと解釈できる。

**社会的ダイナミクスと変化の兆候**
従来の左右の政治的対立軸に加えて、新たな「世代間価値観対立」「グローバル化対ローカル化」「効率性対安定性」といった多次元的な対立軸が形成されつつある。これは単線的な進歩史観では捉えきれない、複雑で非線形的な社会変化の兆候として注目される。

特に注目すべきは、従来の「保守対革新」の枠組みを超えた「適応的保守主義」の萌芽である。これは変化の必要性は認めつつも、その方法論において慎重さを求める新しい思考パターンであり、日本社会の成熟化の表れとも考えられる。

**政策提言と社会設計への創造的示唆**
第一に、世代間対話の制度化が急務である。単発的な討論会ではなく、継続的な相互理解促進メカニズムの構築が必要だ。具体的には「世代間メンター制度」「政策立案への世代別参画保証制度」などが考えられる。

第二に、「段階的変革設計」の専門的フレームワーク開発が重要である。急激な変化への不安を軽減しつつ、必要な改革を実現する「漸進的イノベーション手法」の確立が求められる。これには変化の予測可能性確保、移行期間の十分な設定、逆行可能性の担保などが含まれる。

**未来社会への建設的ビジョン**
この調査結果は、多様性と慎重さを両立させる新しい民主主義モデルの可能性を示唆している。異なる価値観を持つ世代が対立ではなく補完関係を築き、集合的知恵を活用する「統合的合意形成社会」の実現可能性が見えてくる。それは急進的変革でも保守的停滞でもない、「適応的進化」を志向する成熟社会のモデルとなりうるだろう。"""
        
        return {
            'success': True,
            'analysis': analysis.strip(),
            'input_tokens': 200,
            'output_tokens': 3000,
            'cost_usd': 0.0
        }

class PDFReportGenerator:
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLabライブラリが必要です: pip install reportlab matplotlib")
        
        self.styles = getSampleStyleSheet()
        self.setup_japanese_styles()
    
    def setup_japanese_styles(self):
        """日本語対応のスタイルを設定"""
        font_path = "/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/ipaexg.ttf"
        if not os.path.exists(font_path):
            # フォントが見つからない場合はデフォルト
            japanese_font = 'Helvetica'
        else:
            pdfmetrics.registerFont(TTFont('Japanese', font_path))
            japanese_font = 'Japanese'
        
        # カスタムスタイル定義
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            fontName=japanese_font,
            textColor=colors.navy
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            fontName=japanese_font,
            textColor=colors.darkblue
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName=japanese_font,
            leading=14
        )
    
    def generate_survey_report(self, survey_data: Dict, analysis_data: Dict = None) -> BytesIO:
        """総合的な調査レポートPDFを生成"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        
        story = []
        
        # タイトルページ
        story.append(Paragraph("LLM世論調査レポート", self.title_style))
        story.append(Spacer(1, 20))
        
        # 調査概要
        story.append(Paragraph("調査概要", self.heading_style))
        story.append(Paragraph(f"質問: {survey_data['question']}", self.body_style))
        story.append(Paragraph(f"実施日時: {survey_data['timestamp']}", self.body_style))
        story.append(Paragraph(f"回答者数: {survey_data['total_responses']}人", self.body_style))
        story.append(Spacer(1, 20))
        
        # 基本統計
        story.append(Paragraph("基本統計", self.heading_style))
        
        if 'demographics' in survey_data:
            demo = survey_data['demographics']
            
            # 世代分布表
            generation_data = [['世代', '人数', '割合']]
            for gen, count in demo['generation_counts'].items():
                percentage = (count / survey_data['total_responses']) * 100
                generation_data.append([gen, str(count), f"{percentage:.1f}%"])
            
            generation_table = Table(generation_data)
            generation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Japanese'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(generation_table)
            story.append(Spacer(1, 20))
        
        # AI分析結果
        if analysis_data and analysis_data.get('success'):
            story.append(PageBreak())
            story.append(Paragraph("AI分析結果", self.title_style))
            story.append(Spacer(1, 20))
            
            # 分析テキストを段落に分けて追加
            analysis_text = analysis_data['analysis']
            paragraphs = analysis_text.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    # マークダウン形式の見出しを処理
                    if para.startswith('**') and para.endswith('**'):
                        clean_text = para.strip('*')
                        story.append(Paragraph(clean_text, self.heading_style))
                    else:
                        story.append(Paragraph(para, self.body_style))
                    story.append(Spacer(1, 8))
        
        # 回答サンプル
        story.append(PageBreak())
        story.append(Paragraph("回答サンプル", self.title_style))
        story.append(Spacer(1, 20))
        
        if 'sample_responses' in survey_data:
            for i, response in enumerate(survey_data['sample_responses'][:10], 1):
                story.append(Paragraph(f"回答 {i}: {response['age']}歳 {response['gender']} ({response['generation']})", 
                                     self.heading_style))
                story.append(Paragraph(response['response'], self.body_style))
                story.append(Spacer(1, 12))
        
        # キーワード分析
        if 'keywords' in survey_data:
            story.append(PageBreak())
            story.append(Paragraph("キーワード分析", self.title_style))
            story.append(Spacer(1, 20))
            
            keyword_data = [['順位', 'キーワード', '出現回数']]
            for i, kw in enumerate(survey_data['keywords'][:15], 1):
                keyword_data.append([str(i), kw['word'], str(kw['count'])])
            
            keyword_table = Table(keyword_data)
            keyword_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Japanese'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(keyword_table)
        
        # 感情分析
        if 'sentiment' in survey_data:
            story.append(Spacer(1, 30))
            story.append(Paragraph("感情分析", self.heading_style))
            
            sentiment = survey_data['sentiment']
            sentiment_data = [
                ['感情', '割合'],
                ['ポジティブ', f"{sentiment['positive']:.1f}%"],
                ['ネガティブ', f"{sentiment['negative']:.1f}%"],
                ['中立', f"{sentiment['neutral']:.1f}%"]
            ]
            
            sentiment_table = Table(sentiment_data)
            sentiment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Japanese'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(sentiment_table)
        
        # PDFを構築
        doc.build(story)
        buffer.seek(0)
        return buffer



# UI関数群
def setup_sidebar():
    st.sidebar.title("⚙️ 設定")
    
    st.sidebar.header("🤖 LLMモード")
    
    use_real_llm = st.sidebar.radio(
        "モードを選択",
        ["シミュレーション（無料）", "GPT-4o-mini（有料）"],
    )
    
    st.session_state.use_real_llm = (use_real_llm == "GPT-4o-mini（有料）")
    
    if st.session_state.use_real_llm:
        st.sidebar.header("🔑 API設定")
        
        api_key = st.sidebar.text_input("OpenAI API Key", type="password")
        
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                st.sidebar.success("✅ 環境変数からAPIキーを読み込み")
            else:
                st.sidebar.error("❌ APIキーを入力してください")
                return
        
        st.session_state.api_key = api_key
        
        st.sidebar.warning("**料金目安:**\n- 100回答: 約1.2円\n- AI分析: 約1.8円")
    
    st.sidebar.header("👥 ペルソナ設定")
    
    persona_count = st.sidebar.selectbox("生成人数", [10, 25, 50, 100], index=0)
    st.session_state.persona_count = persona_count
    
    if st.session_state.use_real_llm:
        estimated_cost = persona_count * 0.00012 * 150
        st.sidebar.info(f"💰 予想コスト: 約{estimated_cost:.1f}円")

def show_home_tab():
    st.header("🏠 LLM100人に聞きました（世論調査シミュレーター）")
    
    st.markdown("""
    <div style="background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem;">
    🏷️ <strong>GPT-4o-mini料金</strong><br>
    • 100回答あたり約2円<br>
    • 創造的AI分析: 約2円/回<br>
    • 🦆 DuckDuckGo検索: 完全無料<br>
    • 📋 PDFレポート出力: 無料
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📊 世論調査シミュレーター
        
        ### ✨ PDF出力対応版の特徴
        
        - **📝 100文字程度**: 質問に対する回答
        - **🤖 回答をAI分析**: 取得した回答について詳細分析
        - **💰 コスト効率**: 文字数制限により低コスト運用
        - **🦆 DuckDuckGo検索**: 最新情報を無料で取得
        - **📊 統計分析**: 世代別・地域別の詳細分析
        - **📋 PDF出力**: 包括的な調査レポートをPDF形式で出力
        
        ### 🎯 活用場面
        
        - 簡易的な世論調査のデモンストレーション
        - 市場調査・消費者インサイト分析
        - 政策立案の参考資料作成
        - 学術研究・論文作成支援
        - プレゼンテーション用レポート作成
        - 企業の意思決定支援
        
        ### 📋 PDFレポート内容
        
        - **調査概要**: 質問、実施日時、回答者数
        - **基本統計**: 世代分布、年齢分布表
        - **AI分析結果**: 簡単な分析（2400文字）
        - **回答サンプル**: 世代別の代表的回答
        - **キーワード分析**: 頻出語句ランキング
        - **感情分析**: ポジティブ・ネガティブ・中立の割合
        """)
    
    with col2:
        st.subheader("📈 統計情報")
        
        if 'personas' in st.session_state:
            personas = st.session_state.personas
            df = pd.DataFrame(personas)
            
            st.metric("生成済みペルソナ数", len(personas))
            st.metric("平均年齢", f"{df['age'].mean():.1f}歳")
            
            generation_counts = df['generation'].value_counts()
            fig = px.pie(
                values=generation_counts.values,
                names=generation_counts.index,
                title="世代分布"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("まず「ペルソナ」タブでペルソナを生成してください")
        
        # PDF出力の依存関係チェック
        if REPORTLAB_AVAILABLE:
            st.success("✅ PDF出力機能: 利用可能")
        else:
            st.warning("⚠️ PDF出力機能: 要インストール\n`pip install reportlab matplotlib`")

def show_persona_tab():
    st.header("👥 ペルソナ生成・管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 データ基盤")
        st.markdown("""
        **人口統計データソース:**
        - 総務省人口推計（2024年10月）
        - 就業構造基本調査（令和4年）
        
        **生成される属性:**
        - 年齢、性別、居住都道府県
        - 職業（20歳以下は自動的に学生）、教育レベル、年収
        - 家族構成、政治的傾向
        - 世代ラベル、居住環境
        """)
        
        if st.button("🎲 ペルソナを生成", type="primary", use_container_width=True):
            generate_personas()
    
    with col2:
        st.subheader("⚙️ 生成設定")
        
        persona_count = st.session_state.get('persona_count', 10)
        st.info(f"生成人数: {persona_count}人")
        
        if st.session_state.get('use_real_llm', False):
            estimated_cost = persona_count * 0.00012 * 150
            st.warning(f"予想調査コスト: 約{estimated_cost:.1f}円")
        else:
            st.success("シミュレーション版: 無料")
    
    if 'personas' in st.session_state:
        st.subheader("👤 生成済みペルソナ")
        
        personas = st.session_state.personas
        df = pd.DataFrame(personas)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("総人数", len(personas))
        with col2:
            st.metric("平均年齢", f"{df['age'].mean():.1f}歳")
        with col3:
            male_ratio = (df['gender'] == '男性').mean()
            st.metric("男女比", f"男{male_ratio:.1%} : 女{1-male_ratio:.1%}")
        with col4:
            urban_ratio = (df['urban_rural'] == '都市部').mean()
            st.metric("都市部比率", f"{urban_ratio:.1%}")
        
        # 簡易グラフ
        col1, col2 = st.columns(2)
        
        with col1:
            generation_counts = df['generation'].value_counts()
            fig1 = px.pie(
                values=generation_counts.values,
                names=generation_counts.index,
                title="世代分布"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.histogram(
                df, x='age',
                title="年齢分布",
                nbins=15
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with st.expander("📋 ペルソナ詳細リスト"):
            display_df = df[['id', 'age', 'gender', 'prefecture', 'occupation', 'generation']].copy()
            display_df.columns = ['ID', '年齢', '性別', '都道府県', '職業', '世代']
            st.dataframe(display_df, use_container_width=True)

def show_survey_tab():
    st.header("❓ 世論調査の実行")
    
    if 'personas' not in st.session_state:
        st.warning("まず「ペルソナ」タブでペルソナを生成してください")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 質問設定")
        
        preset_questions = {
            "カスタム質問": "",
            "2025年の重要政治課題": "AI時代の新しい働き方とは？",
            "少子化対策": "効果的な少子化対策は何だと思いますか？",
            "経済政策": "日本経済活性化に最も重要な政策は何ですか？",
            "働き方改革": "理想的な働き方改革とはどのようなものですか？",
            "環境問題": "環境問題解決のためにできることは何ですか？",
            "教育制度": "日本の教育制度で改善すべき点は何ですか？",
            "社会保障": "将来の社会保障制度についてどう思いますか？"
        }
        
        selected_preset = st.selectbox(
            "プリセット質問から選択",
            list(preset_questions.keys())
        )
        
        if selected_preset == "カスタム質問":
            question = st.text_area(
                "質問を入力してください",
                value="",
                height=100,
                placeholder="例：あなたが考える理想的な社会とは？"
            )
        else:
            question = st.text_area(
                "選択された質問（編集可能）",
                value=preset_questions[selected_preset],
                height=100
            )
        
        st.subheader("🦆 Web検索（最新情報取得）")
        use_web_search = st.checkbox("質問に関連する最新情報を検索")
        
        search_query = ""
        if use_web_search:
            search_query = st.text_input(
                "検索キーワード",
                value=extract_search_keywords(question) if question else "",
                help="DuckDuckGoで最新情報を検索（無料）"
            )
    
    with col2:
        st.subheader("📊 調査設定")
        
        personas = st.session_state.personas
        st.metric("対象ペルソナ数", len(personas))
        
        if st.session_state.get('use_real_llm', False):
            st.success("🤖 GPT-4o-mini使用")
            
            if question:
                estimated_cost = len(personas) * 0.00012 * 150
                st.info(f"予想コスト: 約{estimated_cost:.1f}円")
        else:
            st.info("🎭 シミュレーション版使用")
            st.success("コスト: 無料")
    
    if st.button("🚀 調査を実行", type="primary", use_container_width=True):
        if not question.strip():
            st.error("質問を入力してください")
        else:
            execute_enhanced_survey(question, search_query if use_web_search else "")

def show_ai_analysis_tab():
    st.header("🤖 AI分析")
    
    if 'survey_responses' not in st.session_state:
        st.info("まず「調査」タブで調査を実行してください")
        return
    
    responses = st.session_state.survey_responses
    question = responses[0]['question']
    
    st.subheader(f"📝 分析対象: {question}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🤖 AI分析機能
        
        - **主要論点**: 3-5個の主要な論点を詳細分析
        - **世代間対立軸**: 世代による意見の違いと背景
        - **感情的傾向**: 心理的背景まで含めた感情分析
        - **重要キーワード**: 文脈的意味まで含めた分析
        - **社会的ダイナミクス**: 変化の兆しを読み取り
        - **政策提言**: 具体的で創造的な提案
        - **📋 PDF出力**: 分析結果をレポート形式で出力
        
        **特徴**: 疑似的な声の分析
        """)
    
    with col2:
        st.subheader("📊 分析設定")
        
        total_responses = len(responses)
        successful_responses = len([r for r in responses if r.get('success', True)])
        
        st.metric("分析対象回答数", successful_responses)
        
        if st.session_state.get('use_real_llm', False):
            st.info("🤖 GPT-4o-mini分析")
            st.warning("分析コスト: 約2円")
        else:
            st.info("🎭 シミュレーション分析")
            st.success("コスト: 無料")
    
    if st.button("🤖 AI分析を実行", type="primary", use_container_width=True):
        execute_ai_analysis(responses, question)
    
    if 'ai_analysis' in st.session_state:
        st.subheader("📋 AI分析レポート")
        
        analysis_result = st.session_state.ai_analysis
        
        if analysis_result.get('success', False):
            st.markdown(analysis_result['analysis'])
            
            # PDF出力ボタン（AI分析のみ）
            if REPORTLAB_AVAILABLE:
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("📋 AI分析レポートをPDF出力", type="secondary"):
                        generate_ai_analysis_pdf(analysis_result, question)
            
            if st.session_state.get('use_real_llm', False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("入力トークン", f"{analysis_result['input_tokens']:,}")
                with col2:
                    st.metric("出力トークン", f"{analysis_result['output_tokens']:,}")
                with col3:
                    st.metric("分析コスト", f"${analysis_result['cost_usd']:.4f}")
        else:
            st.error(f"分析エラー: {analysis_result.get('analysis', '不明なエラー')}")

def show_analysis_tab():
    st.header("📊 統計分析")
    
    if 'survey_responses' not in st.session_state:
        st.info("まず「調査」タブで調査を実行してください")
        return
    
    responses = st.session_state.survey_responses
    responses_df = pd.DataFrame([{
        'generation': r['persona']['generation'],
        'age': r['persona']['age'],
        'gender': r['persona']['gender'],
        'political_leaning': r['persona']['political_leaning'],
        'urban_rural': r['persona']['urban_rural'],
        'response': r['response'],
        'response_length': len(r['response'])
    } for r in responses])
    
    analyzer = ResponseAnalyzer()
    
    # 基本統計
    st.subheader("📈 基本統計")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.histogram(
            responses_df, x='response_length', 
            title="回答文字数分布",
            nbins=20
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.box(
            responses_df, x='generation', y='response_length',
            title="世代別回答長比較"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # キーワード分析
    st.subheader("🏷️ キーワード分析")
    
    responses_list = responses_df['response'].tolist()
    keywords = analyzer.extract_keywords(responses_list)
    
    if keywords:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            keyword_df = pd.DataFrame(keywords[:10])
            fig = px.bar(
                keyword_df, x='count', y='word',
                orientation='h',
                title="頻出キーワード Top 10"
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**キーワードランキング**")
            for i, kw in enumerate(keywords[:8], 1):
                st.write(f"{i}. {kw['word']} ({kw['count']}回)")
    
    # 感情分析
    st.subheader("😊 感情分析")
    
    sentiment = analyzer.analyze_sentiment(responses_list)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=[sentiment['positive'], sentiment['negative'], sentiment['neutral']],
            names=['ポジティブ', 'ネガティブ', '中立'],
            title="全体感情分布"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 世代別感情
        generation_sentiment = {}
        for generation in responses_df['generation'].unique():
            gen_responses = responses_df[responses_df['generation'] == generation]['response'].tolist()
            gen_sentiment = analyzer.analyze_sentiment(gen_responses)
            generation_sentiment[generation] = gen_sentiment
        
        sentiment_df = pd.DataFrame(generation_sentiment).T
        
        fig2 = px.bar(
            sentiment_df.reset_index(),
            x='index', y=['positive', 'negative', 'neutral'],
            title="世代別感情分析"
        )
        st.plotly_chart(fig2, use_container_width=True)

def show_results_tab():
    st.header("📊 調査結果")
    
    if 'survey_responses' not in st.session_state:
        st.info("まず「調査」タブで調査を実行してください")
        return
    
    responses = st.session_state.survey_responses
    question = responses[0]['question']
    
    st.subheader(f"📝 質問: {question}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_responses = len(responses)
    successful_responses = len([r for r in responses if r.get('success', True)])
    avg_response_length = np.mean([len(r['response']) for r in responses])
    
    with col1:
        st.metric("総回答数", total_responses)
    with col2:
        st.metric("成功回答数", successful_responses)
    with col3:
        st.metric("平均回答長", f"{avg_response_length:.1f}文字")
    with col4:
        if st.session_state.get('use_real_llm', False):
            total_cost = sum(r.get('cost_usd', 0) for r in responses)
            st.metric("総コスト", f"${total_cost:.4f}")
        else:
            st.metric("コスト", "無料")
    
    # 検索情報表示
    if 'search_results' in st.session_state:
        with st.expander("🦆 使用された最新情報"):
            for result in st.session_state.search_results:
                st.write(f"**{result['title']}**")
                st.write(result['snippet'])
                st.write("---")
    
    # 世代別回答サンプル
    response_df = pd.DataFrame([{
        'generation': r['persona']['generation'],
        'age': r['persona']['age'],
        'gender': r['persona']['gender'],
        'response': r['response']
    } for r in responses])
    
    st.subheader("💬 世代別回答サンプル")
    
    for generation in response_df['generation'].unique():
        with st.expander(f"{generation} の回答サンプル"):
            gen_responses = response_df[response_df['generation'] == generation]
            
            for idx, (_, row) in enumerate(gen_responses.head(3).iterrows(), 1):
                st.write(f"**{idx}. {row['age']}歳 {row['gender']}**")
                st.write(f"💬 {row['response']}")
                st.write("---")
    
    # データエクスポート
    st.subheader("📤 データエクスポート")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = response_df.copy()
        csv_data['質問'] = question
        csv_data['回答時刻'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        csv_str = csv_data.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📊 CSV形式でダウンロード",
            data=csv_str,
            file_name=f"survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = {
            'survey_info': {
                'question': question,
                'timestamp': datetime.now().isoformat(),
                'total_responses': len(response_df),
                'ai_analysis': st.session_state.get('ai_analysis', {})
            },
            'responses': responses
        }
        
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        st.download_button(
            label="📄 JSON形式でダウンロード",
            data=json_str,
            file_name=f"survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col3:
        # PDF出力ボタン
        if REPORTLAB_AVAILABLE:
            if st.button("📋 PDFレポート生成", type="primary", use_container_width=True):
                generate_pdf_report(responses, question)
        else:
            st.warning("📋 PDF出力にはReportLabが必要です\n`pip install reportlab matplotlib`")

# ヘルパー関数
def extract_search_keywords(question: str) -> str:
    keywords = []
    if '政治' in question:
        keywords.append('日本 政治 2025')
    if '経済' in question:
        keywords.append('日本 経済 2025')
    if '少子化' in question:
        keywords.append('少子化対策 2025')
    if '環境' in question:
        keywords.append('環境問題 日本')
    if '教育' in question:
        keywords.append('教育制度 日本')
    
    return ' '.join(keywords) if keywords else question[:20]

def generate_personas():
    persona_count = st.session_state.get('persona_count', 10)
    
    with st.spinner(f'{persona_count}人のペルソナを生成中...'):
        progress_bar = st.progress(0)
        
        demographics_db = JapanDemographicsDB()
        persona_generator = PersonaGenerator(demographics_db)
        
        personas = []
        for i in range(persona_count):
            persona = persona_generator.generate_persona(i + 1)
            personas.append(asdict(persona))
            progress_bar.progress((i + 1) / persona_count)
        
        st.session_state.personas = personas
        st.success(f"✅ {persona_count}人のペルソナを生成しました！")

def execute_enhanced_survey(question: str, search_query: str = ""):
    personas = st.session_state.personas
    use_real_llm = st.session_state.get('use_real_llm', False)
    
    # 検索結果の要約を実行
    context_info = ""
    search_summary = None
    
    if search_query:
        search_provider = WebSearchProvider()
        
        # 10件の検索結果を取得
        search_results = search_provider.search_recent_info(search_query, num_results=10)
        st.session_state.search_results = search_results
        
        if search_results and len(search_results) > 0:
            # 検索結果要約の実行
            with st.spinner('🔍 検索結果を要約中...'):
                if use_real_llm and 'llm_provider' in st.session_state:
                    # 実LLMで要約
                    async def run_summary():
                        return await st.session_state.llm_provider.summarize_search_results(search_results, question)
                    
                    try:
                        search_summary = asyncio.run(run_summary())
                        if search_summary.get('success', False):
                            context_info = f"【最新情報要約】\n{search_summary['summary']}"
                            st.success(f"✅ 検索結果要約完了（{len(search_results)}件から要約）")
                        else:
                            st.warning("検索結果要約に失敗しました")
                    except Exception as e:
                        st.error(f"要約エラー: {e}")
                else:
                    # シミュレーション版で要約
                    sim_provider = SimulationProvider()
                    
                    async def run_sim_summary():
                        return await sim_provider.summarize_search_results(search_results, question)
                    
                    try:
                        search_summary = asyncio.run(run_sim_summary())
                        if search_summary.get('success', False):
                            context_info = f"【最新情報要約】\n{search_summary['summary']}"
                            st.success(f"✅ 検索結果要約完了（{len(search_results)}件から要約）")
                    except Exception as e:
                        st.error(f"要約エラー: {e}")
    
    # プロバイダー初期化
    if use_real_llm:
        if 'llm_provider' not in st.session_state:
            api_key = st.session_state.get('api_key')
            if not api_key:
                st.error("APIキーが設定されていません")
                return
            
            try:
                st.session_state.llm_provider = GPT4OMiniProvider(api_key)
            except Exception as e:
                st.error(f"プロバイダー初期化エラー: {e}")
                return
        
        provider = st.session_state.llm_provider
    else:
        provider = SimulationProvider()
    
    # 調査実行
    with st.spinner(f'{"GPT-4o-mini" if use_real_llm else "シミュレーション"}で調査中...'):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 要約情報も表示
        if search_summary:
            cost_text = st.empty()
            if use_real_llm:
                cost_text.info(f"検索要約コスト: ${search_summary.get('cost_usd', 0):.4f}")
        
        responses = []
        
        async def run_survey():
            for i, persona in enumerate(personas):
                status_text.text(f"回答生成中: {i+1}/{len(personas)}")
                
                result = await provider.generate_response(persona, question, context_info)
                
                response = {
                    'persona_id': persona['id'],
                    'persona': persona,
                    'question': question,
                    'response': result['response'],
                    'success': result.get('success', True),
                    'cost_usd': result.get('cost_usd', 0.0),
                    'timestamp': datetime.now().isoformat(),
                    'context_used': bool(context_info)
                }
                
                responses.append(response)
                progress_bar.progress((i + 1) / len(personas))
        
        try:
            asyncio.run(run_survey())
        except Exception as e:
            st.error(f"調査実行エラー: {e}")
            return
        
        # 検索要約情報も保存
        if search_summary:
            st.session_state.search_summary = search_summary
        
        st.session_state.survey_responses = responses
        
        successful_count = len([r for r in responses if r['success']])
        
        # 総コスト計算
        total_cost = sum(r.get('cost_usd', 0) for r in responses)
        if search_summary:
            total_cost += search_summary.get('cost_usd', 0)
        
        if successful_count == len(responses):
            cost_msg = f" (総コスト: ${total_cost:.4f})" if use_real_llm else ""
            st.success(f"✅ 調査完了！{successful_count}件の回答を取得{cost_msg}")
        else:
            st.warning(f"⚠️ 調査完了。{successful_count}/{len(responses)}件の回答を取得")

def execute_ai_analysis(responses: List[Dict], question: str):
    use_real_llm = st.session_state.get('use_real_llm', False)
    
    successful_responses = [r['response'] for r in responses if r.get('success', True)]
    
    if not successful_responses:
        st.error("分析可能な回答がありません")
        return
    
    if use_real_llm:
        if 'llm_provider' not in st.session_state:
            st.error("LLMプロバイダーが初期化されていません")
            return
        provider = st.session_state.llm_provider
    else:
        provider = SimulationProvider()
    
    with st.spinner('🤖 AI分析中...'):
        
        async def run_analysis():
            result = await provider.analyze_responses(successful_responses, question)
            return result
        
        try:
            analysis_result = asyncio.run(run_analysis())
            st.session_state.ai_analysis = analysis_result
            
            if analysis_result.get('success', False):
                st.success("✅ AI分析完了！")
            else:
                st.error(f"❌ AI分析エラー: {analysis_result.get('analysis', '不明')}")
                
        except Exception as e:
            st.error(f"AI分析実行エラー: {e}")

def generate_pdf_report(responses: List[Dict], question: str):
    """PDF調査レポートを生成"""
    try:
        with st.spinner('📋 PDFレポートを生成中...'):
            # データ準備
            responses_df = pd.DataFrame([{
                'generation': r['persona']['generation'],
                'age': r['persona']['age'],
                'gender': r['persona']['gender'],
                'political_leaning': r['persona']['political_leaning'],
                'urban_rural': r['persona']['urban_rural'],
                'response': r['response'],
                'response_length': len(r['response'])
            } for r in responses])
            
            # 統計分析
            analyzer = ResponseAnalyzer()
            responses_list = responses_df['response'].tolist()
            keywords = analyzer.extract_keywords(responses_list)
            sentiment = analyzer.analyze_sentiment(responses_list)
            
            # 世代分布
            generation_counts = responses_df['generation'].value_counts().to_dict()
            
            # サンプル回答
            sample_responses = []
            for generation in responses_df['generation'].unique():
                gen_responses = responses_df[responses_df['generation'] == generation]
                for _, row in gen_responses.head(2).iterrows():
                    sample_responses.append({
                        'age': row['age'],
                        'gender': row['gender'],
                        'generation': row['generation'],
                        'response': row['response']
                    })
            
            # 調査データ構造
            survey_data = {
                'question': question,
                'timestamp': datetime.now().strftime("%Y年%m月%d日 %H:%M"),
                'total_responses': len(responses),
                'demographics': {
                    'generation_counts': generation_counts
                },
                'sample_responses': sample_responses[:15],  # 最大15件
                'keywords': keywords,
                'sentiment': sentiment
            }
            
            # AI分析データ
            analysis_data = st.session_state.get('ai_analysis', {})
            
            # PDF生成
            pdf_generator = PDFReportGenerator()
            pdf_buffer = pdf_generator.generate_survey_report(survey_data, analysis_data)
            
            # ダウンロードボタン
            st.success("✅ PDFレポート生成完了！")
            st.download_button(
                label="📋 PDFレポートをダウンロード",
                data=pdf_buffer,
                file_name=f"survey_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
            
    except Exception as e:
        st.error(f"PDF生成エラー: {e}")
        st.info("必要なライブラリをインストールしてください: `pip install reportlab matplotlib`")

def generate_ai_analysis_pdf(analysis_result: Dict, question: str):
    """AI分析結果のみのPDFを生成"""
    try:
        with st.spinner('📋 AI分析PDFを生成中...'):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
            
            pdf_generator = PDFReportGenerator()
            story = []
            
            # タイトル
            story.append(Paragraph("AI分析レポート", pdf_generator.title_style))
            story.append(Spacer(1, 20))
            
            # 質問
            story.append(Paragraph("分析対象", pdf_generator.heading_style))
            story.append(Paragraph(f"質問: {question}", pdf_generator.body_style))
            story.append(Paragraph(f"分析日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}", pdf_generator.body_style))
            story.append(Spacer(1, 30))
            
            # AI分析結果
            story.append(Paragraph("AI分析結果", pdf_generator.title_style))
            story.append(Spacer(1, 20))
            
            # 分析テキストを段落に分けて追加
            analysis_text = analysis_result['analysis']
            paragraphs = analysis_text.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    # マークダウン形式の見出しを処理
                    if para.startswith('**') and para.endswith('**'):
                        clean_text = para.strip('*')
                        story.append(Paragraph(clean_text, pdf_generator.heading_style))
                    else:
                        story.append(Paragraph(para, pdf_generator.body_style))
                    story.append(Spacer(1, 8))
            
            # PDFを構築
            doc.build(story)
            buffer.seek(0)
            
            # ダウンロードボタン
            st.success("✅ AI分析PDF生成完了！")
            st.download_button(
                label="📋 AI分析PDFをダウンロード",
                data=buffer,
                file_name=f"ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
            
    except Exception as e:
        st.error(f"AI分析PDF生成エラー: {e}")

# メイン関数
def main():
    st.title("💰 LLM100人に聞きました")
    st.caption("📋 フリーアンサーcsv・json出力 | 約100文字回答 + AI分析 + 包括的PDFレポート")
    
    setup_sidebar()
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 ホーム", "👥 ペルソナ", "❓ 調査", "🤖 AI分析", "📊 統計", "📈 結果"
    ])
    
    with tab1:
        show_home_tab()
    
    with tab2:
        show_persona_tab()
    
    with tab3:
        show_survey_tab()
    
    with tab4:
        show_ai_analysis_tab()
    
    with tab5:
        show_analysis_tab()
    
    with tab6:
        show_results_tab()

if __name__ == "__main__":
    main()

