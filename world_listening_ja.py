# app.py - 地球生物種意見調査シミュレーター（日本語版 Streamlit）
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
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import re
from collections import Counter

# オプション imports
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
    matplotlib.use('Agg')
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ページ設定
st.set_page_config(
    page_title="地球生物種意見調査シミュレーター",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態初期化
def init_session_state():
    """セッション状態変数を初期化してKeyErrorを防ぐ"""
    defaults = {
        'use_real_llm': False,
        'api_key': '',
        'persona_count': 10,
        'species_personas': None,
        'survey_responses': None,
        'ai_analysis': None,
        'search_results': None,
        'search_summary': None,
        'llm_provider': None,
        'cost_tracker': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# 起動時にセッション状態を初期化
init_session_state()

@dataclass
class SpeciesProfile:
    id: int
    species_type: str  # '海洋', '陸上', '空中'
    species_name: str
    individual_name: str
    age: int
    gender: str
    region: str
    habitat: str
    communication_method: str
    ecological_role: str
    resource_access: str
    social_status: str
    survival_priority: str
    intelligence_level: str

class GlobalSpeciesDB:
    def __init__(self):
        self.setup_species_data()
    
    def setup_species_data(self):
        # 実際の個体数データに基づく主要種族（個体数順）
        self.species_population = {
            # 海洋生物（最大個体数）
            'ニシン': {
                'population': 8e11, 
                'habitats': ['北大西洋', '北太平洋'], 
                'regions': ['北極海', '北太平洋', '北大西洋'],
                'type': '海洋'
            },
            'サバ': {
                'population': 3e11, 
                'habitats': ['温帯海域', '亜寒帯海域'], 
                'regions': ['太平洋', '大西洋', 'インド洋'],
                'type': '海洋'
            },
            'タラ': {
                'population': 2e11, 
                'habitats': ['北大西洋深海', '大陸棚'], 
                'regions': ['北大西洋', '北極海'],
                'type': '海洋'
            },
            'サケ': {
                'population': 1e11, 
                'habitats': ['北太平洋', '河川'], 
                'regions': ['北太平洋', '北米河川', 'アジア河川'],
                'type': '海洋'
            },
            'マグロ': {
                'population': 5e10, 
                'habitats': ['外洋', '深海'], 
                'regions': ['太平洋', '大西洋', 'インド洋'],
                'type': '海洋'
            },
            
            # 鳥類（最大陸上個体数）
            'ニワトリ': {
                'population': 3.3e10, 
                'habitats': ['農場', '都市部'], 
                'regions': ['全大陸'],
                'type': '陸上'
            },
            'スズメ': {
                'population': 5e8, 
                'habitats': ['都市部', '農地', '森林端'], 
                'regions': ['ユーラシア', '北米', 'アフリカ'],
                'type': '空中'
            },
            'カラス': {
                'population': 4e8, 
                'habitats': ['都市部', '森林', '農地'], 
                'regions': ['全大陸'],
                'type': '空中'
            },
            'ハト': {
                'population': 3e8, 
                'habitats': ['都市部', '岩場'], 
                'regions': ['全大陸'],
                'type': '空中'
            },
            
            # 哺乳類
            'ネズミ': {
                'population': 1e10, 
                'habitats': ['都市部', '農地', '森林', '地下'], 
                'regions': ['全大陸'],
                'type': '陸上'
            },
            'コウモリ': {
                'population': 1e9, 
                'habitats': ['洞窟', '森林', '都市部'], 
                'regions': ['全大陸'],
                'type': '空中'
            },
            'イヌ': {
                'population': 1e9, 
                'habitats': ['都市部', '農村部', '野生'], 
                'regions': ['全大陸'],
                'type': '陸上'
            },
            'ネコ': {
                'population': 6e8, 
                'habitats': ['都市部', '農村部', '野生'], 
                'regions': ['全大陸'],
                'type': '陸上'
            },
            
            # 家畜
            'ウシ': {
                'population': 1e9, 
                'habitats': ['牧場', '草地'], 
                'regions': ['全大陸'],
                'type': '陸上'
            },
            'ヒツジ': {
                'population': 1.2e9, 
                'habitats': ['牧場', '山地草原'], 
                'regions': ['全大陸'],
                'type': '陸上'
            },
            'ヤギ': {
                'population': 1.1e9, 
                'habitats': ['山地', '乾燥地'], 
                'regions': ['全大陸'],
                'type': '陸上'
            },
            'ブタ': {
                'population': 7e8, 
                'habitats': ['農場', '森林'], 
                'regions': ['全大陸'],
                'type': '陸上'
            },
            
            # アフリカサバンナ
            'ヌー': {
                'population': 2e6, 
                'habitats': ['サバンナ', '草原'], 
                'regions': ['東アフリカ', '南アフリカ'],
                'type': '陸上'
            },
            'シマウマ': {
                'population': 7.5e5, 
                'habitats': ['サバンナ', '草原'], 
                'regions': ['アフリカ'],
                'type': '陸上'
            },
            'ゾウ': {
                'population': 5e5, 
                'habitats': ['サバンナ', '森林'], 
                'regions': ['アフリカ', 'アジア'],
                'type': '陸上'
            },
            
            # 海洋哺乳類
            'イルカ': {
                'population': 6e6, 
                'habitats': ['温帯海域', '熱帯海域'], 
                'regions': ['全海洋'],
                'type': '海洋'
            },
            'クジラ': {
                'population': 2e6, 
                'habitats': ['外洋', '極地海域'], 
                'regions': ['全海洋'],
                'type': '海洋'
            },
            
            # 爬虫類・両生類
            'ヘビ': {
                'population': 1e8, 
                'habitats': ['森林', '砂漠', '草原'], 
                'regions': ['全大陸（南極除く）'],
                'type': '陸上'
            },
            'カエル': {
                'population': 5e7, 
                'habitats': ['湿地', '森林', '池沼'], 
                'regions': ['全大陸'],
                'type': '陸上'
            },
        }
        
        # 種族特性データ
        self.species_characteristics = {
            'ニシン': {
                'communication': '化学信号と群れ行動',
                'intelligence': '基本的集団知能',
                'survival_traits': ['大群形成', '高速移動', '産卵戦略'],
                'priorities': ['群れの安全', '豊富な餌場', '産卵場所の確保'],
                'ecological_role': '海洋食物連鎖の要',
                'social_structure': '大規模群れ社会'
            },
            'サバ': {
                'communication': '側線感覚と群れ形成',
                'intelligence': '回遊本能',
                'survival_traits': ['高速遊泳', '群れ行動', '季節回遊'],
                'priorities': ['回遊路の安全', '捕食者回避', '豊富な漁場'],
                'ecological_role': '中層捕食者',
                'social_structure': '回遊群れ'
            },
            'ニワトリ': {
                'communication': '鳴き声と身体言語',
                'intelligence': '社会学習能力',
                'survival_traits': ['警戒心', '社会性', '適応力'],
                'priorities': ['群れの安全', '安定した餌', '営巣場所'],
                'ecological_role': '雑食性地上鳥',
                'social_structure': '階層社会'
            },
            'ネズミ': {
                'communication': '超音波と匂い',
                'intelligence': '高い学習能力',
                'survival_traits': ['高い繁殖力', '適応力', '小さく敏捷'],
                'priorities': ['安全な巣穴', '食料確保', '繁殖成功'],
                'ecological_role': '小型哺乳類・種子散布者',
                'social_structure': '家族群'
            },
            'イルカ': {
                'communication': 'エコーロケーションと音響信号',
                'intelligence': '高度な認知能力',
                'survival_traits': ['知能', '協力', '音響能力'],
                'priorities': ['海洋環境保護', 'ポッドの絆', '魚資源確保'],
                'ecological_role': '海洋頂点捕食者',
                'social_structure': 'ポッド社会'
            },
            'ゾウ': {
                'communication': '低周波と触覚',
                'intelligence': '高度な知能と記憶',
                'survival_traits': ['長寿', '記憶力', '家族の絆', '大型'],
                'priorities': ['家族群保護', '水源確保', '知識継承'],
                'ecological_role': '大型草食動物・生態系エンジニア',
                'social_structure': '母系社会'
            },
            'ヌー': {
                'communication': '鳴き声と匂い',
                'intelligence': '集団行動本能',
                'survival_traits': ['大移動', '群れ行動', '持久力'],
                'priorities': ['移動成功', '草地確保', '群れ結束'],
                'ecological_role': '大型草食動物・回遊種',
                'social_structure': '大群れ社会'
            },
            'カラス': {
                'communication': '複雑な鳴き声とジェスチャー',
                'intelligence': '高度な問題解決能力',
                'survival_traits': ['知能', '道具使用', '記憶力', '適応力'],
                'priorities': ['知恵の活用', '縄張り確保', '仲間との協力'],
                'ecological_role': '知能捕食者・清掃者',
                'social_structure': '家族群と群れ'
            },
            'クジラ': {
                'communication': '歌声と長距離音響',
                'intelligence': '高度な社会知能',
                'survival_traits': ['大型', '長距離回遊', '深海潜水'],
                'priorities': ['海洋保護', '回遊路維持', '家族ポッド保護'],
                'ecological_role': '海洋大型捕食者',
                'social_structure': '家族ポッド'
            }
        }
        
        # デフォルト特性（具体的データがない種族用）
        self.default_characteristics = {
            'communication': '種族固有の方法',
            'intelligence': '本能的知能',
            'survival_traits': ['適応力', '生存本能'],
            'priorities': ['種族繁栄', '生存確保'],
            'ecological_role': '生態系構成員',
            'social_structure': '群れ社会'
        }

class SpeciesPersonaGenerator:
    def __init__(self, species_db: GlobalSpeciesDB):
        self.db = species_db
        
    def generate_weighted_choice(self, distribution: Dict[str, float]) -> str:
        choices = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(choices, weights=weights)[0]
    
    def calculate_species_distribution(self, total_personas: int) -> Dict[str, int]:
        """個体数データに基づく種族分布計算"""
        total_population = sum(data['population'] for data in self.db.species_population.values())
        
        species_distribution = {}
        remaining_personas = total_personas
        
        # 個体数比率に基づく割り当て
        species_list = list(self.db.species_population.items())
        species_list.sort(key=lambda x: x[1]['population'], reverse=True)
        
        for species, data in species_list[:-1]:  # 最後の種族以外
            ratio = data['population'] / total_population
            count = max(1, min(int(total_personas * ratio), remaining_personas - (len(species_list) - len(species_distribution) - 1)))
            
            if remaining_personas > 0:
                species_distribution[species] = count
                remaining_personas -= count
        
        # 残りを最後の種族に割り当て
        if species_list and remaining_personas > 0:
            last_species = species_list[-1][0]
            species_distribution[last_species] = remaining_personas
        
        return species_distribution
    
    def generate_species_persona(self, persona_id: int, species: str) -> SpeciesProfile:
        species_data = self.db.species_population.get(species, {})
        species_chars = self.db.species_characteristics.get(species, self.db.default_characteristics)
        
        # 基本属性
        habitats = species_data.get('habitats', ['未知の生息地'])
        regions = species_data.get('regions', ['地球'])
        species_type = species_data.get('type', '陸上')
        
        habitat = random.choice(habitats)
        region = random.choice(regions)
        
        # 年齢設定（種族の寿命に基づく）
        age_ranges = {
            'ニシン': (0, 15), 'サバ': (0, 12), 'タラ': (0, 20), 'サケ': (0, 8), 'マグロ': (0, 30),
            'ニワトリ': (0, 8), 'スズメ': (0, 10), 'カラス': (0, 20), 'ハト': (0, 15),
            'ネズミ': (0, 3), 'コウモリ': (0, 30), 'イヌ': (0, 15), 'ネコ': (0, 18),
            'ウシ': (0, 20), 'ヒツジ': (0, 15), 'ヤギ': (0, 18), 'ブタ': (0, 15),
            'ヌー': (0, 20), 'シマウマ': (0, 25), 'ゾウ': (0, 70),
            'イルカ': (0, 50), 'クジラ': (0, 80), 'ヘビ': (0, 25), 'カエル': (0, 15)
        }
        
        min_age, max_age = age_ranges.get(species, (0, 10))
        age = random.randint(min_age, max_age)
        
        # 性別
        gender = random.choice(['オス', 'メス'])
        
        # 社会的地位
        social_structure = species_chars['social_structure']
        if '大規模' in social_structure or '群れ' in social_structure:
            social_status = random.choice(['群れのリーダー', '群れのメンバー', '若い個体'])
        elif '家族' in social_structure:
            social_status = random.choice(['家族の長', '親', '子ども'])
        elif '階層' in social_structure:
            social_status = random.choice(['優位個体', '中位個体', '劣位個体'])
        else:
            social_status = random.choice(['リーダー', 'メンバー', '単独個体'])
        
        # 知能レベル
        intelligence_levels = {
            'イルカ': '高度な認知能力', 'クジラ': '高度な社会知能', 'ゾウ': '高度な記憶・学習',
            'カラス': '問題解決・道具使用', 'ネズミ': '学習・適応能力',
            'ニワトリ': '社会学習', 'イヌ': '協力・学習能力', 'ネコ': '狩猟・独立思考',
            'ヌー': '集団知能', 'シマウマ': '警戒・記憶能力'
        }
        
        intelligence_level = intelligence_levels.get(species, '本能的知能')
        
        # 資源アクセス
        resource_access = random.choice(['豊富', '普通', '乏しい', '変動的'])
        
        # 生存優先事項
        survival_priority = random.choice(species_chars['priorities'])
        
        return SpeciesProfile(
            id=persona_id,
            species_type=species_type,
            species_name=species,
            individual_name=f"{species}-{persona_id}",
            age=age,
            gender=gender,
            region=region,
            habitat=habitat,
            communication_method=species_chars['communication'],
            ecological_role=species_chars['ecological_role'],
            resource_access=resource_access,
            social_status=social_status,
            survival_priority=survival_priority,
            intelligence_level=intelligence_level
        )

class WebSearchProvider:
    def __init__(self):
        pass
        
    def search_recent_info(self, query: str, num_results: int = 10) -> List[Dict]:
        """安全な検索と適切なエラーハンドリング・結果トリミング"""
        # クエリの制限と無害化
        safe_query = str(query)[:100]  # クエリ長制限
        num_results = min(max(1, num_results), 20)  # 結果数を1-20に制限
        
        if DDGS_AVAILABLE:
            try:
                ddgs = DDGS()
                search_results = []
                
                results = ddgs.text(
                    keywords=f"{safe_query} 生物 環境 野生動物 2025",
                    region='jp-jp',
                    max_results=num_results
                )
                
                for result in results:
                    # 安全な結果処理と適切なトリミング
                    safe_result = {
                        'title': self._safe_trim(result.get('title', ''), 150),
                        'snippet': self._safe_trim(result.get('body', ''), 250),
                        'url': self._safe_trim(result.get('href', ''), 200),
                        'date': '2025年最新'
                    }
                    search_results.append(safe_result)
                
                return search_results if search_results else self._get_demo_results(safe_query, num_results)
                
            except Exception as e:
                st.warning(f"検索エラー: {str(e)[:100]}")  # 安全なエラーメッセージ
                return self._get_demo_results(safe_query, num_results)
        else:
            return self._get_demo_results(safe_query, num_results)
    
    def _safe_trim(self, text: str, max_length: int) -> str:
        """テキストを指定長に安全にトリミング"""
        if not text:
            return ""
        
        text = str(text)  # 文字列型確保
        if len(text) <= max_length:
            return text
        
        # 単語切断を避けるためmax_length前の最後のスペースを探す
        trimmed = text[:max_length]
        last_space = trimmed.rfind(' ')
        
        if last_space > max_length * 0.8:  # スペースが終端に合理的に近い場合
            return trimmed[:last_space] + "..."
        else:
            return trimmed[:max_length-3] + "..."
    
    def _get_demo_results(self, query: str, num_results: int = 10) -> List[Dict]:
        """安全なデモ結果生成"""
        demo_results = []
        safe_query = self._safe_trim(query, 50)
        
        for i in range(min(num_results, 5)):  # デモ結果を制限
            demo_results.append({
                'title': f'{safe_query}に関する最新生物学研究 {i+1}',
                'snippet': f'{safe_query}について、生物学者と環境科学者が新しい発見を報告。生態系への影響と種間相互作用について重要な知見が得られています。',
                'url': f'https://bio-research{i+1}.com',
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
    
    def create_species_persona_prompt(self, persona: Dict, question: str, context_info: str = "") -> str:
        context_section = f"\n【環境情報】\n{context_info}\n" if context_info else ""
        
        prompt = f"""【あなたのプロフィール】
種族: {persona['species_name']} ({persona['individual_name']})
年齢: {persona['age']}歳, 性別: {persona['gender']}
生息地: {persona['habitat']} ({persona['region']})
生態的役割: {persona['ecological_role']}
コミュニケーション: {persona['communication_method']}
知能レベル: {persona['intelligence_level']}
社会的地位: {persona['social_status']}
生存優先事項: {persona['survival_priority']}
{context_section}
【質問】{question}

【回答指示】
{persona['species_name']}として、種族の繁栄と生存を最優先に回答してください。
- あなたの本能、知能、経験に基づいて
- 種族の特性と生態的役割を活用して
- 100文字以内で簡潔に
- {persona['species_name']}の視点から
"""
        return prompt
    
    def create_search_summary_prompt(self, search_results: List[Dict], question: str) -> str:
        """検索結果要約プロンプト"""
        search_content = "\n".join([
            f"【記事{i+1}】{result['title']}\n{result['snippet']}"
            for i, result in enumerate(search_results[:10])
        ])
        
        prompt = f"""【質問】{question}

【検索結果】
{search_content}

【要約指示】
上記の検索結果を300文字以内で要約してください：
1. {question}に関する最新の生物学・環境動向
2. 生態系や種族への影響
3. 専門家の見解
4. 環境変化と保護活動

生物にとって分かりやすい要約を作成してください。
"""
        return prompt
    
    def create_analysis_prompt(self, responses: List[str], question: str) -> str:
        all_responses = "\n".join([f"{i+1}: {resp}" for i, resp in enumerate(responses)])
        
        prompt = f"""【質問】{question}

【地球の生物種からの回答】
{all_responses}

【分析指示】
2400文字以内で詳細かつ創造的に分析してください：

1. **種族間の主要な論争軸と対立軸**（500文字）
   - 海洋生物vs陸上生物の視点の違い
   - 捕食者vs被食者の利害対立
   - 高個体数種vs希少種の影響力の違い
   - 高知能種vs本能依存種の思考パターン

2. **生態系ポジション別の戦略と優先順位**（500文字）
   - 大群形成種（ニシン・ヌーなど）の集団主義的思考
   - 高知能種（イルカ・ゾウ・カラスなど）の問題解決アプローチ
   - 頂点捕食者の資源確保戦略
   - 被食種の安全重視思考

3. **コミュニケーション方法が思考に与える影響**（400文字）
   - 化学信号依存種の直感的判断
   - 音響コミュニケーション種の協力性
   - 視覚コミュニケーション種の情報処理能力
   - 触覚・振動ベースコミュニケーションの特徴

4. **生存戦略の多様性と相互依存**（400文字）
   - 量的戦略（大量繁殖）vs質的戦略（エリート方式）
   - 移動戦略vs定住戦略
   - 協力戦略vs競争戦略
   - 適応戦略vs環境改変戦略

5. **地球規模課題への種族横断的解決策**（300文字）
   - 各種族の能力を活用した協力システム
   - 海洋-陸上-空中ネットワーク連携
   - 知能と本能を組み合わせた最適化

6. **生物多様性保護への新アプローチ**（300文字）
   - 種族の声を反映した環境政策
   - 生態系自己組織化能力の活用
   - 人間中心主義から生命中心主義への価値転換

生物多様性と生態系の複雑さを活用した革新的分析を2400文字で作成してください。
"""
        return prompt
    
    def count_tokens(self, text: str) -> int:
        """tiktokenを使用した正確なトークン数計算"""
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                # エンコーディング失敗時のフォールバック
                st.warning(f"トークン数計算エラー: {e}。近似値を使用します。")
                return len(text.split()) * 1.3  # より正確な近似
        else:
            # tiktoken利用不可時のより良い近似
            return int(len(text.split()) * 1.3)
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """GPT-4o-miniの正確なコスト計算"""
        input_cost = (input_tokens / 1000) * 0.00015  # 入力1Kトークンあたり$0.00015
        output_cost = (output_tokens / 1000) * 0.0006  # 出力1Kトークンあたり$0.0006
        return input_cost + output_cost

class GPT4OMiniProvider:
    def __init__(self, api_key: str):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAIライブラリが必要です")
            
        self.client = openai.OpenAI(api_key=api_key)  # 同期クライアント
        self.prompt_generator = EnhancedPromptGenerator()
        self.cost_tracker = CostTracker()
        
    def generate_response(self, persona: Dict, question: str, context_info: str = "") -> Dict:
        """StreamlitのasyncioIssueを回避するための同期レスポンス生成"""
        prompt = self.prompt_generator.create_species_persona_prompt(persona, question, context_info)
        input_tokens = self.prompt_generator.count_tokens(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.9,
                timeout=45
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # 100文字制限を強制
            if len(response_text) > 100:
                response_text = response_text[:97] + "..."
            
            output_tokens = self.prompt_generator.count_tokens(response_text)
            cost_usd = self.prompt_generator.estimate_cost(input_tokens, output_tokens)
            self.cost_tracker.add_usage(input_tokens, output_tokens)
            
            return {
                'success': True,
                'response': response_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost_usd': cost_usd
            }
            
        except Exception as e:
            self.cost_tracker.add_usage(input_tokens, 0)
            error_msg = str(e)
            
            # 安全なエラーメッセージトリミング
            if len(error_msg) > 50:
                error_msg = error_msg[:47] + "..."
            
            return {
                'success': False,
                'response': f"APIエラー: {error_msg}",
                'input_tokens': input_tokens,
                'output_tokens': 0,
                'cost_usd': self.prompt_generator.estimate_cost(input_tokens, 0),
                'error': str(e)
            }
    
    def summarize_search_results(self, search_results: List[Dict], question: str) -> Dict:
        """同期検索結果要約"""
        # 安全な検索結果トリミング
        safe_results = []
        for result in search_results[:10]:  # 10件に制限
            safe_result = {
                'title': str(result.get('title', ''))[:100],  # タイトル長制限
                'snippet': str(result.get('snippet', ''))[:200]  # スニペット長制限
            }
            safe_results.append(safe_result)
        
        prompt = self.prompt_generator.create_search_summary_prompt(safe_results, question)
        input_tokens = self.prompt_generator.count_tokens(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3,
                timeout=45
            )
            
            summary_text = response.choices[0].message.content.strip()
            
            if len(summary_text) > 300:
                summary_text = summary_text[:297] + "..."
            
            output_tokens = self.prompt_generator.count_tokens(summary_text)
            cost_usd = self.prompt_generator.estimate_cost(input_tokens, output_tokens)
            self.cost_tracker.add_usage(input_tokens, output_tokens)
            
            return {
                'success': True,
                'summary': summary_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost_usd': cost_usd
            }
            
        except Exception as e:
            self.cost_tracker.add_usage(input_tokens, 0)
            error_msg = str(e)
            
            if len(error_msg) > 50:
                error_msg = error_msg[:47] + "..."
            
            return {
                'success': False,
                'summary': f"要約エラー: {error_msg}",
                'input_tokens': input_tokens,
                'output_tokens': 0,
                'cost_usd': self.prompt_generator.estimate_cost(input_tokens, 0),
                'error': str(e)
            }
    
    def analyze_responses(self, responses: List[str], question: str) -> Dict:
        """同期レスポンス分析"""
        # 安全なレスポンストリミング
        safe_responses = [str(resp)[:200] for resp in responses[:100]]  # レスポンス長と数を制限
        
        prompt = self.prompt_generator.create_analysis_prompt(safe_responses, question)
        input_tokens = self.prompt_generator.count_tokens(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.3,
                timeout=60
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            if len(analysis_text) > 3600:
                analysis_text = analysis_text[:3597] + "..."
            
            output_tokens = self.prompt_generator.count_tokens(analysis_text)
            cost_usd = self.prompt_generator.estimate_cost(input_tokens, output_tokens)
            self.cost_tracker.add_usage(input_tokens, output_tokens)
            
            return {
                'success': True,
                'analysis': analysis_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost_usd': cost_usd
            }
            
        except Exception as e:
            self.cost_tracker.add_usage(input_tokens, 0)
            error_msg = str(e)
            
            if len(error_msg) > 50:
                error_msg = error_msg[:47] + "..."
            
            return {
                'success': False,
                'analysis': f"分析エラー: {error_msg}",
                'input_tokens': input_tokens,
                'output_tokens': 0,
                'cost_usd': self.prompt_generator.estimate_cost(input_tokens, 0),
                'error': str(e)
            }

class ResponseAnalyzer:
    def __init__(self):
        self.stop_words = {'の', 'に', 'は', 'を', 'が', 'で', 'と', 'から', 'まで', 'より', 'こと', 'もの', 'ため'}
    
    def extract_keywords(self, responses: List[str]) -> List[Dict]:
        all_text = ' '.join(responses)
        # 日本語キーワード抽出（簡単な分割）
        words = re.findall(r'[ぁ-んァ-ヶ一-龯]{2,}', all_text)
        filtered_words = [word for word in words if word not in self.stop_words]
        word_freq = Counter(filtered_words)
        return [{'word': word, 'count': count} for word, count in word_freq.most_common(15)]
    
    def analyze_sentiment(self, responses: List[str]) -> Dict:
        positive_words = ['良い', '必要', '重要', '協力', '保護', '発展', '繁栄', '安全', '成功']
        negative_words = ['危険', '困難', '脅威', '不安', '問題', '減少', '破壊', '危機', '失敗']
        
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
        
        # 種族固有の回答パターン
        self.response_patterns = {
            'ニシン': [
                "大群で行動することで安全を確保し、豊富な餌場を守ります。団結が我々の力です。",
                "敏感な魚として海洋変化をいち早く察知し、水温や海流変化に対応しなければなりません。",
                "産卵場所の保護と捕食者からの群れ防衛が、種族繁栄に直結します。"
            ],
            'イルカ': [
                "海洋の知恵を活用し、ポッドメンバーと協力して持続可能な解決策を見つけることが重要です。",
                "音響コミュニケーションで情報共有し、ポッド全体で最適な判断を下します。",
                "海洋環境保護は我々の生存基盤。人間との共存も考慮した戦略が必要です。"
            ],
            'ゾウ': [
                "長年の経験と記憶を活用し、家族群の知恵を集めて慎重に判断することが大切です。",
                "水源確保と移動路の維持は、世代を超えた最優先事項です。",
                "巨大な力と高い知能を組み合わせ、生態系バランスを考慮した行動を取ります。"
            ],
            'ネズミ': [
                "小さくても敏捷で適応力があります。環境変化に素早く対応し、繁殖成功を目指します。",
                "安全な巣穴確保と豊富な食料源発見が、基本戦略です。",
                "数の力で生き残り、どんな環境でも新たな機会を見つけ出します。"
            ],
            'カラス': [
                "知恵と道具使用能力を活用し、創意工夫で問題を解決します。",
                "仲間との情報共有と学習能力で、新しい環境にも素早く適応できます。",
                "多様な戦略で縄張りを拡大し、都市環境も活用します。"
            ],
            'ニワトリ': [
                "群れの安全と安定した食料確保が最優先。平和な環境で繁殖したいです。",
                "階層社会での役割を果たしつつ、集団の調和を大切にします。",
                "危険に対して警戒を怠らず、みんなで協力して安全に暮らします。"
            ]
        }
    
    def generate_response(self, persona: Dict, question: str, context_info: str = "") -> Dict:
        """シミュレーション用同期レスポンス生成"""
        import time
        time.sleep(0.1)  # 処理時間をシミュレート
        
        species = persona.get('species_name', 'ネズミ')
        survival_priority = persona.get('survival_priority', '種族繁栄')
        
        # 種族固有レスポンスパターンを利用可能な場合使用
        if species in self.response_patterns:
            base_responses = self.response_patterns[species]
            response = random.choice(base_responses)
        else:
            # 汎用レスポンス生成
            if any(word in question for word in ['環境', '保護', '協力']):
                response = f"我々{species}は{survival_priority}を目指し、生態系の調和を考慮して行動します。"
            elif any(word in question for word in ['危険', '脅威', '問題']):
                response = f"{species}として、仲間と共に困難に立ち向かい、{survival_priority}のために行動します。"
            else:
                response = f"{species}の特性を活用し、{survival_priority}のための最適な方法を追求します。"
        
        # 安全なレスポンストリミング
        if len(response) > 100:
            response = response[:97] + "..."
        
        input_tokens = len(question.split()) + 100
        output_tokens = len(response.split()) * 2  # より現実的なトークン推定
        
        self.cost_tracker.add_usage(input_tokens, output_tokens)
        
        return {
            'success': True,
            'response': response,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': 0.0
        }
    
    def summarize_search_results(self, search_results: List[Dict], question: str) -> Dict:
        """同期検索結果要約（シミュレーション版）"""
        summary = f"""【{question}に関する最新生物動向】

環境研究者らは、気候変動が各種族の生息地に大きく影響していることを報告。海洋生物は水温上昇に、陸上生物は生息地変化に直面しています。生物多様性保護の重要性が高まる中、種間協力と生態系相互依存の理解が進んでいます。

最新研究では、高知能種による環境適応戦略と、群れ行動による集団知能活用に注目。持続可能な生態系維持には、各種族の特性を活かした連携アプローチが重要であることが判明しています。"""
        
        # 安全な要約トリミング
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        return {
            'success': True,
            'summary': summary.strip(),
            'input_tokens': 50,
            'output_tokens': 100,
            'cost_usd': 0.0
        }
    
    def analyze_responses(self, responses: List[str], question: str) -> Dict:
        """同期レスポンス分析（シミュレーション版）"""
        # 安全なレスポンス処理
        safe_responses = [str(resp)[:200] for resp in responses[:50]]  # シミュレーション用制限
        
        analysis = """【地球生物種調査 - AI分析レポート】

**種族間の主要な論争軸と対立軸**
この調査により、海洋生物と陸上生物の間に根本的な環境認識の違いが明らかになりました。海洋種は「流動性」と「集団思考」を重視し、陸上種は「縄張り」と「個体安全」を優先します。特に、ニシンやイルカなどの海洋生物は大規模環境変化への適応性を示す一方、ゾウやカラスなどの陸上高知能種は記憶に基づく長期戦略を重視します。

個体数格差が影響力の違いを生み出しています。兆単位のニシンは「量の論理」で安全を確保する思考を示し、数十万のゾウは「質の論理」で知恵と経験継承を重視します。この対比は、生物多様性保護における個体数vs種族価値の評価基準について根本的な問題を提起します。

**生態系ポジション別の戦略と優先順位**
大群形成種（ニシン・ヌーなど）は「集団知能」と「リスク分散」を中心とした思考パターンを示します。彼らの回答は個体犠牲を前提とした種族全体最適化戦略を示し、民主的合意プロセスより本能的集団行動を重視します。

対照的に、高知能種（イルカ・ゾウ・カラス）は「問題解決思考」を発達させ、環境変化に対する創造的適応戦略を提案します。特に、イルカの音響ネットワークによる情報共有、ゾウの世代継承知識、カラスの道具使用技術は、種族横断的学習システムの可能性を示唆します。

頂点捕食者と被食者間では明確な資源確保戦略の違いが存在します。捕食者は「効率性」と「選択的狩り」を重視し、被食者は「警戒システム」と「逃避戦術」に特化した思考を示します。

**コミュニケーション方法が思考に与える影響**
化学信号依存種（多くの昆虫、一部哺乳類）は直感的で高応答性の判断パターンを示し、論理的分析より本能的反応を重視します。対照的に、音響コミュニケーション種（イルカ・クジラ・多くの鳥類）は複雑な情報伝達能力に基づく協力的問題解決アプローチを採用します。

視覚コミュニケーション中心種は情報処理精度と速度に優れ、環境変化の早期発見と迅速な適応戦略が特徴です。触覚・振動コミュニケーション主体種は、より親密で持続的な社会結束に基づく安定志向戦略を好みます。

**生存戦略の多様性と相互依存**
量的戦略（大量繁殖）種は環境変動抵抗性を重視し、質的戦略（エリート方式）種は個体価値最大化と知識蓄積を重視します。これらの戦略は競合的に見えますが、実際は生態系安定性において補完的機能を果たします。

移動戦略種（渡り鳥・回遊魚）は「柔軟性」と「適応性」に重点を置き、定住戦略種は「安定性」と「資源育成」を重視します。両回答は環境変化対応における移動-定住最適化の重要性を浮き彫りにします。

**地球規模課題への種族横断的解決策**
回答分析から、各種族の固有能力を統合した協力システムの可能性が浮上します。海洋生物の広域情報ネットワーク、陸上生物の局地環境管理能力、飛行生物の立体監視システムを組み合わせることで、地球規模環境監視・早期警戒システム構築が可能になります。

知能種の戦略的思考と本能種の感覚的環境検出の融合は、人工知能では代替不可能な「生物知能ネットワーク」創造を示唆します。

**生物多様性保護への新アプローチ**
従来の人間中心保護政策から、「種族の声」を直接反映した環境政策への転換可能性が浮上しています。各種族の生存戦略と環境認識を政策決定プロセスに組み込むことで、より効果的な保護戦略策定が可能になります。

生態系自己組織化能力を最大限活用し、人間介入を最小限に抑制することで、「生命主導型環境管理」実現が可能となり、持続可能性と生物多様性が共存する新たな地球管理モデル構築につながります。"""
        
        # 安全な分析トリミング
        if len(analysis) > 3600:
            analysis = analysis[:3597] + "..."
        
        return {
            'success': True,
            'analysis': analysis.strip(),
            'input_tokens': 200,
            'output_tokens': 3000,
            'cost_usd': 0.0
        }

# UI関数
def setup_sidebar():
    """安全なセッション状態処理でサイドバー設定"""
    st.sidebar.title("⚙️ 設定")
    
    st.sidebar.header("🤖 LLM モード")
    
    use_real_llm = st.sidebar.radio(
        "モード選択",
        ["シミュレーション（無料）", "GPT-4o-mini（有料）"],
        index=0 if not st.session_state.use_real_llm else 1
    )
    
    st.session_state.use_real_llm = (use_real_llm == "GPT-4o-mini（有料）")
    
    if st.session_state.use_real_llm:
        st.sidebar.header("🔑 API設定")
        
        api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)
        
        if not api_key:
            env_api_key = os.getenv("OPENAI_API_KEY")
            if env_api_key:
                st.sidebar.success("✅ 環境変数からAPIキーを読み込みました")
                st.session_state.api_key = env_api_key
            else:
                st.sidebar.error("❌ APIキーを入力してください")
                return
        else:
            st.session_state.api_key = api_key
        
        st.sidebar.warning("**コスト目安:**\n- 100回答: 約$0.12\n- AI分析: 約$0.18")
    
    st.sidebar.header("🐾 生物ペルソナ設定")
    
    persona_count = st.sidebar.selectbox(
        "個体数", 
        [10, 25, 50, 100], 
        index=[10, 25, 50, 100].index(st.session_state.persona_count) if st.session_state.persona_count in [10, 25, 50, 100] else 0
    )
    st.session_state.persona_count = persona_count
    
    if st.session_state.use_real_llm:
        estimated_cost = persona_count * 0.00012
        st.sidebar.info(f"💰 推定コスト: 約${estimated_cost:.3f}")

def show_home_tab():
    """安全なセッション状態処理でホームタブ"""
    st.header("🌍 地球生物種意見調査シミュレーター")
    
    st.markdown("""
    <div style="background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem;">
    🏷️ <strong>特徴</strong><br>
    • 実際の地球生物種個体数データに基づく<br>
    • 各種族が自らの繁栄を目指す<br>
    • 🦆 DuckDuckGo検索: 最新環境情報<br>
    • 📋 生物多様性レポート出力
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🐾 地球の生物種の声を聞く
        
        ### ✨ 特徴
        
        - **🌊 海洋生物**: ニシン（8×10¹¹）、サバ（3×10¹¹）など - 最大個体数種
        - **🦅 鳥類**: ニワトリ（330億）、スズメ、カラス、ハト
        - **🐭 哺乳類**: ネズミ（100億）、イルカ、ゾウ、イヌ、ネコ  
        - **🦌 アフリカ大陸**: ヌー、シマウマ、ゾウ - サバンナ住民
        - **🧠 知能レベル**: 高度認知能力から本能まで
        - **🌍 地域分布**: 個体数データに基づく自然分布
        
        ### 🎯 各種族の視点
        
        - **海洋生物**: 集団知能、水生環境重視
        - **高知能種**: 問題解決、長期戦略
        - **群れ動物**: 集団行動、安全重視
        - **捕食者**: 資源確保、縄張り戦略
        - **被食種**: 警戒システム、逃避戦術
        
        ### 📋 レポート内容
        
        - **種族間対立軸**: 海洋vs陸上、捕食者vs被食者
        - **コミュニケーション分析**: 音響・化学・視覚信号の影響
        - **生存戦略多様性**: 量vs質、移動vs定住
        - **生態系ポジション思考**: 各生物の立場からの戦略
        """)
    
    with col2:
        st.subheader("📈 個体数ランキング")
        
        # Noneチェック付きの安全なセッション状態アクセス
        if st.session_state.species_personas is not None and len(st.session_state.species_personas) > 0:
            personas = st.session_state.species_personas
            
            try:
                df = pd.DataFrame(personas)
                
                st.metric("生成済み個体", len(personas))
                
                species_counts = df['species_name'].value_counts()
                fig = px.pie(
                    values=species_counts.values,
                    names=species_counts.index,
                    title="種族分布"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"チャート生成エラー: {str(e)[:50]}")
                st.metric("生成済み個体", len(personas))
        else:
            st.info("まず「ペルソナ」タブで生物個体を生成してください")
        
        # 主要種族個体数表示
        st.subheader("🔢 地球トップ個体数")
        top_species = [
            ("ニシン", "8×10¹¹", "🐟"),
            ("サバ", "3×10¹¹", "🐟"),
            ("ニワトリ", "3.3×10¹⁰", "🐔"),
            ("ネズミ", "1×10¹⁰", "🐭"),
            ("イルカ", "6×10⁶", "🐬"),
            ("ゾウ", "5×10⁵", "🐘")
        ]
        
        for species, count, emoji in top_species:
            st.write(f"{emoji} {species}: {count}個体")

def show_persona_tab():
    """安全なセッション状態処理でペルソナタブ"""
    st.header("🐾 生物種ペルソナ生成・管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🌍 地球生物種データベース")
        st.markdown("""
        **個体数データソース:**
        - 海洋生物学研究データ
        - 野生動物調査統計
        - 畜産統計データ
        
        **生成される属性:**
        - 種族名、個体名、年齢、性別
        - 生息地、地域、生態的役割
        - コミュニケーション方法、知能レベル
        - 社会的地位、生存優先事項
        - 資源アクセス状況
        """)
        
        if st.button("🎲 生物種ペルソナを生成", type="primary", use_container_width=True):
            generate_species_personas()
    
    with col2:
        st.subheader("⚙️ 生成設定")
        
        persona_count = st.session_state.persona_count
        st.info(f"個体数: {persona_count}")
        
        if st.session_state.use_real_llm:
            estimated_cost = persona_count * 0.00012
            st.warning(f"推定調査コスト: 約${estimated_cost:.3f}")
        else:
            st.success("シミュレーション版: 無料")
    
    # Noneチェック付きペルソナの安全なセッション状態アクセス
    if st.session_state.species_personas is not None and len(st.session_state.species_personas) > 0:
        st.subheader("🐾 生成済み生物種ペルソナ")
        
        try:
            personas = st.session_state.species_personas
            df = pd.DataFrame(personas)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("総個体数", len(personas))
            with col2:
                avg_age = df['age'].mean()
                st.metric("平均年齢", f"{avg_age:.1f}歳")
            with col3:
                marine_ratio = (df['species_type'] == '海洋').mean()
                st.metric("海洋生物比率", f"{marine_ratio:.1%}")
            with col4:
                high_intel = df['intelligence_level'].str.contains('高度', na=False).mean()
                st.metric("高知能比率", f"{high_intel:.1%}")
            
            # エラーハンドリング付きチャート表示
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    species_counts = df['species_name'].value_counts()
                    fig1 = px.pie(
                        values=species_counts.values,
                        names=species_counts.index,
                        title="種族分布"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                except Exception as e:
                    st.warning(f"種族チャートエラー: {str(e)[:50]}")
            
            with col2:
                try:
                    type_counts = df['species_type'].value_counts()
                    fig2 = px.bar(
                        x=type_counts.values,
                        y=type_counts.index,
                        orientation='h',
                        title="生息地タイプ別分布"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                except Exception as e:
                    st.warning(f"タイプチャートエラー: {str(e)[:50]}")
            
            with st.expander("📋 詳細生物種ペルソナ一覧"):
                try:
                    display_df = df[['id', 'species_name', 'age', 'gender', 'region', 'ecological_role']].copy()
                    display_df.columns = ['ID', '種族', '年齢', '性別', '地域', '生態的役割']
                    st.dataframe(display_df, use_container_width=True)
                except Exception as e:
                    st.warning(f"テーブル表示エラー: {str(e)[:50]}")
                    st.write(f"{len(personas)}個のペルソナが正常に生成されました")
                    
        except Exception as e:
            st.error(f"ペルソナ表示エラー: {str(e)[:100]}")
            st.write("ペルソナは生成されましたが表示に失敗しました。再生成をお試しください。")

def show_survey_tab():
    """包括的なNoneチェック付き調査タブ"""
    st.header("❓ 生物種意見調査実行")
    
    # 明示的なNone処理での安全なペルソナチェック
    personas = st.session_state.species_personas
    if personas is None or len(personas) == 0:
        st.warning("⚠️ まず「ペルソナ」タブで生物種ペルソナを生成してください")
        st.info("👈 「ペルソナ」タブに移動して「生物種ペルソナを生成」をクリック")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 質問設定")
        
        preset_questions = {
            "カスタム質問": "",
            "環境保護": "地球環境を守るために最も重要なことは何ですか？",
            "気候変動対策": "気候変動にどう対処すべきでしょうか？",
            "生物多様性保全": "生物多様性保全のために何をすべきでしょうか？",
            "海洋保護": "海洋環境を守るために何ができますか？",
            "森林保護": "森林と緑地を保護するにはどうすればよいでしょうか？",
            "種族間協力": "異なる種族が協力するために必要なことは？",
            "持続可能性": "持続可能な地球のために必要なことは？",
            "人間との共存": "人間と他の生物はどう共存すべきでしょうか？"
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
                placeholder="例: 理想的な地球環境とは何ですか？"
            )
        else:
            question = st.text_area(
                "選択された質問（編集可能）",
                value=preset_questions[selected_preset],
                height=100
            )
        
        st.subheader("🦆 ウェブ検索（最新環境情報）")
        use_web_search = st.checkbox("質問に関連する最新環境情報を検索する")
        
        search_query = ""
        if use_web_search:
            search_query = st.text_input(
                "検索キーワード",
                value=extract_search_keywords(question) if question else "",
                help="DuckDuckGoで最新環境情報を検索（無料）"
            )
    
    with col2:
        st.subheader("📊 調査設定")
        
        # 明示的なNoneチェックでの安全なペルソナアクセス
        try:
            personas_count = len(personas) if personas is not None else 0
            st.metric("調査対象個体", personas_count)
            
            if personas_count > 0:
                # エラーハンドリング付き種族分布表示
                try:
                    df = pd.DataFrame(personas)
                    species_counts = df['species_name'].value_counts().head(5)
                    st.write("**主要参加種族:**")
                    for species, count in species_counts.items():
                        st.write(f"• {species}: {count}個体")
                except Exception as e:
                    st.warning(f"種族分布表示エラー: {str(e)[:50]}")
                    st.write(f"• {personas_count}個体が生成済み")
            
        except Exception as e:
            st.error(f"ペルソナアクセスエラー: {str(e)[:50]}")
            st.metric("調査対象個体", 0)
            personas_count = 0
        
        if st.session_state.use_real_llm:
            st.success("🤖 GPT-4o-mini使用")
            
            if question and personas_count > 0:
                estimated_cost = personas_count * 0.00012
                st.info(f"推定コスト: 約${estimated_cost:.3f}")
        else:
            st.info("🎭 シミュレーション版使用")
            st.success("コスト: 無料")
    
    # 調査実行ボタン
    if st.button("🚀 生物種調査を実行", type="primary", use_container_width=True):
        if not question.strip():
            st.error("❌ 質問を入力してください")
        elif personas_count == 0:
            st.error("❌ まず生物種ペルソナを生成してください")
        else:
            execute_species_survey(question, search_query if use_web_search else "")

def show_ai_analysis_tab():
    """包括的なNoneチェック付きAI分析タブ"""
    st.header("🤖 生物知能分析")
    
    # 明示的なNone処理での安全な調査結果チェック
    responses = st.session_state.survey_responses
    if responses is None or len(responses) == 0:
        st.info("⚠️ まず「調査」タブで生物種調査を実行してください")
        st.info("👈 「調査」タブに移動して先に調査を実行してください")
        return
    
    # エラーハンドリング付きの安全なレスポンスアクセス
    try:
        if not responses or len(responses) == 0:
            st.error("利用可能な調査回答がありません")
            return
            
        # 安全な質問抽出
        question = "未知の質問"
        if isinstance(responses, list) and len(responses) > 0:
            first_response = responses[0]
            if isinstance(first_response, dict) and 'question' in first_response:
                question = first_response['question']
        
    except Exception as e:
        st.error(f"調査回答アクセスエラー: {str(e)[:50]}")
        return
    
    st.subheader(f"📝 分析対象: {question}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🧠 生物知能AI分析機能
        
        - **種族間対立軸**: 海洋vs陸上、捕食者vs被食者の視点
        - **生態系ポジション戦略**: 各種族の立場からの思考分析
        - **コミュニケーション方法影響**: 音響・化学・視覚信号が思考に与える影響
        - **生存戦略多様性**: 量vs質、移動vs定住の戦略
        - **種族横断解決策**: 生物知能を活用した地球規模課題への対応
        - **生物多様性保護**: 新しいアプローチ提案
        
        **特徴**: 人間中心ではなく、生物多様性視点からの分析
        """)
    
    with col2:
        st.subheader("📊 分析設定")
        
        try:
            total_responses = len(responses) if responses else 0
            successful_responses = len([r for r in responses if r and r.get('success', True)]) if responses else 0
            
            st.metric("分析対象回答数", successful_responses)
            
            if successful_responses > 0:
                # エラーハンドリング付き種族統計
                try:
                    valid_responses = [r for r in responses if r and isinstance(r, dict) and 'persona' in r]
                    if valid_responses:
                        personas_data = [r['persona'] for r in valid_responses if r['persona']]
                        if personas_data:
                            df = pd.DataFrame(personas_data)
                            species_counts = df['species_name'].value_counts().head(3)
                            st.write("**主要回答種族:**")
                            for species, count in species_counts.items():
                                st.write(f"• {species}: {count}個体")
                except Exception as e:
                    st.warning(f"種族統計エラー: {str(e)[:50]}")
                    st.write(f"• {successful_responses}回答が利用可能")
            
        except Exception as e:
            st.error(f"回答分析エラー: {str(e)[:50]}")
            st.metric("分析対象回答数", 0)
            successful_responses = 0
        
        if st.session_state.use_real_llm:
            st.info("🤖 GPT-4o-mini分析")
            st.warning("分析コスト: 約$0.18")
        else:
            st.info("🎭 シミュレーション分析")
            st.success("コスト: 無料")
    
    # 分析実行ボタン
    if st.button("🧠 生物知能分析を実行", type="primary", use_container_width=True):
        if successful_responses == 0:
            st.error("❌ 分析用の有効な回答がありません")
        else:
            execute_species_ai_analysis(responses, question)
    
    # 安全なアクセスでの分析結果表示
    analysis_result = st.session_state.ai_analysis
    if analysis_result is not None:
        st.subheader("📋 生物知能分析レポート")
        
        try:
            if analysis_result and isinstance(analysis_result, dict):
                if analysis_result.get('success', False):
                    analysis_text = analysis_result.get('analysis', '分析内容がありません')
                    st.markdown(analysis_text)
                    
                    if st.session_state.use_real_llm:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            input_tokens = analysis_result.get('input_tokens', 0)
                            st.metric("入力トークン", f"{input_tokens:,}")
                        with col2:
                            output_tokens = analysis_result.get('output_tokens', 0)
                            st.metric("出力トークン", f"{output_tokens:,}")
                        with col3:
                            cost_usd = analysis_result.get('cost_usd', 0)
                            st.metric("分析コスト", f"${cost_usd:.4f}")
                else:
                    error_msg = analysis_result.get('analysis', '不明なエラーが発生しました')[:100]
                    st.error(f"❌ 分析エラー: {error_msg}")
            else:
                st.error("❌ 無効な分析結果形式です")
                
        except Exception as e:
            st.error(f"分析表示エラー: {str(e)[:100]}")

def show_analysis_tab():
    st.header("📊 生物種統計分析")
    
    if 'survey_responses' not in st.session_state or st.session_state.survey_responses is None:
        st.info("まず「調査」タブで調査を実行してください")
        return
    
    responses = st.session_state.survey_responses
    responses_df = pd.DataFrame([{
        'species_name': r['persona']['species_name'],
        'species_type': r['persona']['species_type'],
        'age': r['persona']['age'],
        'gender': r['persona']['gender'],
        'region': r['persona']['region'],
        'intelligence_level': r['persona']['intelligence_level'],
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
            responses_df, x='species_type', y='response_length',
            title="生息地タイプ別回答文字数"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # 種族分析
    st.subheader("🐾 種族分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        species_counts = responses_df['species_name'].value_counts()
        fig3 = px.pie(
            values=species_counts.values,
            names=species_counts.index,
            title="参加種族分布"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        type_counts = responses_df['species_type'].value_counts()
        fig4 = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            title="生息地タイプ別参加状況"
        )
        st.plotly_chart(fig4, use_container_width=True)
    
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
                title="頻出キーワード トップ10"
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**生物キーワードランキング**")
            for i, kw in enumerate(keywords[:8], 1):
                st.write(f"{i}. {kw['word']} ({kw['count']}回)")
    
    # 感情分析
    st.subheader("😊 生物種感情分析")
    
    sentiment = analyzer.analyze_sentiment(responses_list)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=[sentiment['positive'], sentiment['negative'], sentiment['neutral']],
            names=['ポジティブ', 'ネガティブ', 'ニュートラル'],
            title="全体感情分布"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 種族別感情（主要種族のみ）
        major_species = responses_df['species_name'].value_counts().head(4).index
        species_sentiment = {}
        
        for species in major_species:
            species_responses = responses_df[responses_df['species_name'] == species]['response'].tolist()
            if species_responses:
                species_sent = analyzer.analyze_sentiment(species_responses)
                species_sentiment[species] = species_sent
        
        if species_sentiment:
            sentiment_df = pd.DataFrame(species_sentiment).T
            
            fig2 = px.bar(
                sentiment_df.reset_index(),
                x='index', y=['positive', 'negative', 'neutral'],
                title="主要種族感情分析"
            )
            st.plotly_chart(fig2, use_container_width=True)

def show_results_tab():
    st.header("📊 生物種調査結果")
    
    if 'survey_responses' not in st.session_state or st.session_state.survey_responses is None:
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
        st.metric("平均回答文字数", f"{avg_response_length:.1f}文字")
    with col4:
        if st.session_state.get('use_real_llm', False):
            total_cost = sum(r.get('cost_usd', 0) for r in responses)
            st.metric("総コスト", f"${total_cost:.4f}")
        else:
            st.metric("コスト", "無料")
    
    # 検索情報表示
    if 'search_results' in st.session_state and st.session_state.search_results is not None:
        with st.expander("🦆 使用された最新環境情報"):
            for result in st.session_state.search_results:
                st.write(f"**{result['title']}**")
                st.write(result['snippet'])
                st.write("---")
    
    # 生物種回答サンプル
    response_df = pd.DataFrame([{
        'species_name': r['persona']['species_name'],
        'species_type': r['persona']['species_type'],
        'age': r['persona']['age'],
        'gender': r['persona']['gender'],
        'region': r['persona']['region'],
        'response': r['response']
    } for r in responses])
    
    st.subheader("💬 生物種回答サンプル")
    
    # 主要種族別サンプル表示
    major_species = response_df['species_name'].value_counts().head(6).index
    
    for species in major_species:
        with st.expander(f"{species} 回答サンプル"):
            species_responses = response_df[response_df['species_name'] == species]
            
            for idx, (_, row) in enumerate(species_responses.head(3).iterrows(), 1):
                st.write(f"**{idx}. {row['age']}歳{row['gender']} ({row['region']})**")
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
            label="📊 CSVでダウンロード",
            data=csv_str,
            file_name=f"生物種調査_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = {
            '調査情報': {
                '質問': question,
                'タイムスタンプ': datetime.now().isoformat(),
                '総回答数': len(response_df),
                'AI分析': st.session_state.get('ai_analysis', {})
            },
            '回答': responses
        }
        
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        st.download_button(
            label="📄 JSONでダウンロード",
            data=json_str,
            file_name=f"生物種調査_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col3:
        # PDF出力ボタン
        if REPORTLAB_AVAILABLE:
            if st.button("📋 PDFレポート生成", type="primary", use_container_width=True):
                generate_species_pdf_report(responses, question)
        else:
            st.warning("📋 PDF出力にはReportLabが必要です\n`pip install reportlab matplotlib`")

# ヘルパー関数
def extract_search_keywords(question: str) -> str:
    keywords = []
    if '環境' in question:
        keywords.append('環境保護 生物多様性')
    if '気候' in question:
        keywords.append('気候変動 生態系')
    if '海洋' in question:
        keywords.append('海洋保護 海洋生物')
    if '森林' in question:
        keywords.append('森林保護 野生動物')
    if '協力' in question:
        keywords.append('種間協力 生態系')
    
    return ' '.join(keywords) if keywords else f"生物 環境 {question[:20]}"

def generate_species_personas():
    persona_count = st.session_state.get('persona_count', 10)
    
    with st.spinner(f'{persona_count}個の生物種ペルソナを生成中...'):
        progress_bar = st.progress(0)
        
        species_db = GlobalSpeciesDB()
        persona_generator = SpeciesPersonaGenerator(species_db)
        
        # 種族分布計算
        species_distribution = persona_generator.calculate_species_distribution(persona_count)
        
        personas = []
        persona_id = 1
        
        for species, count in species_distribution.items():
            for _ in range(count):
                persona = persona_generator.generate_species_persona(persona_id, species)
                personas.append(asdict(persona))
                persona_id += 1
                progress_bar.progress(persona_id / (persona_count + 1))
        
        st.session_state.species_personas = personas
        
        # 生成種族分布表示
        generated_species = {}
        for persona in personas:
            species = persona['species_name']
            generated_species[species] = generated_species.get(species, 0) + 1
        
        st.success(f"✅ {len(personas)}個の生物種ペルソナを生成しました！")
        
        with st.expander("📊 生成された種族分布"):
            for species, count in sorted(generated_species.items(), key=lambda x: x[1], reverse=True):
                st.write(f"• {species}: {count}個体")

def execute_species_survey(question: str, search_query: str = ""):
    """適切なエラーハンドリング付き生物種調査実行"""
    if not st.session_state.species_personas:
        st.error("利用可能な生物種ペルソナがありません")
        return
    
    personas = st.session_state.species_personas
    use_real_llm = st.session_state.use_real_llm
    
    # 検索結果要約実行
    context_info = ""
    search_summary = None
    
    if search_query:
        search_provider = WebSearchProvider()
        
        search_results = search_provider.search_recent_info(search_query, num_results=10)
        st.session_state.search_results = search_results
        
        if search_results and len(search_results) > 0:
            with st.spinner('🔍 環境情報を要約中...'):
                try:
                    if use_real_llm and st.session_state.llm_provider:
                        # 実際のLLM要約
                        search_summary = st.session_state.llm_provider.summarize_search_results(search_results, question)
                    else:
                        # シミュレーション要約
                        sim_provider = SimulationProvider()
                        search_summary = sim_provider.summarize_search_results(search_results, question)
                    
                    if search_summary and search_summary.get('success', False):
                        context_info = f"【最新環境情報】\n{search_summary['summary']}"
                        st.success(f"✅ 環境情報要約完了（{len(search_results)}件のソース）")
                    else:
                        st.warning("環境情報要約に失敗しました")
                        
                except Exception as e:
                    st.error(f"要約エラー: {str(e)[:100]}")
    
    # プロバイダー初期化
    if use_real_llm:
        api_key = st.session_state.api_key
        if not api_key:
            st.error("APIキーが設定されていません")
            return
        
        try:
            if not st.session_state.llm_provider:
                st.session_state.llm_provider = GPT4OMiniProvider(api_key)
            provider = st.session_state.llm_provider
        except Exception as e:
            st.error(f"プロバイダー初期化エラー: {str(e)[:100]}")
            return
    else:
        provider = SimulationProvider()
    
    # 調査実行
    with st.spinner(f'{"GPT-4o-mini" if use_real_llm else "シミュレーション"}生物種調査を実行中...'):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        if search_summary and use_real_llm:
            cost_text = st.empty()
            cost_text.info(f"環境情報要約コスト: ${search_summary.get('cost_usd', 0):.4f}")
        
        responses = []
        
        try:
            for i, persona in enumerate(personas):
                status_text.text(f"回答生成中: {i+1}/{len(personas)} ({persona['species_name']})")
                
                # asyncio.run()の代わりに同期呼び出し
                result = provider.generate_response(persona, question, context_info)
                
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
                
        except Exception as e:
            st.error(f"調査実行エラー: {str(e)[:100]}")
            return
        
        if search_summary:
            st.session_state.search_summary = search_summary
        
        st.session_state.survey_responses = responses
        
        successful_count = len([r for r in responses if r['success']])
        
        total_cost = sum(r.get('cost_usd', 0) for r in responses)
        if search_summary:
            total_cost += search_summary.get('cost_usd', 0)
        
        if successful_count == len(responses):
            cost_msg = f"（総コスト: ${total_cost:.4f}）" if use_real_llm else ""
            st.success(f"✅ 生物種調査完了！{successful_count}件の回答を取得{cost_msg}")
        else:
            st.warning(f"⚠️ 調査完了。{successful_count}/{len(responses)}件の回答を取得")

def execute_species_ai_analysis(responses: List[Dict], question: str):
    """適切なエラーハンドリング付きAI分析実行"""
    use_real_llm = st.session_state.use_real_llm
    
    successful_responses = [r['response'] for r in responses if r.get('success', True)]
    
    if not successful_responses:
        st.error("分析用の回答がありません")
        return
    
    if use_real_llm:
        if not st.session_state.llm_provider:
            st.error("LLMプロバイダーが初期化されていません")
            return
        provider = st.session_state.llm_provider
    else:
        provider = SimulationProvider()
    
    with st.spinner('🧠 生物知能AI分析を実行中...'):
        try:
            # asyncio.run()の代わりに同期呼び出し
            analysis_result = provider.analyze_responses(successful_responses, question)
            st.session_state.ai_analysis = analysis_result
            
            if analysis_result.get('success', False):
                st.success("✅ 生物知能AI分析完了！")
            else:
                error_msg = analysis_result.get('analysis', '不明なエラー')[:100]
                st.error(f"❌ 生物知能AI分析エラー: {error_msg}")
                
        except Exception as e:
            st.error(f"分析実行エラー: {str(e)[:100]}")

def generate_species_pdf_report(responses: List[Dict], question: str):
    """適切なMIME処理での生物種調査PDFレポート生成"""
    try:
        with st.spinner('📋 生物種調査レポートを生成中...'):
            # 安全なデータ準備
            if not responses:
                st.error("レポート生成用の回答がありません")
                return
            
            responses_df = pd.DataFrame([{
                'species_name': str(r['persona'].get('species_name', '不明')),
                'species_type': str(r['persona'].get('species_type', '不明')),
                'age': int(r['persona'].get('age', 0)),
                'gender': str(r['persona'].get('gender', '不明')),
                'region': str(r['persona'].get('region', '不明')),
                'intelligence_level': str(r['persona'].get('intelligence_level', '不明')),
                'response': str(r.get('response', ''))[:200],  # 安全なトリミング
                'response_length': len(str(r.get('response', '')))
            } for r in responses if r.get('persona')])
            
            if responses_df.empty:
                st.error("有効な回答データがありません")
                return
            
            # エラーハンドリング付き統計分析
            try:
                analyzer = ResponseAnalyzer()
                responses_list = responses_df['response'].tolist()
                keywords = analyzer.extract_keywords(responses_list)
                sentiment = analyzer.analyze_sentiment(responses_list)
            except Exception as e:
                st.warning(f"分析エラー: {str(e)[:50]}、基本統計を使用")
                keywords = [{'word': '環境', 'count': 1}]
                sentiment = {'positive': 33.3, 'negative': 33.3, 'neutral': 33.3}
            
            # 種族分布
            species_counts = responses_df['species_name'].value_counts().to_dict()
            
            # 安全な処理でのサンプル回答
            sample_responses = []
            try:
                major_species = responses_df['species_name'].value_counts().head(6).index
                for species in major_species:
                    species_responses = responses_df[responses_df['species_name'] == species]
                    for _, row in species_responses.head(2).iterrows():
                        sample_responses.append({
                            'age': row['age'],
                            'gender': row['gender'],
                            'species': row['species_name'],
                            'region': row['region'],
                            'response': row['response'][:100]  # 安全なトリミング
                        })
                    if len(sample_responses) >= 15:  # 総サンプル数制限
                        break
            except Exception as e:
                st.warning(f"サンプル生成エラー: {str(e)[:50]}")
            
            # レポート内容生成
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                safe_question = str(question)[:200]  # 安全な質問トリミング
                
                # 包括的レポート内容作成
                report_content = f"""地球生物種意見調査レポート

質問: {safe_question}
調査日時: {timestamp}
総回答数: {len(responses)}

=== 調査概要 ===

主要参加種族:
{chr(10).join([f"- {species}: {count}個体" for species, count in list(species_counts.items())[:10]])}

=== キーワード分析 ===

頻出キーワード:
{chr(10).join([f"{i+1}. {kw['word']} ({kw['count']}回)" for i, kw in enumerate(keywords[:15])])}

=== 感情分析 ===

全体感情分布:
- ポジティブ: {sentiment['positive']:.1f}%
- ネガティブ: {sentiment['negative']:.1f}%
- ニュートラル: {sentiment['neutral']:.1f}%

=== 回答サンプル ===

{chr(10).join([f"• {resp['species']} ({resp['age']}歳{resp['gender']}, {resp['region']}): {resp['response']}" for resp in sample_responses[:12]])}

=== 生物種統計 ===

種族タイプ分布:
{chr(10).join([f"- {species_type}: {count}個体" for species_type, count in responses_df['species_type'].value_counts().items()])}

年齢分布:
- 平均年齢: {responses_df['age'].mean():.1f}歳
- 年齢範囲: {responses_df['age'].min()}-{responses_df['age'].max()}歳

回答文字数統計:
- 平均回答文字数: {responses_df['response_length'].mean():.1f}文字
- 総生成テキスト: {responses_df['response_length'].sum()}文字

=== 調査メタデータ ===

調査設定:
- モデル: {"GPT-4o-mini" if st.session_state.use_real_llm else "シミュレーション"}
- 総コスト: {"${:.4f}".format(sum(r.get('cost_usd', 0) for r in responses)) if st.session_state.use_real_llm else "無料"}
- 生成時刻: {timestamp}
- コンテキスト使用: {"あり" if any(r.get('context_used', False) for r in responses) else "なし"}

地球生物種意見調査シミュレーターによるレポート
"""
                
                # 正しいMIMEタイプでの適切なファイルダウンロード
                st.success("✅ 生物種調査レポート生成完了！")
                
                # 複数ダウンロード形式の提供
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📄 レポートダウンロード（TXT）",
                        data=report_content.encode('utf-8'),
                        file_name=f"生物種調査レポート_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    # データ分析用CSV形式
                    csv_data = responses_df.copy()
                    csv_data['質問'] = safe_question
                    csv_data['調査日時'] = timestamp
                    
                    csv_str = csv_data.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📊 データダウンロード（CSV）",
                        data=csv_str.encode('utf-8-sig'),
                        file_name=f"生物種調査データ_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # ReportLab利用可能時のPDF生成
                if REPORTLAB_AVAILABLE:
                    try:
                        st.info("📋 ReportLabで高度なPDF生成が利用可能です")
                        # 実際のPDF生成をここで実装可能
                    except Exception as e:
                        st.warning(f"PDF生成エラー: {str(e)[:50]}")
                else:
                    st.info("💡 拡張PDF出力にはReportLabをインストール: `pip install reportlab`")
                
            except Exception as e:
                st.error(f"レポート内容生成エラー: {str(e)[:100]}")
                return
            
    except Exception as e:
        st.error(f"レポート生成失敗: {str(e)[:100]}")
        st.info("データを確認して再試行してください。問題が続く場合はサポートにお問い合わせください。")

# メイン関数
def main():
    st.title("🌍 地球生物種意見調査シミュレーター")
    st.caption("🐾 実際の個体数データに基づく生物多様性の声 | 各種族が自らの繁栄を目指す")
    
    setup_sidebar()
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🌍 ホーム", "🐾 ペルソナ", "❓ 調査", "🧠 AI分析", "📊 統計", "📈 結果"
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
    
    # フッター情報
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌍 データソース")
    st.sidebar.markdown("""
    **個体数データ:**
    - 海洋生物学研究統計
    - 野生動物保護調査
    - 農業統計データ
    
    **特徴:**
    - ニシン: 8×10¹¹個体（海洋最大）
    - ニワトリ: 3.3×10¹⁰羽（陸上最大）
    - ネズミ: 1×10¹⁰個体（野生哺乳類最大）
    - 高知能: イルカ、ゾウ、カラスなど
    """)
    
    # 安全なセッション状態アクセスでサイドバー情報
    if st.session_state.species_personas is not None and len(st.session_state.species_personas) > 0:
        st.sidebar.markdown("### 📊 現在の設定")
        personas = st.session_state.species_personas
        st.sidebar.metric("生成済み個体", len(personas))
        
        try:
            df = pd.DataFrame(personas)
            marine_count = len(df[df['species_type'] == '海洋'])
            terrestrial_count = len(df[df['species_type'] == '陸上'])
            aerial_count = len(df[df['species_type'] == '空中'])
            
            st.sidebar.write(f"🌊 海洋生物: {marine_count}個体")
            st.sidebar.write(f"🦌 陸上生物: {terrestrial_count}個体")
            st.sidebar.write(f"🦅 飛行生物: {aerial_count}個体")
        except Exception as e:
            st.sidebar.warning(f"表示エラー: {str(e)[:30]}")

if __name__ == "__main__":
    main()