"""
Copywriting Agent Prompt Templates.

Centralized prompt definitions for the copywriting workflow.
Supports internationalization by providing templates in multiple languages.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CopywritingPrompts:
    """Prompt templates for the copywriting agent workflow."""
    
    # Stage thoughts - status messages shown during workflow
    plan_start: str = "[plan] 正在为 {product_name} 规划营销大纲..."
    plan_complete: str = "[plan] 营销大纲创建完成"
    draft_start: str = "[draft] 正在根据大纲撰写初稿..."
    draft_complete: str = "[draft] 初稿撰写完成"
    critique_start: str = "[critique] 正在审核和优化文案..."
    critique_complete: str = "[critique] 审核完成，已生成改进建议"
    finalize_start: str = "[finalize] 正在生成最终版本..."
    finalize_complete: str = "[finalize] 最终文案生成完成!"
    
    @staticmethod
    def get_plan_prompt(
        product_name: str,
        features: List[str],
        brand_guidelines: Optional[str] = None,
    ) -> str:
        """
        Generate plan stage prompt.
        
        Args:
            product_name: Product name
            features: List of product features
            brand_guidelines: Optional brand voice guidelines
            
        Returns:
            Formatted prompt string
        """
        features_text = "\n".join(f"- {f}" for f in features)
        brand_text = f"\n品牌指南: {brand_guidelines}" if brand_guidelines else ""
        
        return f"""你是一位专业的营销文案策划师。请为以下产品创建一份营销文案大纲。

产品名称: {product_name}

产品特点:
{features_text}
{brand_text}

请创建一份包含以下内容的营销大纲:
1. 目标受众分析
2. 核心卖点提炼 (3-5个)
3. 情感诉求点
4. 推荐的文案结构
5. 关键词和标语建议

请用中文输出。"""

    @staticmethod
    def get_draft_prompt(product_name: str, plan: str) -> str:
        """
        Generate draft stage prompt.
        
        Args:
            product_name: Product name
            plan: Marketing plan from previous stage
            
        Returns:
            Formatted prompt string
        """
        return f"""你是一位专业的营销文案撰写师。请根据以下营销大纲为产品撰写完整的营销文案。

产品名称: {product_name}

营销大纲:
{plan}

要求:
1. 文案应该吸引人、专业且有说服力
2. 包含引人注目的标题
3. 清晰展示产品价值
4. 包含行动号召 (Call to Action)
5. 长度在300-500字左右

请用中文输出完整的营销文案。"""

    @staticmethod
    def get_critique_prompt(draft: str) -> str:
        """
        Generate critique stage prompt.
        
        Args:
            draft: Draft copy from previous stage
            
        Returns:
            Formatted prompt string
        """
        return f"""你是一位资深的文案审核编辑。请对以下营销文案进行专业审核，并提出具体的改进建议。

待审核文案:
{draft}

请从以下方面进行审核:
1. **语言表达**: 是否流畅、专业、有感染力？
2. **营销效果**: 是否能有效吸引目标客户？
3. **价值传递**: 产品价值是否清晰传达？
4. **行动号召**: CTA是否有效？
5. **结构布局**: 文案结构是否合理？

请提供:
- 3-5条具体的改进建议
- 每条建议说明原因和修改方向
- 优先级标注（高/中/低）

请用中文输出。"""

    @staticmethod
    def get_finalize_prompt(draft: str, critique: str) -> str:
        """
        Generate finalize stage prompt.
        
        Args:
            draft: Draft copy
            critique: Critique suggestions
            
        Returns:
            Formatted prompt string
        """
        return f"""你是一位专业的文案润色专家。请根据初稿和审核建议，生成一份完美的最终营销文案。

初稿:
{draft}

审核建议:
{critique}

要求:
1. 综合所有改进建议优化文案
2. 保持品牌调性一致
3. 确保语言精炼有力
4. 最终文案应该可以直接用于发布
5. 长度控制在300-500字

请直接输出最终版营销文案，无需额外说明。"""


# Default prompts instance
COPYWRITING_PROMPTS = CopywritingPrompts()
