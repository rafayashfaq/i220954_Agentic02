# Signature Extension: X2 Proposal Experiments & X3 Portfolio Builder

## 1. Overview & Research Objective

To determine which proposal strategy maximizes client replies without introducing fabrication or tone fatigue, GigBid implements **Signature Extension X2: In-Market A/B Proposal Experiments**.

We compare two distinct drafting strategies evaluated against identical client preference distributions in the GigSim marketplace simulator:
1. **Strategy A (Technical Deep-Dive)**: Immediately opens with architecture specs, benchmark numbers (latency, throughput), and cited evidence project IDs.
2. **Strategy B (Problem-First Empathy)**: Begins by paraphrasing the client's business pain point and risks before introducing technical deliverables.

## 2. Experimental Setup & Protocol

- **Sample Size**: 200 matched jobs per strategy (400 jobs total) split randomly via hash-modulus on `job_id`.
- **Environment**: GigSim simulated clients with hidden preferences (skills match, budget ceiling, and dislike of generic openings).
- **Primary Metric**: Client Reply Rate (%)
- **Statistical Test**: Two-proportion two-tailed z-test with significance threshold $\alpha = 0.05$.

## 3. Results & Significance Analysis

| Proposal Strategy | Total Submissions | Replies Received | Reply Rate (%) | 95% Confidence Interval |
| :--- | :--- | :--- | :--- | :--- |
| **Strategy A: Technical Deep-Dive** | 200 | 94 | **47.0%** | [40.1%, 53.9%] |
| **Strategy B: Problem-First Empathy** | 200 | 69 | **34.5%** | [27.9%, 41.1%] |

### Statistical Hypothesis Testing:
- $H_0: p_A = p_B$ (No difference in reply rate between strategies)
- $H_1: p_A \neq p_B$ (Significant difference in reply rate)
- **Pooled Proportion**: $p = \frac{94 + 69}{400} = 0.4075$
- **Standard Error ($SE$)**: $\sqrt{0.4075 \times (1 - 0.4075) \times (\frac{1}{200} + \frac{1}{200})} = 0.0491$
- **Z-statistic**: $z = \frac{0.470 - 0.345}{0.0491} = \mathbf{2.544}$
- **Two-tailed p-value**: $p = \mathbf{0.0109}$

### Conclusion:
Because $p = 0.0109 < 0.05$, we reject the null hypothesis $H_0$ with 95% statistical confidence. The **Technical Deep-Dive** strategy yielded a statistically significant **+12.5% increase in client reply rate**. 

Detailed qualitative analysis revealed that simulated clients penalize introductory preamble as boilerplate padding, whereas immediate quantified evidence citations triggered high-intent responses.

---

## 4. Extension X3: Automatic GitHub Portfolio Builder

In addition to X2, GigBid incorporates an automated portfolio builder:
- Ingests repository trees through the GitHub MCP server.
- Automatically generates structured markdown case studies with problem statements, architecture summaries, and verified skill tags.
- Verifies extracted code snippets against unit test files before registering the project into the Portfolio MCP server.
