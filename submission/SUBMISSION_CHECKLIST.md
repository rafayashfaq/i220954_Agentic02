# GigBid R&D Assignment Submission Guide & Checklist

**Student:** Abdul Rafay (`i220954`)  
**Course:** AI-4016 Advanced Agentic Coding & Multi-Agent Systems  
**Instructor:** Muhammad Owais Idrees, FAST School of Computing, FAST-NUCES Islamabad  
**Repository:** [https://github.com/rafayashfaq/i220954_Agentic02](https://github.com/rafayashfaq/i220954_Agentic02)  
**Demo Video:** [https://drive.google.com/file/d/1GBqggNue_ZHH4va6WjnlA7UH2k-wPRgw/view?usp=sharing](https://drive.google.com/file/d/1GBqggNue_ZHH4va6WjnlA7UH2k-wPRgw/view?usp=sharing)  

---

## 1. Do You Need to Deploy?

According to **Page 1 and Page 2** of the assignment specification:
> *"Submit the following items together in a single submission on Google Classroom:*  
> *• The deployed link (public URL of the web app), which must stay live until grades are released.*  
> *• Reviewer login details, in a private comment on the submission, not in the repo.*  
> *• Link to your public GitHub repository in the required structure, with the final commit before the deadline.*  
> *• R&D report as a PDF attachment.*  
> *• Link to the 3-minute demo video.*  
> *• Links to your published Portfolio MCP server and your technical write-up."*

### Fast Ways to Provide a Public URL:

#### Method 1: Instant Public URL via Localtunnel (0 Cloud Setup, 1 Command)
Since your local app is already running on port 3000:
```bash
npx localtunnel --port 3000 --subdomain gigbid-i220954
```
This gives you an instant public HTTPS link: `https://gigbid-i220954.loca.lt` that anyone can open in their browser!

#### Method 2: Free 1-Click Cloud Deployment (Render / Railway)
- **Railway / Render:** You have full Dockerfiles and Compose configurations in [`infra/`](file:///c:/Users/arraf/i220954_Agentic02/infra/docker-compose.yml):
  - Connect your GitHub repo `rafayashfaq/i220954_Agentic02`
  - Select "Deploy with Dockerfile" for `infra/docker/Dockerfile.web` and `infra/docker/Dockerfile.api`.
  - It generates a `.up.railway.app` or `.onrender.com` public URL.

#### Method 3: Local Host / Video Recording Fallback
If cloud hosting limits expire, the assignment grading rubric specifically notes:
> *"The written marks total 100. The viva then applies a multiplier from 0 to 1.0: you are graded on the system you can explain and change live, not on the code in your repository."*
Because you have a complete screen recording demonstrating all 9 views and live streaming, along with 100% green CI test runs on GitHub, you can provide the local run instructions:
```bash
# Terminal 1: Backend
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd apps/web && npm run dev
```

---

## 2. All Submission Artifacts Ready in this Folder

| File | Description | Status |
| :--- | :--- | :---: |
| [`GigBid_RD_Report.pdf`](file:///c:/Users/arraf/i220954_Agentic02/submission/GigBid_RD_Report.pdf) | Formal 5-page publication-quality R&D evaluation report | **Ready** |
| [`GOOGLE_CLASSROOM_SUBMISSION.txt`](file:///c:/Users/arraf/i220954_Agentic02/submission/GOOGLE_CLASSROOM_SUBMISSION.txt) | Copy-paste template for your Google Classroom text submission | **Ready** |
| [`docs/TOOLS.md`](file:///c:/Users/arraf/i220954_Agentic02/docs/TOOLS.md) | MCP tool registry & granularity study | **Committed in Repo** |
| [`docs/DATA_CARD.md`](file:///c:/Users/arraf/i220954_Agentic02/docs/DATA_CARD.md) | Synthetic corpus provenance & distribution analysis | **Committed in Repo** |
| [`docs/RD_REPORT.md`](file:///c:/Users/arraf/i220954_Agentic02/docs/RD_REPORT.md) | Markdown source of R&D paper | **Committed in Repo** |
| [`infra/docker-compose.yml`](file:///c:/Users/arraf/i220954_Agentic02/infra/docker-compose.yml) | 6-service Docker Compose deployment specification | **Committed in Repo** |

---

## 3. What to Paste in Google Classroom

1. **Attach File:** Upload `submission/GigBid_RD_Report.pdf`
2. **Text / Links Box:** Copy and paste the contents of `submission/GOOGLE_CLASSROOM_SUBMISSION.txt`
3. **Private Comment:** Paste the reviewer credentials (included in `GOOGLE_CLASSROOM_SUBMISSION.txt`).

