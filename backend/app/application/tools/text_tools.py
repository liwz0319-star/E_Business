"""
Text Tools

Provides text generation and processing utilities using LLM.
"""

import json
from typing import Optional, List


class TextTools:
    """
    Text generation and processing utilities.

    Wraps LLM calls for consistent text operations.
    """

    def __init__(self, llm_client=None):
        """
        Initialize text tools.

        Args:
            llm_client: LLM client for text generation (e.g., DeepSeek client)
        """
        self.llm_client = llm_client

    async def generate_text(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate text using LLM.

        Args:
            prompt: Generation prompt
            context: Optional context to include
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text

        Raises:
            RuntimeError: If LLM client not configured or generation fails
        """
        if self.llm_client is None:
            raise RuntimeError("LLM client not configured")

        # Build full prompt with context if provided
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\n{prompt}"

        try:
            # Call LLM client (placeholder - adapt to actual client)
            response = await self._call_llm(
                full_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response
        except Exception as e:
            raise RuntimeError(f"Text generation failed: {str(e)}")

    async def _call_llm(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Internal method to call LLM.

        This is a placeholder - implement based on actual LLM client.

        Args:
            prompt: Prompt to send
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            Generated text
        """
        # TODO: Implement based on actual LLM client (e.g., DeepSeek)
        # For now, return a mock response
        return f"Generated text based on: {prompt[:100]}..."

    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extract top keywords from text.

        Simple keyword extraction based on word frequency.

        Args:
            text: Text to analyze
            top_k: Number of top keywords to return

        Returns:
            List of keywords
        """
        # Simple keyword extraction (can be enhanced)
        words = text.lower().split()
        word_freq = {}

        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_k]]

    def format_copywriting_prompt(
        self,
        channel: str,
        analysis: dict,
        background: str,
    ) -> str:
        """
        Build copywriting generation prompt.

        Args:
            channel: Channel type (product_page, social_post, ad_short)
            analysis: Product analysis data
            background: User-provided background context

        Returns:
            Formatted prompt
        """
        prompts = {
            "product_page": f"""
Generate a product page description for an e-commerce listing.

Product Analysis:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

Background Context:
{background}

Requirements:
- Compelling headline
- Key features highlighting
- Clear value proposition
- Call-to-action
- Professional tone

Format as markdown.
""",
            "social_post": f"""
Generate an engaging social media post.

Product Analysis:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

Background Context:
{background}

Requirements:
- Attention-grabbing hook
- Emoji usage (moderate)
- Hashtags (3-5 relevant)
- Conversational tone
- Platform-agnostic (works for Instagram, TikTok, etc.)

Format as plain text.
""",
            "ad_short": f"""
Generate a short advertisement script (15-30 seconds).

Product Analysis:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

Background Context:
{background}

Requirements:
- Strong opening hook
- Key selling points (2-3)
- Clear call-to-action
- Conversational tone
- Timing: 15-30 seconds when spoken

Format as script with timing notes.
""",
        }

        return prompts.get(channel, prompts["product_page"])

    def format_campaign_plan_prompt(
        self,
        analysis: dict,
        background: str,
    ) -> str:
        """
        Build campaign planning prompt.

        Args:
            analysis: Product analysis data
            background: User-provided background context

        Returns:
            Formatted prompt
        """
        return f"""
Create a comprehensive marketing campaign plan for this product.

Product Analysis:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

Background Context:
{background}

Output a structured markdown plan with:
1. Campaign Objective
2. Target Audience Profile
3. Key Messaging Pillars (3-5)
4. Channel Strategy
5. Content Suggestions
6. Success Metrics

Keep it practical and actionable.
"""
