================================================================================
           TECHNICAL PRESENTATION: AI-POWERED RECRUITMENT QUALIFICATION
                         SQORUS | IA RH - AXA Project
================================================================================

SLIDE 1: EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
Problem Solved
- Transform vague recruitment requests from managers into structured, exploitable job descriptions
- Eliminate back-and-forth between HR and managers (typical delay: 2-3 weeks)
- Standardize job descriptions to AXA format and taxonomy
- Enable objective CV screening with clear evaluation criteria

Why It Matters for HR
- Reduces time-to-fill by 40-60% through better initial qualification
- Improves candidate quality through clearer job requirements
- Ensures consistency with AXA job taxonomy and standards
- Enables data-driven recruitment decisions

SLIDE 2: FUNCTIONAL OVERVIEW
--------------------------------------------------------------------------------
User Capabilities
Input Modes
- Free text (natural language recruitment need)
- Audio input (voice recording via microphone)
- File upload (existing job descriptions)

Analysis Features
- Job family/subfamily detection (45 families, subfamilies)
- Missing information detection
- Fuzzy term identification
- Clarification question generation
- Evaluation criteria creation
- Interview question generation

Output Deliverables
- Structured AXA job description (5 sections)
- Quality checklist
- Screening recommendations
- Recruiter brief (ready to send email)
- Market benchmark analysis
- Qualification score with confidence level

SLIDE 3: END-TO-END WORKFLOW
--------------------------------------------------------------------------------
Step 1: Input
       User enters recruitment need in natural language

Step 2: Validation + Pre-matching
       Python-based job family scoring (keyword matching)
       If uncertain -> LLM family router agent

Step 3: Sub-family Detection
       Python-based subfamily scoring
       If uncertain -> LLM subfamily router agent

Step 4: Core Extraction (Extractor Agent)
       LLM generates structured job description
       Identifies missing information
       Creates evaluation criteria

Step 5: Quality Validation (Quality Agent)
       Validates output structure and content

Step 6: Scoring & Analysis
       Compute 5-dimension qualification score
       Generate confidence level
       Build recommendations

Step 7: Market Benchmark (Optional)
       Compare with market data
       Assess competitiveness

SLIDE 4: TECHNICAL ARCHITECTURE
--------------------------------------------------------------------------------
Layers (Top-Down):

1. UI LAYER (app.py)
   - Streamlit web interface
   - User input handling
   - Session state management
   - Display components

2. ORCHESTRATION LAYER (orchestration/pipeline.py)
   - Main pipeline coordinator
   - Step-by-step execution flow
   - Error handling
   - Language management

3. AGENTS LAYER (agents/)
   - extractor_agent.py: Core extraction + JD generation
   - family_router_agent.py: Job family detection
   - subfamily_router_agent.py: Subfamily detection
   - quality_agent.py: Output validation
   - market_benchmark_agent.py: Market comparison
   - summary_agent.py: Executive summary
   - validator_agent.py: Input validation

4. DOMAIN LAYER (domain/)
   - scoring.py: Qualification score computation
   - matching.py: Python-based family/subfamily scoring
   - rules.py: Business rules and thresholds
   - schemas.py: Data validation schemas

5. VALIDATION LAYER (validation/)
   - validation.py: Input/output validation
   - Helper functions for data quality

6. SERVICES LAYER (services/)
   - llm_service.py: LLM API integration (Groq)
   - audio_service.py: Audio transcription

7. DATA LAYER (data/)
   - data_layer.py: Taxonomy + reference data
   - CSV files: AXA job taxonomy, references

SLIDE 5: ARCHITECTURE DIAGRAM (TEXT)
--------------------------------------------------------------------------------

    ┌─────────────────────────────────────────────────────────────────┐
    │                        APP.PY (UI Layer)                        │
    │  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌─────────────┐  │
    │  │Input Form│  │Session    │  │Tabs      │  │Results     │  │
    │  │         │  │State      │  │         │  │Display     │  │
    │  └──────────┘  └───────────┘  └──────────┘  └─────────────┘  │
    └─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │              ORCHESTRATION/PIPELINE.PY                           │
    │  ┌────────────────────────────────────────────────────────┐  │
    │  │  1. Validate Input  2. Score Families  3. Router      │  │
    │  │  4. Score SubFamilies  5. Extract  6. Validate       │  │
    │  │  7. Score & Analyze  8. Benchmark                    │  │
    │  └────────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────────┘
                                  │
          ┌───────────────┬─────────┴─────────┬────────────┐
          ▼               ▼                   ▼            ▼
    ┌───────────┐   ┌───────────┐    ┌─────────┐    ┌──────────┐
    │Matching  │   │Domain     │    │Agents   │    │Services  │
    │(Python)  │   │Rules     │    │(LLM)   │    │(API)    │
    └───────────┘   └───────────┘    └─────────┘    └──────────┘

SLIDE 6: DATA FLOW
--------------------------------------------------------------------------------
Input -> Validation -> Extraction -> Scoring -> Output

