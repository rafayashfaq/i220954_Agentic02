"""
Portfolio MCP Prompt Templates.
Provides structured prompt templates for freelancers.
"""

def screening_question_prompt(question: str, job_title: str) -> str:
    """Prompt template to answer a marketplace screening question grounded in portfolio evidence."""
    return f"""You are drafting an answer to a client screening question.
Ground every single claim in verified portfolio evidence items.

Job Title: {job_title}
Screening Question: {question}

Instructions:
1. Identify the core technical skill required by the question.
2. Cite the exact case study ID (e.g. [evidence_id: case-ai-001]) that proves direct experience.
3. Keep the response concise, authoritative, and metric-focused (under 120 words).
4. Never invent years of experience or tools not in the portfolio.
"""

