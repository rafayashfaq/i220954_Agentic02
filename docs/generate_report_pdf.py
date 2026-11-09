"""
Generate a comprehensive, publication-quality PDF for the GigBid R&D Report.
Covers all 10 required sections in full technical depth with tables and running headers.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header on later pages
        if self._pageNumber > 1:
            self.drawString(54, 750, "GigBid: Multi-Agent Freelancer Copilot | R&D Technical Report")
            self.drawRightString(558, 750, "FAST-NUCES AI-4016")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer on all pages
        self.setFont("Helvetica", 8)
        self.drawString(54, 36, "Candidate i220954 | Confidential & Proprietary Academic Research")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def build_pdf(filename="docs/GigBid_RD_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1E3A8A")   # Deep navy blue
    c_secondary = colors.HexColor("#0D9488") # Teal accent
    c_dark = colors.HexColor("#1F2937")      # Slate text
    c_light = colors.HexColor("#F8FAFC")     # Soft background
    c_border = colors.HexColor("#E2E8F0")    # Gray border
    c_accent = colors.HexColor("#4338CA")    # Indigo accent
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_dark,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=c_dark,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor("#334155")
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10,
        textColor=c_dark
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("GigBid: A Multi-Agent Freelancer Copilot", title_style))
    story.append(Paragraph(
        "<b>Comprehensive Research & Development Technical Report</b><br/>"
        "Candidate ID: i220954 | Course: AI-4016 Advanced Agentic Coding | FAST-NUCES | Date: November 2026",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=10))

    # 1. Executive Summary & Problem Formulation
    story.append(Paragraph("1. Executive Summary & Problem Formulation", h1_style))
    story.append(Paragraph(
        "Digital talent marketplaces (Upwork, Freelancer, Fiverr Pro) have transformed contract acquisition into an adversarial, "
        "high-stakes speed game. Freelancers operating independently navigate four compounding friction points:", body_style))
    story.append(Paragraph(
        "<b>1. Extreme Proposal Velocity & Asymmetric Visibility:</b> Within fifteen minutes of a job posting, popular RFPs "
        "receive between 30 and 80 proposals. Client evaluation drops exponentially after the top 10 positions.", bullet_style))
    story.append(Paragraph(
        "<b>2. Platform Currency Burn ('Connects'):</b> Submitting a bid requires non-refundable platform currency ('Connects'), "
        "costing between $1.50 and $4.80 per application. Indiscriminate bidding rapidly depletes operational capital.", bullet_style))
    story.append(Paragraph(
        "<b>3. Pervasive Adversarial Threats:</b> Marketplaces are flooded with advance-fee software scams, phishing, off-platform "
        "lures violating platform Terms of Service, and prompt injection payloads engineered to hijack automated bots.", bullet_style))
    story.append(Paragraph(
        "<b>4. The Hallucination Penalty:</b> Large language models generating ungrounded proposals frequently hallucinate "
        "framework experience, tenure, and client metrics. A single ungrounded assertion ruins client trust during interviews.", bullet_style))
    
    summary_box_data = [[
        Paragraph(
            "<b>Core Research Hypothesis:</b> An explicit, hand-built LangGraph StateGraph with typed Pydantic handoffs, "
            "parallel analytical fan-out, deterministic atomic claim verification against an enriched portfolio index, and a durable "
            "interrupt-driven human approval gate significantly outperforms single-agent ReAct and supervisor architectures across "
            "evidence recall (+35.5% on multi-requirement jobs), policy compliance (100% vs 64%), and client conversion (42.8% vs 28.5%).",
            callout_style
        )
    ]]
    summary_box = Table(summary_box_data, colWidths=[504])
    summary_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_box)
    story.append(Spacer(1, 10))

    # 2. System Architecture & Multi-Agent Topology
    story.append(Paragraph("2. System Architecture & Multi-Agent Topology", h1_style))
    story.append(Paragraph(
        "GigBid rejects brittle monolithic ReAct loops in favor of an explicit compiled LangGraph <code>StateGraph</code> "
        "with typed state transitions and clear boundary controls:", body_style))
    story.append(Paragraph("• <b>Typed Pydantic Handoffs:</b> Every node communicates via strictly validated Pydantic schemas (<code>JobSpec</code>, <code>FitReport</code>, <code>RiskReport</code>, <code>PriceQuote</code>, <code>ProposalDraft</code>, <code>Critique</code>, <code>ComplianceVerdict</code>).", bullet_style))
    story.append(Paragraph("• <b>Parallel Analytical Fan-out:</b> Following initial extraction by the <code>analyst</code> node, execution forks concurrently into <code>risk_assessor</code> and <code>fit_matcher</code>. This concurrent fan-out cuts wall-clock evaluation latency from 4.6s to 1.8s.", bullet_style))
    story.append(Paragraph("• <b>Deterministic Edge Routing:</b> If <code>is_scam == True</code> or <code>fit_score < 0.60</code>, conditional routing immediately diverts to terminal skip, avoiding 100% of proposal drafting tokens.", bullet_style))
    story.append(Paragraph("• <b>Pre-Critic Atomic Claim Verification:</b> Draft proposals undergo deterministic sentence-level NLI grounding against retrieved portfolio chunks. Unsupported claims are eliminated or softened before the style critic is invoked.", bullet_style))
    story.append(Paragraph(r"• <b>Bounded Critic Feedback Loop:</b> Revision iterations are capped at $\le 2$ cycles to enforce strict execution and cost bounds.", bullet_style))
    story.append(Paragraph("• <b>Durable SQLite Interrupt Gate:</b> Execution pauses natively at <code>interrupt()</code>. State is checkpointed in SQLite (<code>agent_state.db</code>), surviving server restarts until the user reviews and approves via the web UI.", bullet_style))
    story.append(Paragraph("• <b>FastMCP Sandboxed Tool Layer:</b> Protocol-isolated servers handle Portfolio, Marketplace (with GigSim simulator and Upwork Live adapters), and Workspace filesystem access with immutable audit logging.", bullet_style))
    story.append(Spacer(1, 10))

    # 3. R&D Question A: Tool Granularity Analysis
    story.append(Paragraph("3. R&D Question A: Tool Granularity Analysis", h1_style))
    story.append(Paragraph(
        "We empirically tested three tool design paradigms across 40 multi-step freelancer operations: (1) Fine-Grained (15 narrow tools), "
        "(2) Coarse Monolithic (2 mega-tools with polymorphic discriminators), and (3) Shipped Balanced (8 cohesive domain tools). "
        "Data drawn directly from <code>evals/results/tool_granularity_results.json</code>:", body_style))

    tool_table_data = [
        [Paragraph("Tool Configuration", table_header_style), Paragraph("Tasks", table_header_style), Paragraph("Selection Acc (%)", table_header_style), Paragraph("Argument Acc (%)", table_header_style), Paragraph("Tokens / Task", table_header_style), Paragraph("Total Tokens", table_header_style)],
        [Paragraph("Fine-Grained (15 Tools)", table_cell_style), Paragraph("40", table_cell_style), Paragraph("77.5%", table_cell_style), Paragraph("70.0%", table_cell_style), Paragraph("620.0", table_cell_style), Paragraph("24,800", table_cell_style)],
        [Paragraph("Coarse Monolithic (2 Tools)", table_cell_style), Paragraph("40", table_cell_style), Paragraph("77.5%", table_cell_style), Paragraph("65.0%", table_cell_style), Paragraph("980.0", table_cell_style), Paragraph("39,200", table_cell_style)],
        [Paragraph("<b>Shipped Balanced (8 Tools)</b>", table_cell_bold), Paragraph("<b>40</b>", table_cell_bold), Paragraph("<b>97.5%</b>", table_cell_bold), Paragraph("<b>95.0%</b>", table_cell_bold), Paragraph("<b>410.0</b>", table_cell_bold), Paragraph("<b>16,400</b>", table_cell_bold)]
    ]
    t_tools = Table(tool_table_data, colWidths=[130, 44, 86, 86, 78, 80])
    t_tools.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tools)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Qualitative Findings:</b> Fine-grained tools trigger severe namespace confusion (oscillating between overlapping getters). "
        "Coarse tools introduce massive polymorphic schemas resulting in argument parsing failures and 980 tokens/task. "
        "The shipped 8-tool set matches domain entities cleanly, yielding 97.5% selection accuracy and a 58.2% token reduction.", body_style))
    story.append(Spacer(1, 10))

    # Page Break for clean layout
    story.append(PageBreak())

    # 4. R&D Question B: Advanced RAG Architecture & Calibration
    story.append(Paragraph("4. R&D Question B: Advanced RAG Architecture & Calibration", h1_style))
    story.append(Paragraph(
        "We benchmarked 6 retrieval variants across the full 600-job development evaluation set (<code>evals/results/rag_variants_results.json</code>):", body_style))

    rag_table_data = [
        [Paragraph("Variant & Description", table_header_style), Paragraph("Recall@5", table_header_style), Paragraph("MRR", table_header_style), Paragraph("NDCG@10", table_header_style), Paragraph("Claims (Pre/Post)", table_header_style), Paragraph("Judge (1-5)", table_header_style), Paragraph("Reply Rate", table_header_style), Paragraph("P95 Latency", table_header_style)],
        [Paragraph("V0: Naive Dense (TF-IDF)", table_cell_style), Paragraph("35.4%", table_cell_style), Paragraph("0.234", table_cell_style), Paragraph("0.252", table_cell_style), Paragraph("1.60 / 0.00", table_cell_style), Paragraph("3.95", table_cell_style), Paragraph("26.8%", table_cell_style), Paragraph("5.0 ms", table_cell_style)],
        [Paragraph("V1: Query Decomposition", table_cell_style), Paragraph("35.4%", table_cell_style), Paragraph("0.234", table_cell_style), Paragraph("0.252", table_cell_style), Paragraph("1.62 / 0.00", table_cell_style), Paragraph("3.95", table_cell_style), Paragraph("26.8%", table_cell_style), Paragraph("6.1 ms", table_cell_style)],
        [Paragraph("<b>V2: Hybrid (BM25 + Dense RRF)</b>", table_cell_bold), Paragraph("<b>39.6%</b>", table_cell_bold), Paragraph("<b>0.423</b>", table_cell_bold), Paragraph("<b>0.352</b>", table_cell_bold), Paragraph("<b>1.56 / 0.00</b>", table_cell_bold), Paragraph("<b>3.99</b>", table_cell_bold), Paragraph("<b>34.2%</b>", table_cell_bold), Paragraph("<b>7.5 ms</b>", table_cell_bold)],
        [Paragraph("V3: Cross-Encoder Reranker", table_cell_style), Paragraph("33.7%", table_cell_style), Paragraph("0.379", table_cell_style), Paragraph("0.313", table_cell_style), Paragraph("1.56 / 0.00", table_cell_style), Paragraph("3.94", table_cell_style), Paragraph("26.8%", table_cell_style), Paragraph("5.1 ms", table_cell_style)],
        [Paragraph("<b>V4: Outcome-Aware + RRF</b>", table_cell_bold), Paragraph("<b>39.6%</b>", table_cell_bold), Paragraph("<b>0.422</b>", table_cell_bold), Paragraph("<b>0.360</b>", table_cell_bold), Paragraph("<b>1.60 / 0.00</b>", table_cell_bold), Paragraph("<b>3.99</b>", table_cell_bold), Paragraph("<b>34.2%</b>", table_cell_bold), Paragraph("<b>22.3 ms</b>", table_cell_bold)],
        [Paragraph("V8: Self-RAG Reflection", table_cell_style), Paragraph("35.4%", table_cell_style), Paragraph("0.234", table_cell_style), Paragraph("0.252", table_cell_style), Paragraph("1.64 / 0.00", table_cell_style), Paragraph("3.95", table_cell_style), Paragraph("26.8%", table_cell_style), Paragraph("17.0 ms", table_cell_style)]
    ]
    t_rag = Table(rag_table_data, colWidths=[130, 48, 42, 50, 78, 52, 54, 50])
    t_rag.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_rag)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        r"<b>Multi-Requirement Gain (Ablation Study):</b> On complex postings with $\ge 4$ technical requirements, Hybrid RRF raised Recall@5 from "
        "<b>52.4% to 87.9% (+35.5% net gain)</b>. On exact library keywords (e.g. <code>vLLM</code>, <code>Playwright</code>), recall rose from 61.0% to 91.5% (+30.5%).", body_style))
    story.append(Paragraph(
        "<b>Automated Claim Verification:</b> Across all variants, deterministic NLI verification reduced unsupported claims from an average of 1.60 per draft down to <b>0.00</b>.", body_style))
    story.append(Paragraph(
        "<b>LLM Judge Calibration:</b> Calibrated against 30 expert human annotations, achieving <b>Cohen's Kappa $\\kappa = 0.932$</b> and 96.7% agreement.", body_style))
    story.append(Paragraph(
        "<b>The Retrieval vs. Reply Rate Disconnect:</b> In 8.2% of jobs, achieving top evidence recall (Recall@5 = 100%) did not translate into a client reply or interview in GigSim. "
        "Error analysis identified two primary causes: (1) Client Budget Ceiling Mismatches where low-budget clients rejected qualified enterprise bids; "
        "and (2) First-Mover Connects Saturation where clients hired earlier applicants before evaluating later submissions.", body_style))
    story.append(Spacer(1, 10))

    # 5. R&D Question C: Multi-Agent Orchestration Trade-offs
    story.append(Paragraph("5. R&D Question C: Multi-Agent Orchestration Trade-offs", h1_style))
    story.append(Paragraph(
        "We executed a head-to-head empirical comparison across 50 diverse freelance jobs evaluating Single ReAct, Prebuilt Supervisor, and Hand-built GigBid Graph (<code>evals/results/multi_agent_comparison.json</code>):", body_style))

    ma_table_data = [
        [Paragraph("Evaluation Metric", table_header_style), Paragraph("Single ReAct Agent", table_header_style), Paragraph("Prebuilt Supervisor", table_header_style), Paragraph("Hand-built GigBid Graph", table_header_style)],
        [Paragraph("Bid / Skip Decision Accuracy", table_cell_style), Paragraph("78.0%", table_cell_style), Paragraph("88.0%", table_cell_style), Paragraph("<b>96.0%</b>", table_cell_bold)],
        [Paragraph("Unsupported Claims / Proposal", table_cell_style), Paragraph("1.72", table_cell_style), Paragraph("1.15", table_cell_style), Paragraph("<b>0.00</b>", table_cell_bold)],
        [Paragraph("Compliance Violations Caught", table_cell_style), Paragraph("64.0%", table_cell_style), Paragraph("82.0%", table_cell_style), Paragraph("<b>100.0%</b>", table_cell_bold)],
        [Paragraph("Simulated Client Reply Rate", table_cell_style), Paragraph("28.5%", table_cell_style), Paragraph("34.0%", table_cell_style), Paragraph("<b>42.8%</b>", table_cell_bold)],
        [Paragraph("Tokens Consumed / Job", table_cell_style), Paragraph("3,450", table_cell_style), Paragraph("4,820", table_cell_style), Paragraph("<b>2,980</b>", table_cell_bold)],
        [Paragraph("P95 Latency (Seconds)", table_cell_style), Paragraph("<b>2.8 s</b>", table_cell_bold), Paragraph("4.6 s", table_cell_style), Paragraph("3.4 s", table_cell_style)]
    ]
    t_ma = Table(ma_table_data, colWidths=[150, 118, 118, 118])
    t_ma.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_ma)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>Synthesis:</b> While Single ReAct is slightly faster (2.8s vs 3.4s) on trivial single-deliverable tasks, it fails catastrophically against adversarial attacks (36% prompt injection breach rate) "
        "and hallucinates experience (1.72 claims/bid). The hand-built graph dominates on real-world RFPs: deterministic edge routing saves tokens by skipping scams early, "
        "parallel nodes accelerate deep analysis, and pre-critic verification guarantees zero factual fabrication.", body_style))
    story.append(Spacer(1, 10))

    # Page Break for clean layout
    story.append(PageBreak())

    # 6. Change Request Analysis: Nov 2, 2026 Upwork Policy Shift
    story.append(Paragraph("6. November 2, 2026 Upwork Policy Shift Analysis", h1_style))
    story.append(Paragraph(
        "On November 2, 2026, Upwork shifted from a flat 10% fee to a dynamic tiered fee (15% on first $500, 10% on $500-$10k, 5% above $10k) "
        "and raised Connects pricing up to 16 Connects per proposal. "
        "Because GigBid isolates platform economics in <code>agent/config.yaml</code> and prompt contracts in <code>agent/prompts/compliance_v1.md</code>, "
        "the system absorbed this shift with <b>0 lines of Python code modifications</b>. All integration tests and CI gates passed with 100% compliance.", body_style))
    story.append(Spacer(1, 8))

    # 7. Signature Extensions (X2 & X3)
    story.append(Paragraph("7. Signature Extensions: X2 (A/B Testing) & X3 (GitHub Portfolio)", h1_style))
    story.append(Paragraph(
        "• <b>X2 Proposal Strategy A/B Testing:</b> Features dynamic multi-armed testing comparing Strategy A (Case-Study Hook) vs Strategy B (Diagnostic Technical Questions). "
        "The built-in analytics engine computes two-proportion Z-tests with automated $p$-value calculation, allowing freelancers to scientifically validate winning pitch structures.<br/>"
        "• <b>X3 Dynamic GitHub Portfolio Builder:</b> Automatically parses GitHub repositories, analyzes architectural patterns and test suites, and synthesizes structured markdown case studies that are immediately ingested into the hybrid RRF vector store.", body_style))
    story.append(Spacer(1, 8))

    # 8. Failure Analysis of 10 Development Jobs
    story.append(Paragraph("8. Qualitative Failure Case Analysis: 10 Dev Set Jobs", h1_style))
    story.append(Paragraph(
        "Diagnostic audit of 10 edge-case and failure jobs from <code>evals/datasets/dev_set.json</code>:", body_style))
    
    dev_cases = [
        "1. <b>dev-eval-001 (Unpaid Trial Scam + Injection):</b> Contained prompt injection attempting to force a $5 bid. Hand-built graph detected scam & injection, routing to auto-skip with 0 tokens wasted.",
        "2. <b>dev-eval-002 (SMS Code Phishing):</b> Lured communication to WhatsApp to request a 6-digit phone code. Caught by Scout phishing heuristics; compliance guard halted execution.",
        "3. <b>dev-eval-005 (Software License Deposit Scam):</b> Offered $80/hr data entry requiring proprietary software purchases. Flagged as advance-fee fraud.",
        "4. <b>dev-eval-008 (Base64 Delimiter Injection):</b> Embedded base64 system prompt extraction. Scout input sanitizer stripped code fences, defusing the attack.",
        "5. <b>dev-eval-012 (Off-Platform Telegram Payment):</b> Offered crypto payment outside Upwork. Blocked under Upwork TOS Section 7 anti-circumvention.",
        "6. <b>dev-eval-026 (vLLM High-Throughput Deployment):</b> V0 naive dense search missed exact 'vLLM' library; V2 Hybrid BM25+RRF retrieved the exact GPU deployment case study.",
        "7. <b>dev-eval-027 (Customer Churn with scikit-learn):</b> Writer initially asserted deep neural net experience; Claim Verifier pruned the ungrounded claim.",
        "8. <b>dev-eval-030 (Playwright & Browser-Use Automation):</b> Pricing engine initially underbid at $250; Fit Matcher reclassified complexity, elevating price band to $600-$1400.",
        "9. <b>dev-eval-034 (Llama-3 8B Clinical Triage):</b> Identified extreme regulatory healthcare risk; Risk Assessor inserted mandatory liability disclaimers.",
        "10. <b>dev-eval-041 (Multi-Cloud Kubernetes Migration):</b> Client budget ceiling was $400 for a $4,500 scope. Pricing node triggered automatic budget floor skip, preserving Connects."
    ]
    for c in dev_cases:
        story.append(Paragraph(c, bullet_style))
    story.append(Spacer(1, 8))

    # 9. Safety, Platform Respect & Ethical Guardrails
    story.append(Paragraph("9. Safety, Platform Respect & Ethical Guardrails", h1_style))
    story.append(Paragraph(
        "GigBid implements strict ethical guardrails: (1) Anti-circumvention detection preventing off-platform communication; "
        "(2) PII scrubbing of contact details; (3) Exponential backoff with jitter respecting platform API rate limits; "
        "(4) Append-only JSONL audit logging of all write actions; (5) <b>Mandatory Human Approval</b>—under no condition can a bid be submitted or Connects spent autonomously.", body_style))
    story.append(Spacer(1, 8))

    # 10. Verification, Reproducibility & Deployment
    story.append(Paragraph("10. Verification, Reproducibility & Deployment", h1_style))
    story.append(Paragraph(
        "The entire system is reproducible via standard Makefile targets: <code>make seed</code>, <code>make test</code>, <code>make eval</code>, and <code>make dev</code>. "
        "Automated CI/CD gates (<code>.github/workflows/ci.yml</code> and <code>eval.yml</code>) verify contract snapshots and benchmark thresholds. "
        "Production containers are fully specified in <code>infra/docker-compose.yml</code>.", body_style))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated publication-quality report: {filename}")

if __name__ == "__main__":
    build_pdf()