1. INPUT
   Natural language "Nous cherchons un chef de projet data senior..."
          │
          ▼
2. VALIDATION (validation/validation.py)
   Check minimum length, extract consolidation
   If invalid -> Error message
          │
          ▼
3. PRE-MATCHING (domain/matching.py)
   Score against 45 job families (keyword matching)
   Threshold: locked (<2) / uncertain / reject
          │
          ▼
4. FAMILY ROUTER (agents/family_router_agent)
   LLM confirms family with confidence score
   If <50% -> Ambiguous error
          │
          ▼
5. EXTRACTION (agents/extractor_agent)
   LLM generates structured job description
   Output: 10+ fields including missing info, criteria
          │
          ▼
6. SCORING (domain/scoring.py)
   5 dimensions: completeness, precision, screening, missions, structure
   Confidence level computation
          │
          ▼
7. OUTPUT
   Job description, checklist, brief, report

SLIDE 7: AI INTEGRATION
--------------------------------------------------------------------------------
LLM Provider: Groq (Llama 3.1 8B model)
- Fast inference for real-time interaction
- Cost-effective for high volume

Why Multiple Agents Instead of Single Prompt?

1. SEPARATION OF CONCERNS
   - Each agent has specific expertise
   - Family router: taxonomy knowledge
   - Extractor: JD structuring
   - Quality: validation
   - Market benchmark: competitive analysis

2. CONFIDENCE ROUTING
   - Python pre-matching first (fast, cheap)
   - LLM only when uncertain (expensive)

3. QUALITY GATES
   - Quality agent validates extractor output
   - Re-run if validation fails

4. ERROR RECOVERY
   - Pipeline can retry specific steps
   - Not full re-execution

5. MAINTAINABILITY
   - Each agent has own prompt/chain
   - Easier to update/tune

SLIDE 8: SCORING LOGIC
--------------------------------------------------------------------------------
5 Dimension Qualification Score (0-100 each):

1. COMPLETENESS (20 pts max)
   - Core fields: job title, contract, experience, company, location
   - Penalized for missing critical information

2. PRECISION (20 pts max)
   - Fuzzy terms count
   - Contradictions detected
   - Consistency of information

3. SCREENING USABILITY (20 pts max)
   - Evaluation criteria present
   - Actionable profile items
   - Clear experience level

4. MISSION CLARITY (20 pts max)
   - Number of actionable missions
   - Specificity vs generic language

5. AXA STRUCTURE COMPLIANCE (20 pts max)
   - Match to AXA job description template
   - Required sections present

GLOBAL SCORE: Average of 5 dimensions (x5 = 0-100)

CONFIDENCE LEVEL: 25-95%
- Low: Based on incomplete/ambiguous input
- Medium: Useful but needs HR validation
- High: Coherent and structured for operational use

SLIDE 9: KEY DESIGN CHOICES
--------------------------------------------------------------------------------
Modular Architecture Benefits

1. SCALABILITY
   - Add new agents without rewriting
   - New job families in taxonomy = new CSV
   - Parallel processing possible

2. MAINTAINABILITY
   - Each layer has single responsibility
   - Easy debugging by layer
   - Independent agent updates

3. TESTABILITY
   - Unit test each component
   - Mock agents for testing
   - Pipeline flow testing

4. REUSABILITY
   - Agents can be reused in other flows
   - Domain functions portable

5. RELIABILITY
   - Quality gates prevent bad output
   - Confidence routing saves costs
   - Error recovery without full restart

Pipeline Orchestration Pattern

- Sequential steps with branching
- Error handling at each step
- Language parameter propagation
- State passed between stages

SLIDE 10: LIMITATIONS
--------------------------------------------------------------------------------
API & Rate Limits
- Groq API rate limits (requests/minute)
- Queue system needed for high volume
- Need fallback strategy

LLM Dependency
- Prompt injection risk
- Model updates may change behavior
- Hallucination potential ( mitigated with validation)

No Real HR System Integration
- Manual data entry required
- No ATS sync
- No candidate management
- No offer letter generation

Data Quality
- Taxonomy limited to AXA jobs
- Reference data needs updates
- Market benchmark limited

Input Quality Dependency
- Garbage in = garbage out
- Requires minimum input length
- Ambiguous needs still fail

SLIDE 11: FUTURE IMPROVEMENTS
--------------------------------------------------------------------------------
Near Term (Q2-Q3 2025)
- Integration with internal ATS (Workday)
- Company-specific taxonomy expansion
- Multi-language support (more languages)
- Voice input improvements

Medium Term (Q4 2025)
- Real-time market salary benchmarking
- Competitor job description analysis
- Candidate matching algorithm
- Performance analytics dashboard

Long Term (2026+)
- Predictive hiring success model
- Candidate pipeline builder
- Automated interview scheduling
- Full recruitment workflow automation

Optimization
- Caching for repeated queries
- Batch processing for bulk analysis
- Custom fine-tuned model

================================================================================
                         END OF PRESENTATION
================================================================================