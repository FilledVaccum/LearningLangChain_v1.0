# LangChain Learning

My personal workspace for learning LangChain and LangGraph. Just experimenting with different models, workflows, and agent patterns.

## What's Inside

### ChatModels/
Different chat model integrations I've been testing:
- `1_ChatModel_OpenAI.py` - OpenAI chat models
- `ChatModel_AWS.py` - AWS Bedrock integration
- `ChatModel_Google.py` - Google's chat models
- `ChatModel_HuggingFace.py` - HuggingFace models
- `5_ChatModel_HF_Local.py` - Running HF models locally

### EmbeddingModels/
Playing with embeddings for semantic search and RAG:
- `1_OpenAI_EmbeddingModels.py` - Basic OpenAI embeddings
- `2_OpenAI_Documents_Embeddings.py` - Embedding documents
- `3_HF_Embeddings.py` - HuggingFace embeddings

### LLMs/
Basic LLM demos and experiments

### CampusX/
Following CampusX tutorials on LangGraph:
- `4. LangGraph Core Concepts.ipynb` - Understanding the basics
- `5. Sequential Workflows in LangGraph` - Building sequential workflows
- `5.3 PromptChaining Workflow - Sequential.ipynb` - Prompt chaining patterns
- `agent_workflow.png` - Visual workflow diagrams

### LangChain_v1.0/
Course materials from LangChain foundations course

### Notebooks
- `Real-World AGent.ipynb` - Experimenting with real-world agent patterns
- `Untitled.ipynb` - Random experiments and scratch work

## Setup

1. Copy `.env` file and add your API keys:
```bash
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
# Add other keys as needed
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start experimenting with the scripts or notebooks

## Notes

This is just a learning repo - code might be messy, incomplete, or experimental. That's the point.
