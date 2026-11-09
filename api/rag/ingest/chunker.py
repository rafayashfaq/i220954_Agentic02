"""
RAG Chunking and Metadata Enrichment.
Produces discrete evidence chunks with full provenance metadata:
persona, type, project, skills, date, client_industry, and outcome.
"""
import re
from typing import Any

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    """Split text into overlapping character windows cleanly along sentence/newline boundaries."""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    chunks = []
    current_chunk = ""

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(current_chunk) + len(p) <= chunk_size:
            current_chunk += ("\n\n" + p if current_chunk else p)
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If paragraph itself is larger than chunk_size, split by sentences
            if len(p) > chunk_size:
                sentences = re.split(r"(?<=[.!?])\s+", p)
                sub_chunk = ""
                for s in sentences:
                    if len(sub_chunk) + len(s) <= chunk_size:
                        sub_chunk += (" " + s if sub_chunk else s)
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = s
                if sub_chunk:
                    current_chunk = sub_chunk
            else:
                current_chunk = p

    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def create_evidence_chunk(
    chunk_id: str,
    text: str,
    persona_id: str,
    evidence_type: str,
    project_id: str,
    skills: list[str],
    date: str = "2025-01-01",
    client_industry: str = "Technology",
    outcome: str = "verified",
    source_path: str = ""
) -> dict[str, Any]:
    """Build a strongly typed chunk dictionary with mandatory metadata."""
    return {
        "chunk_id": chunk_id,
        "text": text,
        "persona_id": persona_id,
        "type": evidence_type,  # case_study, repo, cv, past_proposal, review
        "project": project_id,
        "skills": skills,
        "date": date,
        "client_industry": client_industry,
        "outcome": outcome,  # won, replied, ignored, verified
        "source": source_path
    }

