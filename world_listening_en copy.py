# app.py - Earth Species Opinion Survey Simulator (English Streamlit Version) - FIXED
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

# Optional imports
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

# Page configuration
st.set_page_config(
    page_title="Earth Species Opinion Survey Simulator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables to prevent KeyError"""
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

# Initialize session state at startup
init_session_state()

@dataclass
class SpeciesProfile:
    id: int
    species_type: str  # 'marine', 'terrestrial', 'aerial'
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
        # Major species based on actual population data (sorted by population)
        self.species_population = {
            # Marine life (highest populations)
            'Herring': {
                'population': 8e11, 
                'habitats': ['North Atlantic', 'North Pacific'], 
                'regions': ['Arctic Ocean', 'North Pacific', 'North Atlantic'],
                'type': 'marine'
            },
            'Mackerel': {
                'population': 3e11, 
                'habitats': ['Temperate seas', 'Subarctic waters'], 
                'regions': ['Pacific', 'Atlantic', 'Indian Ocean'],
                'type': 'marine'
            },
            'Cod': {
                'population': 2e11, 
                'habitats': ['North Atlantic deep sea', 'Continental shelf'], 
                'regions': ['North Atlantic', 'Arctic Ocean'],
                'type': 'marine'
            },
            'Salmon': {
                'population': 1e11, 
                'habitats': ['North Pacific', 'Rivers'], 
                'regions': ['North Pacific', 'North American rivers', 'Asian rivers'],
                'type': 'marine'
            },
            'Tuna': {
                'population': 5e10, 
                'habitats': ['Open ocean', 'Deep sea'], 
                'regions': ['Pacific', 'Atlantic', 'Indian Ocean'],
                'type': 'marine'
            },
            
            # Birds (highest terrestrial populations)
            'Chicken': {
                'population': 3.3e10, 
                'habitats': ['Farms', 'Urban areas'], 
                'regions': ['All continents'],
                'type': 'terrestrial'
            },
            'Sparrow': {
                'population': 5e8, 
                'habitats': ['Urban areas', 'Farmland', 'Forest edges'], 
                'regions': ['Eurasia', 'North America', 'Africa'],
                'type': 'aerial'
            },
            'Crow': {
                'population': 4e8, 
                'habitats': ['Urban areas', 'Forests', 'Farmland'], 
                'regions': ['All continents'],
                'type': 'aerial'
            },
            'Pigeon': {
                'population': 3e8, 
                'habitats': ['Urban areas', 'Rocky areas'], 
                'regions': ['All continents'],
                'type': 'aerial'
            },
            
            # Mammals
            'Rat': {
                'population': 1e10, 
                'habitats': ['Urban areas', 'Farmland', 'Forests', 'Underground'], 
                'regions': ['All continents'],
                'type': 'terrestrial'
            },
            'Bat': {
                'population': 1e9, 
                'habitats': ['Caves', 'Forests', 'Urban areas'], 
                'regions': ['All continents'],
                'type': 'aerial'
            },
            'Dog': {
                'population': 1e9, 
                'habitats': ['Urban areas', 'Rural areas', 'Wild'], 
                'regions': ['All continents'],
                'type': 'terrestrial'
            },
            'Cat': {
                'population': 6e8, 
                'habitats': ['Urban areas', 'Rural areas', 'Wild'], 
                'regions': ['All continents'],
                'type': 'terrestrial'
            },
            
            # Livestock
            'Cattle': {
                'population': 1e9, 
                'habitats': ['Ranches', 'Grasslands'], 
                'regions': ['All continents'],
                'type': 'terrestrial'
            },
            'Sheep': {
                'population': 1.2e9, 
                'habitats': ['Ranches', 'Mountain grasslands'], 
                'regions': ['All continents'],
                'type': 'terrestrial'
            },
            'Goat': {
                'population': 1.1e9, 
                'habitats': ['Mountains', 'Arid lands'], 
                'regions': ['All continents'],
                'type': 'terrestrial'
            },
            'Pig': {
                'population': 7e8, 
                'habitats': ['Farms', 'Forests'], 
                'regions': ['All continents'],
                'type': 'terrestrial'
            },
            
            # African Savanna
            'Wildebeest': {
                'population': 2e6, 
                'habitats': ['Savanna', 'Grasslands'], 
                'regions': ['East Africa', 'Southern Africa'],
                'type': 'terrestrial'
            },
            'Zebra': {
                'population': 7.5e5, 
                'habitats': ['Savanna', 'Grasslands'], 
                'regions': ['Africa'],
                'type': 'terrestrial'
            },
            'Elephant': {
                'population': 5e5, 
                'habitats': ['Savanna', 'Forests'], 
                'regions': ['Africa', 'Asia'],
                'type': 'terrestrial'
            },
            
            # Marine mammals
            'Dolphin': {
                'population': 6e6, 
                'habitats': ['Temperate seas', 'Tropical seas'], 
                'regions': ['All oceans'],
                'type': 'marine'
            },
            'Whale': {
                'population': 2e6, 
                'habitats': ['Open ocean', 'Polar seas'], 
                'regions': ['All oceans'],
                'type': 'marine'
            },
            
            # Reptiles & Amphibians
            'Snake': {
                'population': 1e8, 
                'habitats': ['Forests', 'Deserts', 'Grasslands'], 
                'regions': ['All continents (except Antarctica)'],
                'type': 'terrestrial'
            },
            'Frog': {
                'population': 5e7, 
                'habitats': ['Wetlands', 'Forests', 'Ponds'], 
                'regions': ['All continents'],
                'type': 'terrestrial'
            },
        }
        
        # Species characteristics data
        self.species_characteristics = {
            'Herring': {
                'communication': 'Chemical signals & schooling behavior',
                'intelligence': 'Basic collective intelligence',
                'survival_traits': ['Mass schooling', 'Fast movement', 'Spawning strategy'],
                'priorities': ['School safety', 'Rich feeding grounds', 'Spawning site security'],
                'ecological_role': 'Key marine food chain species',
                'social_structure': 'Large school society'
            },
            'Mackerel': {
                'communication': 'Lateral line sensing & schooling',
                'intelligence': 'Migration instinct',
                'survival_traits': ['High-speed swimming', 'Schooling behavior', 'Seasonal migration'],
                'priorities': ['Migration route security', 'Predator avoidance', 'Rich fishing grounds'],
                'ecological_role': 'Mid-water predator',
                'social_structure': 'Migratory school'
            },
            'Chicken': {
                'communication': 'Vocalizations & body language',
                'intelligence': 'Social learning ability',
                'survival_traits': ['Vigilance', 'Sociality', 'Adaptability'],
                'priorities': ['Flock safety', 'Stable food supply', 'Nesting sites'],
                'ecological_role': 'Omnivorous ground bird',
                'social_structure': 'Hierarchical society'
            },
            'Rat': {
                'communication': 'Ultrasonic calls & pheromones',
                'intelligence': 'High learning ability',
                'survival_traits': ['High reproduction', 'Adaptability', 'Small & agile'],
                'priorities': ['Safe burrows', 'Food security', 'Breeding success'],
                'ecological_role': 'Small mammal & seed disperser',
                'social_structure': 'Family groups'
            },
            'Dolphin': {
                'communication': 'Echolocation & acoustic signals',
                'intelligence': 'Advanced cognitive abilities',
                'survival_traits': ['Intelligence', 'Cooperation', 'Acoustic abilities'],
                'priorities': ['Ocean environment protection', 'Pod bonds', 'Fish resource security'],
                'ecological_role': 'Marine apex predator',
                'social_structure': 'Pod society'
            },
            'Elephant': {
                'communication': 'Infrasound & tactile',
                'intelligence': 'Advanced intelligence & memory',
                'survival_traits': ['Longevity', 'Memory', 'Family bonds', 'Large size'],
                'priorities': ['Family herd protection', 'Water source security', 'Knowledge transfer'],
                'ecological_role': 'Large herbivore & ecosystem engineer',
                'social_structure': 'Matriarchal society'
            },
            'Wildebeest': {
                'communication': 'Vocalizations & scent',
                'intelligence': 'Collective behavior instinct',
                'survival_traits': ['Great migration', 'Herd behavior', 'Endurance'],
                'priorities': ['Migration success', 'Grazing land security', 'Herd unity'],
                'ecological_role': 'Large herbivore & migratory species',
                'social_structure': 'Large herd society'
            },
            'Crow': {
                'communication': 'Complex vocalizations & gestures',
                'intelligence': 'Advanced problem-solving ability',
                'survival_traits': ['Intelligence', 'Tool use', 'Memory', 'Adaptability'],
                'priorities': ['Wisdom utilization', 'Territory security', 'Cooperation with allies'],
                'ecological_role': 'Intelligent predator & scavenger',
                'social_structure': 'Family groups & flocks'
            },
            'Whale': {
                'communication': 'Songs & long-distance acoustics',
                'intelligence': 'Advanced social intelligence',
                'survival_traits': ['Large size', 'Long-distance migration', 'Deep diving'],
                'priorities': ['Ocean protection', 'Migration route maintenance', 'Family pod protection'],
                'ecological_role': 'Marine megapredator',
                'social_structure': 'Family pods'
            }
        }
        
        # Default characteristics (for species without specific data)
        self.default_characteristics = {
            'communication': 'Species-specific methods',
            'intelligence': 'Instinctual intelligence',
            'survival_traits': ['Adaptability', 'Survival instinct'],
            'priorities': ['Species prosperity', 'Survival security'],
            'ecological_role': 'Ecosystem member',
            'social_structure': 'Herd society'
        }

class SpeciesPersonaGenerator:
    def __init__(self, species_db: GlobalSpeciesDB):
        self.db = species_db
        
    def generate_weighted_choice(self, distribution: Dict[str, float]) -> str:
        choices = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(choices, weights=weights)[0]
    
    def calculate_species_distribution(self, total_personas: int) -> Dict[str, int]:
        """Calculate species distribution based on population data"""
        total_population = sum(data['population'] for data in self.db.species_population.values())
        
        species_distribution = {}
        remaining_personas = total_personas
        
        # Allocate based on population ratios
        species_list = list(self.db.species_population.items())
        species_list.sort(key=lambda x: x[1]['population'], reverse=True)
        
        for species, data in species_list[:-1]:  # All except last species
            ratio = data['population'] / total_population
            count = max(1, min(int(total_personas * ratio), remaining_personas - (len(species_list) - len(species_distribution) - 1)))
            
            if remaining_personas > 0:
                species_distribution[species] = count
                remaining_personas -= count
        
        # Assign remainder to last species
        if species_list and remaining_personas > 0:
            last_species = species_list[-1][0]
            species_distribution[last_species] = remaining_personas
        
        return species_distribution
    
    def generate_species_persona(self, persona_id: int, species: str) -> SpeciesProfile:
        species_data = self.db.species_population.get(species, {})
        species_chars = self.db.species_characteristics.get(species, self.db.default_characteristics)
        
        # Basic attributes
        habitats = species_data.get('habitats', ['Unknown habitat'])
        regions = species_data.get('regions', ['Earth'])
        species_type = species_data.get('type', 'terrestrial')
        
        habitat = random.choice(habitats)
        region = random.choice(regions)
        
        # Age setting (based on species lifespan)
        age_ranges = {
            'Herring': (0, 15), 'Mackerel': (0, 12), 'Cod': (0, 20), 'Salmon': (0, 8), 'Tuna': (0, 30),
            'Chicken': (0, 8), 'Sparrow': (0, 10), 'Crow': (0, 20), 'Pigeon': (0, 15),
            'Rat': (0, 3), 'Bat': (0, 30), 'Dog': (0, 15), 'Cat': (0, 18),
            'Cattle': (0, 20), 'Sheep': (0, 15), 'Goat': (0, 18), 'Pig': (0, 15),
            'Wildebeest': (0, 20), 'Zebra': (0, 25), 'Elephant': (0, 70),
            'Dolphin': (0, 50), 'Whale': (0, 80), 'Snake': (0, 25), 'Frog': (0, 15)
        }
        
        min_age, max_age = age_ranges.get(species, (0, 10))
        age = random.randint(min_age, max_age)
        
        # Gender
        gender = random.choice(['Male', 'Female'])
        
        # Social status
        social_structure = species_chars['social_structure']
        if 'Large' in social_structure or 'school' in social_structure:
            social_status = random.choice(['Group leader', 'Group member', 'Young individual'])
        elif 'Family' in social_structure:
            social_status = random.choice(['Family head', 'Parent', 'Offspring'])
        elif 'Hierarchical' in social_structure:
            social_status = random.choice(['Dominant individual', 'Mid-rank individual', 'Subordinate individual'])
        else:
            social_status = random.choice(['Leader', 'Member', 'Independent individual'])
        
        # Intelligence level
        intelligence_levels = {
            'Dolphin': 'Advanced cognitive abilities', 'Whale': 'Advanced social intelligence', 'Elephant': 'Advanced memory & learning',
            'Crow': 'Problem-solving & tool use', 'Rat': 'Learning & adaptation abilities',
            'Chicken': 'Social learning', 'Dog': 'Cooperation & learning abilities', 'Cat': 'Hunting & independent thinking',
            'Wildebeest': 'Collective intelligence', 'Zebra': 'Vigilance & memory abilities'
        }
        
        intelligence_level = intelligence_levels.get(species, 'Instinctual intelligence')
        
        # Resource access
        resource_access = random.choice(['Abundant', 'Normal', 'Scarce', 'Variable'])
        
        # Survival priority
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
        """Safe search with proper error handling and result trimming"""
        # Limit and sanitize query
        safe_query = str(query)[:100]  # Limit query length
        num_results = min(max(1, num_results), 20)  # Limit results between 1-20
        
        if DDGS_AVAILABLE:
            try:
                ddgs = DDGS()
                search_results = []
                
                results = ddgs.text(
                    keywords=f"{safe_query} species environment wildlife 2025",
                    region='wt-wt',
                    max_results=num_results
                )
                
                for result in results:
                    # Safe result processing with proper trimming
                    safe_result = {
                        'title': self._safe_trim(result.get('title', ''), 150),
                        'snippet': self._safe_trim(result.get('body', ''), 250),
                        'url': self._safe_trim(result.get('href', ''), 200),
                        'date': '2025 Latest'
                    }
                    search_results.append(safe_result)
                
                return search_results if search_results else self._get_demo_results(safe_query, num_results)
                
            except Exception as e:
                st.warning(f"Search error: {str(e)[:100]}")  # Safe error message
                return self._get_demo_results(safe_query, num_results)
        else:
            return self._get_demo_results(safe_query, num_results)
    
    def _safe_trim(self, text: str, max_length: int) -> str:
        """Safely trim text to specified length"""
        if not text:
            return ""
        
        text = str(text)  # Ensure string type
        if len(text) <= max_length:
            return text
        
        # Find last space before max_length to avoid cutting words
        trimmed = text[:max_length]
        last_space = trimmed.rfind(' ')
        
        if last_space > max_length * 0.8:  # If space is reasonably close to end
            return trimmed[:last_space] + "..."
        else:
            return trimmed[:max_length-3] + "..."
    
    def _get_demo_results(self, query: str, num_results: int = 10) -> List[Dict]:
        """Generate safe demo results"""
        demo_results = []
        safe_query = self._safe_trim(query, 50)
        
        for i in range(min(num_results, 5)):  # Limit demo results
            demo_results.append({
                'title': f'Latest Biological Research on {safe_query} {i+1}',
                'snippet': f'Regarding {safe_query}, biologists and environmental scientists report new discoveries. Important insights about ecosystem impacts and inter-species interactions have been obtained.',
                'url': f'https://bio-research{i+1}.com',
                'date': '2025 Latest'
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
        context_section = f"\n【Environmental Information】\n{context_info}\n" if context_info else ""
        
        prompt = f"""【Your Profile】
Species: {persona['species_name']} ({persona['individual_name']})
Age: {persona['age']} years old, Gender: {persona['gender']}
Habitat: {persona['habitat']} ({persona['region']})
Ecological Role: {persona['ecological_role']}
Communication: {persona['communication_method']}
Intelligence Level: {persona['intelligence_level']}
Social Status: {persona['social_status']}
Survival Priority: {persona['survival_priority']}
{context_section}
【Question】{question}

【Response Instructions】
As a {persona['species_name']}, respond prioritizing your species' prosperity and survival.
- Based on your instincts, intelligence, and experience
- Utilizing your species' characteristics and ecological role
- In 100 characters or less, concisely
- From a {persona['species_name']} perspective
"""
        return prompt
    
    def create_search_summary_prompt(self, search_results: List[Dict], question: str) -> str:
        """Search results summary prompt"""
        search_content = "\n".join([
            f"【Article {i+1}】{result['title']}\n{result['snippet']}"
            for i, result in enumerate(search_results[:10])
        ])
        
        prompt = f"""【Question】{question}

【Search Results】
{search_content}

【Summary Instructions】
Summarize the above search results in 300 characters or less:
1. Latest biological and environmental trends regarding {question}
2. Ecosystem and species impacts
3. Expert opinions
4. Environmental changes and conservation activities

Create a summary that is easy for living beings to understand.
"""
        return prompt
    
    def create_analysis_prompt(self, responses: List[str], question: str) -> str:
        all_responses = "\n".join([f"{i+1}: {resp}" for i, resp in enumerate(responses)])
        
        prompt = f"""【Question】{question}

【Responses from Earth's Species】
{all_responses}

【Analysis Instructions】
Analyze in detail and creatively within 2400 characters:

1. **Major Arguments and Conflict Axes Between Species** (500 characters)
   - Differences in perspectives between marine vs terrestrial life
   - Interest conflicts between predators vs prey
   - Differences in influence between high-population vs rare species
   - Thought patterns of high-intelligence vs instinct-based species

2. **Strategies and Priorities by Ecosystem Position** (500 characters)
   - Collectivist thinking of mass-forming species (Herring, Wildebeest, etc.)
   - Problem-solving approaches of high-intelligence species (Dolphins, Elephants, Crows, etc.)
   - Resource securing strategies of apex predators
   - Safety-focused thinking of prey species

3. **Impact of Communication Methods on Thinking** (400 characters)
   - Intuitive judgment of chemical signal-dependent species
   - Cooperation of acoustic communication species
   - Information processing abilities of visual communication species
   - Characteristics of tactile/vibration-based communication

4. **Diversity and Interdependence of Survival Strategies** (400 characters)
   - Quantitative strategy (mass reproduction) vs qualitative strategy (elite approach)
   - Migration strategy vs settlement strategy
   - Cooperation strategy vs competition strategy
   - Adaptation strategy vs environmental modification strategy

5. **Cross-Species Solutions for Global Challenges** (300 characters)
   - Cooperative systems utilizing each species' abilities
   - Marine-terrestrial-aerial network collaboration
   - Optimization combining intelligence and instinct

6. **New Approaches to Biodiversity Conservation** (300 characters)
   - Environmental policies reflecting species voices
   - Utilizing ecosystem self-organization capabilities
   - Value shift from human-centered to bio-centered

Create innovative analysis in 2400 characters utilizing biological diversity and ecosystem complexity.
"""
        return prompt
    
    def count_tokens(self, text: str) -> int:
        """Accurate token counting using tiktoken"""
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                # Fallback to approximate counting if encoding fails
                st.warning(f"Token counting error: {e}. Using approximation.")
                return len(text.split()) * 1.3  # More accurate approximation
        else:
            # Better approximation when tiktoken not available
            return int(len(text.split()) * 1.3)
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Accurate cost calculation for GPT-4o-mini"""
        input_cost = (input_tokens / 1000) * 0.00015  # $0.00015 per 1K input tokens
        output_cost = (output_tokens / 1000) * 0.0006  # $0.0006 per 1K output tokens
        return input_cost + output_cost

class GPT4OMiniProvider:
    def __init__(self, api_key: str):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library is required")
            
        self.client = openai.OpenAI(api_key=api_key)  # Synchronous client
        self.prompt_generator = EnhancedPromptGenerator()
        self.cost_tracker = CostTracker()
        
    def generate_response(self, persona: Dict, question: str, context_info: str = "") -> Dict:
        """Synchronous response generation to avoid asyncio issues in Streamlit"""
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
            
            # Enforce 100 character limit
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
            
            # Safe error message truncation
            if len(error_msg) > 50:
                error_msg = error_msg[:47] + "..."
            
            return {
                'success': False,
                'response': f"API Error: {error_msg}",
                'input_tokens': input_tokens,
                'output_tokens': 0,
                'cost_usd': self.prompt_generator.estimate_cost(input_tokens, 0),
                'error': str(e)
            }
    
    def summarize_search_results(self, search_results: List[Dict], question: str) -> Dict:
        """Synchronous search results summary"""
        # Safe search results trimming
        safe_results = []
        for result in search_results[:10]:  # Limit to 10 results
            safe_result = {
                'title': str(result.get('title', ''))[:100],  # Limit title length
                'snippet': str(result.get('snippet', ''))[:200]  # Limit snippet length
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
                'summary': f"Summary Error: {error_msg}",
                'input_tokens': input_tokens,
                'output_tokens': 0,
                'cost_usd': self.prompt_generator.estimate_cost(input_tokens, 0),
                'error': str(e)
            }
    
    def analyze_responses(self, responses: List[str], question: str) -> Dict:
        """Synchronous response analysis"""
        # Safe response trimming
        safe_responses = [str(resp)[:200] for resp in responses[:100]]  # Limit response length and count
        
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
                'analysis': f"Analysis Error: {error_msg}",
                'input_tokens': input_tokens,
                'output_tokens': 0,
                'cost_usd': self.prompt_generator.estimate_cost(input_tokens, 0),
                'error': str(e)
            }

class ResponseAnalyzer:
    def __init__(self):
        self.stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'to', 'are', 'as', 'we', 'our'}
    
    def extract_keywords(self, responses: List[str]) -> List[Dict]:
        all_text = ' '.join(responses).lower()
        words = re.findall(r'\b[a-z]{3,}\b', all_text)
        filtered_words = [word for word in words if word not in self.stop_words]
        word_freq = Counter(filtered_words)
        return [{'word': word, 'count': count} for word, count in word_freq.most_common(15)]
    
    def analyze_sentiment(self, responses: List[str]) -> Dict:
        positive_words = ['good', 'necessary', 'important', 'cooperation', 'protection', 'development', 'prosperity']
        negative_words = ['dangerous', 'difficult', 'threat', 'anxiety', 'problem', 'decline', 'destruction']
        
        positive_count = negative_count = neutral_count = 0
        
        for response in responses:
            response_lower = response.lower()
            pos_score = sum(response_lower.count(word) for word in positive_words)
            neg_score = sum(response_lower.count(word) for word in negative_words)
            
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
        
        # Species-specific response patterns
        self.response_patterns = {
            'Herring': [
                "Acting in large schools ensures safety and protects rich feeding grounds. Unity is our strength.",
                "We sensitive fish detect ocean changes early and must respond to water temperature and current shifts.",
                "Protecting spawning areas and defending schools from predators directly relates to species prosperity."
            ],
            'Dolphin': [
                "Using ocean wisdom to cooperate with pod members and find sustainable solutions is essential.",
                "Sharing information through acoustic communication allows our pod to make optimal decisions.",
                "Ocean environment protection is our survival foundation. We need strategies that consider coexistence with humans."
            ],
            'Elephant': [
                "Using long experience and memory, gathering family herd wisdom for careful decisions is important.",
                "Water source security and migration route maintenance are our top priorities across generations.",
                "Combining our massive strength and high intelligence for ecosystem-balanced actions."
            ],
            'Rat': [
                "Though small, we're agile and adaptable. We quickly respond to environmental changes for breeding success.",
                "Securing safe burrows and discovering abundant food sources are our basic strategies.",
                "Surviving through numbers, finding new opportunities in any environment."
            ],
            'Crow': [
                "Using wisdom and tool-use abilities to solve problems through creativity and innovation.",
                "Information sharing and learning abilities with companions enable quick adaptation to new environments.",
                "Expanding territory through diverse strategies while utilizing urban environments."
            ],
            'Chicken': [
                "Flock safety and stable food security are top priorities. We want peaceful environments for breeding.",
                "Fulfilling our role in hierarchical society while valuing collective harmony.",
                "Maintaining vigilance against dangers while everyone cooperates for safe living."
            ]
        }
    
    def generate_response(self, persona: Dict, question: str, context_info: str = "") -> Dict:
        """Synchronous response generation for simulation"""
        import time
        time.sleep(0.1)  # Simulate processing time
        
        species = persona.get('species_name', 'Rat')
        survival_priority = persona.get('survival_priority', 'Species prosperity')
        
        # Use species-specific response patterns if available
        if species in self.response_patterns:
            base_responses = self.response_patterns[species]
            response = random.choice(base_responses)
        else:
            # Generate generic responses
            if any(word in question.lower() for word in ['environment', 'protection', 'cooperation']):
                response = f"We {species} aim for {survival_priority} and act with ecosystem harmony in mind."
            elif any(word in question.lower() for word in ['danger', 'threat', 'problem']):
                response = f"As {species}, we face difficulties together with companions for {survival_priority}."
            else:
                response = f"Utilizing {species} characteristics to pursue optimal methods for {survival_priority}."
        
        # Safe response truncation
        if len(response) > 100:
            response = response[:97] + "..."
        
        input_tokens = len(question.split()) + 100
        output_tokens = len(response.split()) * 2  # More realistic token estimation
        
        self.cost_tracker.add_usage(input_tokens, output_tokens)
        
        return {
            'success': True,
            'response': response,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': 0.0
        }
    
    def summarize_search_results(self, search_results: List[Dict], question: str) -> Dict:
        """Synchronous search results summary (simulation version)"""
        summary = f"""【Latest Biological Trends Regarding {question}】

Environmental researchers report that climate change significantly affects each species' habitats, with marine life facing rising water temperatures and terrestrial life confronting habitat changes. As biodiversity protection importance increases, understanding inter-species cooperation and ecosystem interdependence progresses.

Latest research focuses on environmental adaptation strategies by high-intelligence species and collective intelligence utilization through herd behavior. For sustainable ecosystem maintenance, coordinated approaches utilizing each species' characteristics have proven important."""
        
        # Safe summary truncation
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
        """Synchronous response analysis (simulation version)"""
        # Safe responses handling
        safe_responses = [str(resp)[:200] for resp in responses[:50]]  # Limit for simulation
        
        analysis = """【Earth Species Survey - AI Analysis Report】

**Major Arguments and Conflict Axes Between Species**
This survey reveals fundamental environmental perception differences between marine and terrestrial life. Marine species emphasize "fluidity" and "collective thinking," while terrestrial species prioritize "territory" and "individual safety." Particularly, marine life like Herring and Dolphins show adaptability to large-scale environmental changes, while terrestrial high-intelligence species like Elephants and Crows emphasize long-term strategies based on memory.

Population disparity creates influence differences. Trillion-individual Herring think with "quantity logic" for security, while hundreds of thousands of Elephants emphasize "quality logic" for wisdom and experience inheritance. This contrast raises fundamental questions about evaluation criteria for individual numbers versus species value in biodiversity protection.

**Strategies and Priorities by Ecosystem Position**
Mass-forming species (Herring, Wildebeest, etc.) show thought patterns centered on "collective intelligence" and "risk distribution." Their responses demonstrate species-wide optimization strategies premised on individual sacrifice, emphasizing instinctual collective behavior over democratic consensus processes.

Contrarily, high-intelligence species (Dolphins, Elephants, Crows) develop "problem-solving thinking," proposing creative adaptation strategies for environmental changes. Particularly, Dolphins' acoustic networks for information sharing, Elephants' intergenerational knowledge inheritance, and Crows' tool-use techniques suggest possibilities for trans-species learning systems.

Clear resource securing strategy differences exist between apex predators and prey. Predators emphasize "efficiency" and "selective hunting," while prey show specialized thinking in "warning systems" and "escape tactics."

**Impact of Communication Methods on Thinking**
Species dependent on chemical signals (many insects, some mammals) show intuitive, high-responsiveness judgment patterns, emphasizing instinctual reactions over logical analysis. Conversely, acoustic communication species (Dolphins, Whales, many birds) adopt cooperative problem-solving approaches based on complex information transmission capabilities.

Visual communication-centered species excel in information processing accuracy and speed, characterized by early environmental change detection and rapid adaptation strategies. Species primarily using tactile/vibration communication prefer stability-oriented strategies based on more intimate, sustained social cohesion.

**Diversity and Interdependence of Survival Strategies**
Quantitative strategy (mass reproduction) species emphasize environmental variation resistance, while qualitative strategy (elite approach) species emphasize individual value maximization and knowledge accumulation. These strategies appear competitive but actually serve complementary functions in ecosystem stability.

Migration strategy species (migratory birds, migratory fish) focus on "flexibility" and "adaptability," while settlement strategy species emphasize "stability" and "resource cultivation." Both responses highlight the importance of optimizing migration-settlement combinations for environmental change response.

**Cross-Species Solutions for Global Challenges**
The possibility of cooperative systems integrating each species' unique abilities emerges from response analysis. Combining marine life's wide-area information networks, terrestrial life's local environment management abilities, and flying life's three-dimensional monitoring systems could enable global environmental monitoring and early warning system construction.

Fusion of intelligent species' strategic thinking and instinctual species' sensory environmental detection suggests creating "biological intelligence networks" irreplaceable by artificial intelligence.

**New Approaches to Biodiversity Conservation**
The possibility emerges for transitioning from conventional human-centered protection policies to environmental policies directly reflecting "species voices." Incorporating each species' survival strategies and environmental perceptions into policy decision processes could enable more effective protection strategy formulation.

Maximally utilizing ecosystem self-organization capabilities while minimizing human intervention could realize "life-led environmental management," constructing new Earth management models where sustainability and biodiversity coexist."""
        
        # Safe analysis truncation
        if len(analysis) > 3600:
            analysis = analysis[:3597] + "..."
        
        return {
            'success': True,
            'analysis': analysis.strip(),
            'input_tokens': 200,
            'output_tokens': 3000,
            'cost_usd': 0.0
        }

# UI Functions
def setup_sidebar():
    """Setup sidebar with safe session state handling"""
    st.sidebar.title("⚙️ Settings")
    
    st.sidebar.header("🤖 LLM Mode")
    
    use_real_llm = st.sidebar.radio(
        "Select Mode",
        ["Simulation (Free)", "GPT-4o-mini (Paid)"],
        index=0 if not st.session_state.use_real_llm else 1
    )
    
    st.session_state.use_real_llm = (use_real_llm == "GPT-4o-mini (Paid)")
    
    if st.session_state.use_real_llm:
        st.sidebar.header("🔑 API Settings")
        
        api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)
        
        if not api_key:
            env_api_key = os.getenv("OPENAI_API_KEY")
            if env_api_key:
                st.sidebar.success("✅ API key loaded from environment")
                st.session_state.api_key = env_api_key
            else:
                st.sidebar.error("❌ Please enter API key")
                return
        else:
            st.session_state.api_key = api_key
        
        st.sidebar.warning("**Cost Estimate:**\n- 100 responses: ~$0.12\n- AI analysis: ~$0.18")
    
    st.sidebar.header("🐾 Species Persona Settings")
    
    persona_count = st.sidebar.selectbox(
        "Number of Individuals", 
        [10, 25, 50, 100], 
        index=[10, 25, 50, 100].index(st.session_state.persona_count) if st.session_state.persona_count in [10, 25, 50, 100] else 0
    )
    st.session_state.persona_count = persona_count
    
    if st.session_state.use_real_llm:
        estimated_cost = persona_count * 0.00012
        st.sidebar.info(f"💰 Estimated Cost: ~${estimated_cost:.3f}")

def show_home_tab():
    """Home tab with safe session state handling"""
    st.header("🌍 Earth Species Opinion Survey Simulator")
    
    st.markdown("""
    <div style="background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem;">
    🏷️ <strong>Features</strong><br>
    • Based on actual Earth species population data<br>
    • Each species aims for their own prosperity<br>
    • 🦆 DuckDuckGo search: Latest environmental information<br>
    • 📋 Biodiversity report output
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🐾 Hearing Earth's Species Voices
        
        ### ✨ Features
        
        - **🌊 Marine Life**: Herring (8×10¹¹), Mackerel (3×10¹¹), etc. - top population species
        - **🦅 Birds**: Chicken (33 billion), Sparrow, Crow, Pigeon
        - **🐭 Mammals**: Rat (10 billion), Dolphin, Elephant, Dog, Cat
        - **🦌 African Continent**: Wildebeest, Zebra, Elephant - Savanna residents
        - **🧠 Intelligence Levels**: From advanced cognitive abilities to instinct
        - **🌍 Regional Distribution**: Natural distribution based on population data
        
        ### 🎯 Each Species' Perspective
        
        - **Marine Life**: Collective intelligence, aquatic environment focus
        - **High Intelligence Species**: Problem-solving, long-term strategies
        - **Herd Animals**: Group behavior, security focus
        - **Predators**: Resource securing, territory strategies
        - **Prey Species**: Warning systems, escape tactics
        
        ### 📋 Report Contents
        
        - **Inter-species Conflict Axes**: Marine vs Terrestrial, Predator vs Prey
        - **Communication Analysis**: Impact of acoustic, chemical, visual signals
        - **Survival Strategy Diversity**: Quantity vs Quality, Migration vs Settlement
        - **Ecosystem Position Thinking**: Strategies from each organism's standpoint
        """)
    
    with col2:
        st.subheader("📈 Population Rankings")
        
        # Safe session state access with None check
        if st.session_state.species_personas is not None and len(st.session_state.species_personas) > 0:
            personas = st.session_state.species_personas
            
            try:
                df = pd.DataFrame(personas)
                
                st.metric("Generated Individuals", len(personas))
                
                species_counts = df['species_name'].value_counts()
                fig = px.pie(
                    values=species_counts.values,
                    names=species_counts.index,
                    title="Species Distribution"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Chart generation error: {str(e)[:50]}")
                st.metric("Generated Individuals", len(personas))
        else:
            st.info("First generate biological individuals in the 'Personas' tab")
        
        # Display major species populations
        st.subheader("🔢 Earth's Top Populations")
        top_species = [
            ("Herring", "8×10¹¹", "🐟"),
            ("Mackerel", "3×10¹¹", "🐟"),
            ("Chicken", "3.3×10¹⁰", "🐔"),
            ("Rat", "1×10¹⁰", "🐭"),
            ("Dolphin", "6×10⁶", "🐬"),
            ("Elephant", "5×10⁵", "🐘")
        ]
        
        for species, count, emoji in top_species:
            st.write(f"{emoji} {species}: {count} individuals")

def show_persona_tab():
    """Persona tab with safe session state handling"""
    st.header("🐾 Species Persona Generation & Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🌍 Earth Species Database")
        st.markdown("""
        **Population Data Sources:**
        - Marine biology research data
        - Wildlife survey statistics
        - Livestock statistical data
        
        **Generated Attributes:**
        - Species name, individual name, age, gender
        - Habitat, region, ecological role
        - Communication method, intelligence level
        - Social status, survival priorities
        - Resource access status
        """)
        
        if st.button("🎲 Generate Species Personas", type="primary", use_container_width=True):
            generate_species_personas()
    
    with col2:
        st.subheader("⚙️ Generation Settings")
        
        persona_count = st.session_state.persona_count
        st.info(f"Number of Individuals: {persona_count}")
        
        if st.session_state.use_real_llm:
            estimated_cost = persona_count * 0.00012
            st.warning(f"Estimated Survey Cost: ~${estimated_cost:.3f}")
        else:
            st.success("Simulation Version: Free")
    
    # Safe session state access for personas with None check
    if st.session_state.species_personas is not None and len(st.session_state.species_personas) > 0:
        st.subheader("🐾 Generated Species Personas")
        
        try:
            personas = st.session_state.species_personas
            df = pd.DataFrame(personas)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Individuals", len(personas))
            with col2:
                avg_age = df['age'].mean()
                st.metric("Average Age", f"{avg_age:.1f} years")
            with col3:
                marine_ratio = (df['species_type'] == 'marine').mean()
                st.metric("Marine Life Ratio", f"{marine_ratio:.1%}")
            with col4:
                high_intel = df['intelligence_level'].str.contains('Advanced', na=False).mean()
                st.metric("High Intelligence Ratio", f"{high_intel:.1%}")
            
            # Chart display with error handling
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    species_counts = df['species_name'].value_counts()
                    fig1 = px.pie(
                        values=species_counts.values,
                        names=species_counts.index,
                        title="Species Distribution"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                except Exception as e:
                    st.warning(f"Species chart error: {str(e)[:50]}")
            
            with col2:
                try:
                    type_counts = df['species_type'].value_counts()
                    fig2 = px.bar(
                        x=type_counts.values,
                        y=type_counts.index,
                        orientation='h',
                        title="Distribution by Habitat Type"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                except Exception as e:
                    st.warning(f"Type chart error: {str(e)[:50]}")
            
            with st.expander("📋 Detailed Species Persona List"):
                try:
                    display_df = df[['id', 'species_name', 'age', 'gender', 'region', 'ecological_role']].copy()
                    display_df.columns = ['ID', 'Species', 'Age', 'Gender', 'Region', 'Ecological Role']
                    st.dataframe(display_df, use_container_width=True)
                except Exception as e:
                    st.warning(f"Table display error: {str(e)[:50]}")
                    st.write(f"Generated {len(personas)} personas successfully")
                    
        except Exception as e:
            st.error(f"Persona display error: {str(e)[:100]}")
            st.write("Personas generated but display failed. Please try regenerating.")

def show_survey_tab():
    """Survey tab with comprehensive None checks"""
    st.header("❓ Species Opinion Survey Execution")
    
    # Safe personas check with explicit None handling
    personas = st.session_state.species_personas
    if personas is None or len(personas) == 0:
        st.warning("⚠️ First generate species personas in the 'Personas' tab")
        st.info("👈 Go to the 'Personas' tab and click 'Generate Species Personas'")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Question Settings")
        
        preset_questions = {
            "Custom Question": "",
            "Environmental Protection": "What is most important for protecting Earth's environment?",
            "Climate Change Response": "How should we respond to climate change?",
            "Biodiversity Conservation": "What should we do for biodiversity conservation?",
            "Ocean Protection": "What can we do to protect marine environments?",
            "Forest Protection": "How do we protect forests and green spaces?",
            "Inter-species Cooperation": "What's needed for different species to cooperate?",
            "Sustainability": "What's necessary for a sustainable Earth?",
            "Coexistence with Humans": "How can humans and other species coexist?"
        }
        
        selected_preset = st.selectbox(
            "Select from Preset Questions",
            list(preset_questions.keys())
        )
        
        if selected_preset == "Custom Question":
            question = st.text_area(
                "Enter your question",
                value="",
                height=100,
                placeholder="Example: What is an ideal Earth environment?"
            )
        else:
            question = st.text_area(
                "Selected Question (Editable)",
                value=preset_questions[selected_preset],
                height=100
            )
        
        st.subheader("🦆 Web Search (Latest Environmental Information)")
        use_web_search = st.checkbox("Search for latest environmental information related to the question")
        
        search_query = ""
        if use_web_search:
            search_query = st.text_input(
                "Search Keywords",
                value=extract_search_keywords(question) if question else "",
                help="Search latest environmental information with DuckDuckGo (free)"
            )
    
    with col2:
        st.subheader("📊 Survey Settings")
        
        # Safe personas access with explicit None checks
        try:
            personas_count = len(personas) if personas is not None else 0
            st.metric("Target Individuals", personas_count)
            
            if personas_count > 0:
                # Display species distribution with error handling
                try:
                    df = pd.DataFrame(personas)
                    species_counts = df['species_name'].value_counts().head(5)
                    st.write("**Major Participating Species:**")
                    for species, count in species_counts.items():
                        st.write(f"• {species}: {count} individuals")
                except Exception as e:
                    st.warning(f"Species distribution display error: {str(e)[:50]}")
                    st.write(f"• {personas_count} individuals generated")
            
        except Exception as e:
            st.error(f"Persona access error: {str(e)[:50]}")
            st.metric("Target Individuals", 0)
            personas_count = 0
        
        if st.session_state.use_real_llm:
            st.success("🤖 Using GPT-4o-mini")
            
            if question and personas_count > 0:
                estimated_cost = personas_count * 0.00012
                st.info(f"Estimated Cost: ~${estimated_cost:.3f}")
        else:
            st.info("🎭 Using Simulation Version")
            st.success("Cost: Free")
    
    # Survey execution button
    if st.button("🚀 Execute Species Survey", type="primary", use_container_width=True):
        if not question.strip():
            st.error("❌ Please enter a question")
        elif personas_count == 0:
            st.error("❌ Please generate species personas first")
        else:
            execute_species_survey(question, search_query if use_web_search else "")

def show_ai_analysis_tab():
    """AI Analysis tab with comprehensive None checks"""
    st.header("🤖 Biological Intelligence Analysis")
    
    # Safe survey responses check with explicit None handling
    responses = st.session_state.survey_responses
    if responses is None or len(responses) == 0:
        st.info("⚠️ First execute a species survey in the 'Survey' tab")
        st.info("👈 Go to the 'Survey' tab and run a survey first")
        return
    
    # Safe responses access with error handling
    try:
        if not responses or len(responses) == 0:
            st.error("No survey responses available")
            return
            
        # Safe question extraction
        question = "Unknown Question"
        if isinstance(responses, list) and len(responses) > 0:
            first_response = responses[0]
            if isinstance(first_response, dict) and 'question' in first_response:
                question = first_response['question']
        
    except Exception as e:
        st.error(f"Error accessing survey responses: {str(e)[:50]}")
        return
    
    st.subheader(f"📝 Analysis Target: {question}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🧠 Biological Intelligence AI Analysis Features
        
        - **Inter-species Conflict Axes**: Marine vs Terrestrial, Predator vs Prey perspectives
        - **Ecosystem Position Strategies**: Thinking analysis from each species' standpoint
        - **Communication Method Impact**: Impact of acoustic, chemical, visual signals on thinking
        - **Survival Strategy Diversity**: Quantity vs Quality, Migration vs Settlement strategies
        - **Cross-species Solutions**: Utilizing biological intelligence for global challenges
        - **Biodiversity Conservation**: New approach proposals
        
        **Features**: Analysis from biodiversity perspective, not human-centered
        """)
    
    with col2:
        st.subheader("📊 Analysis Settings")
        
        try:
            total_responses = len(responses) if responses else 0
            successful_responses = len([r for r in responses if r and r.get('success', True)]) if responses else 0
            
            st.metric("Analysis Target Responses", successful_responses)
            
            if successful_responses > 0:
                # Species statistics with error handling
                try:
                    valid_responses = [r for r in responses if r and isinstance(r, dict) and 'persona' in r]
                    if valid_responses:
                        personas_data = [r['persona'] for r in valid_responses if r['persona']]
                        if personas_data:
                            df = pd.DataFrame(personas_data)
                            species_counts = df['species_name'].value_counts().head(3)
                            st.write("**Major Responding Species:**")
                            for species, count in species_counts.items():
                                st.write(f"• {species}: {count} individuals")
                except Exception as e:
                    st.warning(f"Species statistics error: {str(e)[:50]}")
                    st.write(f"• {successful_responses} responses available")
            
        except Exception as e:
            st.error(f"Response analysis error: {str(e)[:50]}")
            st.metric("Analysis Target Responses", 0)
            successful_responses = 0
        
        if st.session_state.use_real_llm:
            st.info("🤖 GPT-4o-mini Analysis")
            st.warning("Analysis Cost: ~$0.18")
        else:
            st.info("🎭 Simulation Analysis")
            st.success("Cost: Free")
    
    # Analysis execution button
    if st.button("🧠 Execute Biological Intelligence Analysis", type="primary", use_container_width=True):
        if successful_responses == 0:
            st.error("❌ No valid responses available for analysis")
        else:
            execute_species_ai_analysis(responses, question)
    
    # Analysis results display with safe access
    analysis_result = st.session_state.ai_analysis
    if analysis_result is not None:
        st.subheader("📋 Biological Intelligence Analysis Report")
        
        try:
            if analysis_result and isinstance(analysis_result, dict):
                if analysis_result.get('success', False):
                    analysis_text = analysis_result.get('analysis', 'No analysis content available')
                    st.markdown(analysis_text)
                    
                    if st.session_state.use_real_llm:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            input_tokens = analysis_result.get('input_tokens', 0)
                            st.metric("Input Tokens", f"{input_tokens:,}")
                        with col2:
                            output_tokens = analysis_result.get('output_tokens', 0)
                            st.metric("Output Tokens", f"{output_tokens:,}")
                        with col3:
                            cost_usd = analysis_result.get('cost_usd', 0)
                            st.metric("Analysis Cost", f"${cost_usd:.4f}")
                else:
                    error_msg = analysis_result.get('analysis', 'Unknown error occurred')[:100]
                    st.error(f"❌ Analysis Error: {error_msg}")
            else:
                st.error("❌ Invalid analysis result format")
                
        except Exception as e:
            st.error(f"Analysis display error: {str(e)[:100]}")

def show_analysis_tab():
    st.header("📊 Species Statistical Analysis")
    
    if 'survey_responses' not in st.session_state or st.session_state.survey_responses is None:
        st.info("First execute a survey in the 'Survey' tab")
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
    
    # Basic statistics
    st.subheader("📈 Basic Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.histogram(
            responses_df, x='response_length', 
            title="Response Length Distribution",
            nbins=20
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.box(
            responses_df, x='species_type', y='response_length',
            title="Response Length by Habitat Type"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Species analysis
    st.subheader("🐾 Species Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        species_counts = responses_df['species_name'].value_counts()
        fig3 = px.pie(
            values=species_counts.values,
            names=species_counts.index,
            title="Participating Species Distribution"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        type_counts = responses_df['species_type'].value_counts()
        fig4 = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            title="Participation by Habitat Type"
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    # Keyword analysis
    st.subheader("🏷️ Keyword Analysis")
    
    responses_list = responses_df['response'].tolist()
    keywords = analyzer.extract_keywords(responses_list)
    
    if keywords:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            keyword_df = pd.DataFrame(keywords[:10])
            fig = px.bar(
                keyword_df, x='count', y='word',
                orientation='h',
                title="Top 10 Frequent Keywords"
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Biological Keyword Rankings**")
            for i, kw in enumerate(keywords[:8], 1):
                st.write(f"{i}. {kw['word']} ({kw['count']} times)")
    
    # Sentiment analysis
    st.subheader("😊 Species Sentiment Analysis")
    
    sentiment = analyzer.analyze_sentiment(responses_list)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=[sentiment['positive'], sentiment['negative'], sentiment['neutral']],
            names=['Positive', 'Negative', 'Neutral'],
            title="Overall Sentiment Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Species sentiment (major species only)
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
                title="Major Species Sentiment Analysis"
            )
            st.plotly_chart(fig2, use_container_width=True)

def show_results_tab():
    st.header("📊 Species Survey Results")
    
    if 'survey_responses' not in st.session_state or st.session_state.survey_responses is None:
        st.info("First execute a survey in the 'Survey' tab")
        return
    
    responses = st.session_state.survey_responses
    question = responses[0]['question']
    
    st.subheader(f"📝 Question: {question}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_responses = len(responses)
    successful_responses = len([r for r in responses if r.get('success', True)])
    avg_response_length = np.mean([len(r['response']) for r in responses])
    
    with col1:
        st.metric("Total Responses", total_responses)
    with col2:
        st.metric("Successful Responses", successful_responses)
    with col3:
        st.metric("Average Response Length", f"{avg_response_length:.1f} chars")
    with col4:
        if st.session_state.get('use_real_llm', False):
            total_cost = sum(r.get('cost_usd', 0) for r in responses)
            st.metric("Total Cost", f"${total_cost:.4f}")
        else:
            st.metric("Cost", "Free")
    
    # Display search information
    if 'search_results' in st.session_state and st.session_state.search_results is not None:
        with st.expander("🦆 Latest Environmental Information Used"):
            for result in st.session_state.search_results:
                st.write(f"**{result['title']}**")
                st.write(result['snippet'])
                st.write("---")
    
    # Species response samples
    response_df = pd.DataFrame([{
        'species_name': r['persona']['species_name'],
        'species_type': r['persona']['species_type'],
        'age': r['persona']['age'],
        'gender': r['persona']['gender'],
        'region': r['persona']['region'],
        'response': r['response']
    } for r in responses])
    
    st.subheader("💬 Species Response Samples")
    
    # Display samples by major species
    major_species = response_df['species_name'].value_counts().head(6).index
    
    for species in major_species:
        with st.expander(f"{species} Response Samples"):
            species_responses = response_df[response_df['species_name'] == species]
            
            for idx, (_, row) in enumerate(species_responses.head(3).iterrows(), 1):
                st.write(f"**{idx}. {row['age']} years old {row['gender']} ({row['region']})**")
                st.write(f"💬 {row['response']}")
                st.write("---")
    
    # Data export
    st.subheader("📤 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = response_df.copy()
        csv_data['Question'] = question
        csv_data['Response_Time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        csv_str = csv_data.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📊 Download as CSV",
            data=csv_str,
            file_name=f"species_survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
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
            label="📄 Download as JSON",
            data=json_str,
            file_name=f"species_survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col3:
        # PDF output button
        if REPORTLAB_AVAILABLE:
            if st.button("📋 Generate PDF Report", type="primary", use_container_width=True):
                generate_species_pdf_report(responses, question)
        else:
            st.warning("📋 ReportLab required for PDF output\n`pip install reportlab matplotlib`")

# Helper functions
def extract_search_keywords(question: str) -> str:
    keywords = []
    if 'environment' in question.lower():
        keywords.append('environmental protection biodiversity')
    if 'climate' in question.lower():
        keywords.append('climate change ecosystem')
    if 'ocean' in question.lower():
        keywords.append('ocean protection marine life')
    if 'forest' in question.lower():
        keywords.append('forest protection wildlife')
    if 'cooperation' in question.lower():
        keywords.append('inter-species cooperation ecosystem')
    
    return ' '.join(keywords) if keywords else f"species environment {question[:20]}"

def generate_species_personas():
    persona_count = st.session_state.get('persona_count', 10)
    
    with st.spinner(f'Generating {persona_count} species personas...'):
        progress_bar = st.progress(0)
        
        species_db = GlobalSpeciesDB()
        persona_generator = SpeciesPersonaGenerator(species_db)
        
        # Calculate species distribution
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
        
        # Display generated species distribution
        generated_species = {}
        for persona in personas:
            species = persona['species_name']
            generated_species[species] = generated_species.get(species, 0) + 1
        
        st.success(f"✅ Generated {len(personas)} species personas!")
        
        with st.expander("📊 Generated Species Distribution"):
            for species, count in sorted(generated_species.items(), key=lambda x: x[1], reverse=True):
                st.write(f"• {species}: {count} individuals")

def execute_species_survey(question: str, search_query: str = ""):
    """Execute species survey with proper error handling"""
    if not st.session_state.species_personas:
        st.error("No species personas available")
        return
    
    personas = st.session_state.species_personas
    use_real_llm = st.session_state.use_real_llm
    
    # Execute search results summary
    context_info = ""
    search_summary = None
    
    if search_query:
        search_provider = WebSearchProvider()
        
        search_results = search_provider.search_recent_info(search_query, num_results=10)
        st.session_state.search_results = search_results
        
        if search_results and len(search_results) > 0:
            with st.spinner('🔍 Summarizing environmental information...'):
                try:
                    if use_real_llm and st.session_state.llm_provider:
                        # Real LLM summary
                        search_summary = st.session_state.llm_provider.summarize_search_results(search_results, question)
                    else:
                        # Simulation summary
                        sim_provider = SimulationProvider()
                        search_summary = sim_provider.summarize_search_results(search_results, question)
                    
                    if search_summary and search_summary.get('success', False):
                        context_info = f"【Latest Environmental Information】\n{search_summary['summary']}"
                        st.success(f"✅ Environmental information summary completed ({len(search_results)} sources)")
                    else:
                        st.warning("Environmental information summary failed")
                        
                except Exception as e:
                    st.error(f"Summary error: {str(e)[:100]}")
    
    # Provider initialization
    if use_real_llm:
        api_key = st.session_state.api_key
        if not api_key:
            st.error("API key not set")
            return
        
        try:
            if not st.session_state.llm_provider:
                st.session_state.llm_provider = GPT4OMiniProvider(api_key)
            provider = st.session_state.llm_provider
        except Exception as e:
            st.error(f"Provider initialization error: {str(e)[:100]}")
            return
    else:
        provider = SimulationProvider()
    
    # Execute survey
    with st.spinner(f'{"GPT-4o-mini" if use_real_llm else "Simulation"} species survey in progress...'):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        if search_summary and use_real_llm:
            cost_text = st.empty()
            cost_text.info(f"Environmental info summary cost: ${search_summary.get('cost_usd', 0):.4f}")
        
        responses = []
        
        try:
            for i, persona in enumerate(personas):
                status_text.text(f"Generating response: {i+1}/{len(personas)} ({persona['species_name']})")
                
                # Synchronous call instead of asyncio.run()
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
            st.error(f"Survey execution error: {str(e)[:100]}")
            return
        
        if search_summary:
            st.session_state.search_summary = search_summary
        
        st.session_state.survey_responses = responses
        
        successful_count = len([r for r in responses if r['success']])
        
        total_cost = sum(r.get('cost_usd', 0) for r in responses)
        if search_summary:
            total_cost += search_summary.get('cost_usd', 0)
        
        if successful_count == len(responses):
            cost_msg = f" (Total cost: ${total_cost:.4f})" if use_real_llm else ""
            st.success(f"✅ Species survey completed! Got {successful_count} responses{cost_msg}")
        else:
            st.warning(f"⚠️ Survey completed. Got {successful_count}/{len(responses)} responses")

def execute_species_ai_analysis(responses: List[Dict], question: str):
    """Execute AI analysis with proper error handling"""
    use_real_llm = st.session_state.use_real_llm
    
    successful_responses = [r['response'] for r in responses if r.get('success', True)]
    
    if not successful_responses:
        st.error("No responses available for analysis")
        return
    
    if use_real_llm:
        if not st.session_state.llm_provider:
            st.error("LLM provider not initialized")
            return
        provider = st.session_state.llm_provider
    else:
        provider = SimulationProvider()
    
    with st.spinner('🧠 Biological intelligence AI analysis in progress...'):
        try:
            # Synchronous call instead of asyncio.run()
            analysis_result = provider.analyze_responses(successful_responses, question)
            st.session_state.ai_analysis = analysis_result
            
            if analysis_result.get('success', False):
                st.success("✅ Biological intelligence AI analysis completed!")
            else:
                error_msg = analysis_result.get('analysis', 'Unknown error')[:100]
                st.error(f"❌ Biological intelligence AI analysis error: {error_msg}")
                
        except Exception as e:
            st.error(f"Analysis execution error: {str(e)[:100]}")

def generate_species_pdf_report(responses: List[Dict], question: str):
    """Generate species survey PDF report with proper MIME handling"""
    try:
        with st.spinner('📋 Generating species survey report...'):
            # Safe data preparation
            if not responses:
                st.error("No responses available for report generation")
                return
            
            responses_df = pd.DataFrame([{
                'species_name': str(r['persona'].get('species_name', 'Unknown')),
                'species_type': str(r['persona'].get('species_type', 'Unknown')),
                'age': int(r['persona'].get('age', 0)),
                'gender': str(r['persona'].get('gender', 'Unknown')),
                'region': str(r['persona'].get('region', 'Unknown')),
                'intelligence_level': str(r['persona'].get('intelligence_level', 'Unknown')),
                'response': str(r.get('response', ''))[:200],  # Safe truncation
                'response_length': len(str(r.get('response', '')))
            } for r in responses if r.get('persona')])
            
            if responses_df.empty:
                st.error("No valid response data available")
                return
            
            # Statistical analysis with error handling
            try:
                analyzer = ResponseAnalyzer()
                responses_list = responses_df['response'].tolist()
                keywords = analyzer.extract_keywords(responses_list)
                sentiment = analyzer.analyze_sentiment(responses_list)
            except Exception as e:
                st.warning(f"Analysis error: {str(e)[:50]}, using basic statistics")
                keywords = [{'word': 'environment', 'count': 1}]
                sentiment = {'positive': 33.3, 'negative': 33.3, 'neutral': 33.3}
            
            # Species distribution
            species_counts = responses_df['species_name'].value_counts().to_dict()
            
            # Sample responses with safe handling
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
                            'response': row['response'][:100]  # Safe truncation
                        })
                    if len(sample_responses) >= 15:  # Limit total samples
                        break
            except Exception as e:
                st.warning(f"Sample generation error: {str(e)[:50]}")
            
            # Generate report content
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                safe_question = str(question)[:200]  # Safe question truncation
                
                # Create comprehensive report content
                report_content = f"""Earth Species Opinion Survey Report

Question: {safe_question}
Survey Date: {timestamp}
Total Responses: {len(responses)}

=== SURVEY OVERVIEW ===

Major Participating Species:
{chr(10).join([f"- {species}: {count} individuals" for species, count in list(species_counts.items())[:10]])}

=== KEYWORD ANALYSIS ===

Top Keywords:
{chr(10).join([f"{i+1}. {kw['word']} ({kw['count']} times)" for i, kw in enumerate(keywords[:15])])}

=== SENTIMENT ANALYSIS ===

Overall Sentiment Distribution:
- Positive: {sentiment['positive']:.1f}%
- Negative: {sentiment['negative']:.1f}%
- Neutral: {sentiment['neutral']:.1f}%

=== RESPONSE SAMPLES ===

{chr(10).join([f"• {resp['species']} ({resp['age']} years old {resp['gender']}, {resp['region']}): {resp['response']}" for resp in sample_responses[:12]])}

=== SPECIES STATISTICS ===

Species Type Distribution:
{chr(10).join([f"- {species_type}: {count} individuals" for species_type, count in responses_df['species_type'].value_counts().items()])}

Age Distribution:
- Average Age: {responses_df['age'].mean():.1f} years
- Age Range: {responses_df['age'].min()}-{responses_df['age'].max()} years

Response Length Statistics:
- Average Response Length: {responses_df['response_length'].mean():.1f} characters
- Total Text Generated: {responses_df['response_length'].sum()} characters

=== SURVEY METADATA ===

Survey Configuration:
- Model: {"GPT-4o-mini" if st.session_state.use_real_llm else "Simulation"}
- Total Cost: {"${:.4f}".format(sum(r.get('cost_usd', 0) for r in responses)) if st.session_state.use_real_llm else "Free"}
- Generation Time: {timestamp}
- Context Used: {"Yes" if any(r.get('context_used', False) for r in responses) else "No"}

Report generated by Earth Species Opinion Survey Simulator
"""
                
                # Proper file download with correct MIME type
                st.success("✅ Species survey report generation completed!")
                
                # Offer multiple download formats
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📄 Download Report (TXT)",
                        data=report_content.encode('utf-8'),
                        file_name=f"species_survey_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    # CSV format for data analysis
                    csv_data = responses_df.copy()
                    csv_data['question'] = safe_question
                    csv_data['survey_date'] = timestamp
                    
                    csv_str = csv_data.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📊 Download Data (CSV)",
                        data=csv_str.encode('utf-8-sig'),
                        file_name=f"species_survey_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # PDF generation if ReportLab is available
                if REPORTLAB_AVAILABLE:
                    try:
                        st.info("📋 Advanced PDF generation available with ReportLab")
                        # Could implement actual PDF generation here
                    except Exception as e:
                        st.warning(f"PDF generation error: {str(e)[:50]}")
                else:
                    st.info("💡 Install ReportLab for enhanced PDF output: `pip install reportlab`")
                
            except Exception as e:
                st.error(f"Report content generation error: {str(e)[:100]}")
                return
            
    except Exception as e:
        st.error(f"Report generation failed: {str(e)[:100]}")
        st.info("Please check your data and try again. Contact support if the issue persists.")

# Main function
def main():
    st.title("🌍 Earth Species Opinion Survey Simulator")
    st.caption("🐾 Voices of biodiversity based on actual population data | Each species aims for their own prosperity")
    
    setup_sidebar()
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🌍 Home", "🐾 Personas", "❓ Survey", "🧠 AI Analysis", "📊 Statistics", "📈 Results"
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
    
    # Footer information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌍 Data Sources")
    st.sidebar.markdown("""
    **Population Data:**
    - Marine biology research statistics
    - Wildlife conservation surveys
    - Agricultural statistical data
    
    **Features:**
    - Herring: 8×10¹¹ individuals (marine highest)
    - Chicken: 3.3×10¹⁰ birds (terrestrial highest)
    - Rat: 1×10¹⁰ individuals (wild mammal highest)
    - High intelligence: Dolphins, Elephants, Crows, etc.
    """)
    
    # Safe session state access for sidebar info
    if st.session_state.species_personas is not None and len(st.session_state.species_personas) > 0:
        st.sidebar.markdown("### 📊 Current Settings")
        personas = st.session_state.species_personas
        st.sidebar.metric("Generated Individuals", len(personas))
        
        try:
            df = pd.DataFrame(personas)
            marine_count = len(df[df['species_type'] == 'marine'])
            terrestrial_count = len(df[df['species_type'] == 'terrestrial'])
            aerial_count = len(df[df['species_type'] == 'aerial'])
            
            st.sidebar.write(f"🌊 Marine Life: {marine_count} individuals")
            st.sidebar.write(f"🦌 Terrestrial Life: {terrestrial_count} individuals")
            st.sidebar.write(f"🦅 Flying Life: {aerial_count} individuals")
        except Exception as e:
            st.sidebar.warning(f"Display error: {str(e)[:30]}")

if __name__ == "__main__":
    main()