import os
import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from sentence_transformers import SentenceTransformer
from database import SessionLocal, DocumentChunk
from dotenv import load_dotenv

try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'), override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_llm():
    provider = os.getenv('LLM_PROVIDER', 'local').lower()
    if provider == 'cloud':
        try:
            return ChatAnthropic(model_name='claude-3-haiku-20240307')
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic LLM: {e}")
            return None
    else:
        if ChatOllama is None:
            logger.warning("langchain_ollama is not installed.")
            return None
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        model_name = os.getenv('OLLAMA_MODEL', 'phi3')
        return ChatOllama(model=model_name, base_url=base_url)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_context(query):
    query_embedding = embedding_model.encode(query)
    
    db = SessionLocal()
    try:
        results = db.query(DocumentChunk).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        ).limit(3).all()
        
        if not results:
            return "No relevant context found.", []
            
        context_parts = []
        sources = set()
        for res in results:
            context_parts.append(res.content)
            if res.source:
                sources.add(res.source)
                
        return "\n\n".join(context_parts), list(sources)
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return "Error retrieving context.", []
    finally:
        db.close()

def detect_skill(query):
    query_lower = query.lower()
    ship30_keywords = ['ship 30', 'essay', 'write an essay', 'ship30', '30 for 30']
    if any(kw in query_lower for kw in ship30_keywords):
        return 'ship30'
    return 'qa'

def ship30_skill(query, context, sources, chat_history):
    system_prompt = """You are a master essay writer. Write an essay using these principles:
- Approximately 1,250 words
- Strong hook that grabs attention in the first line
- Clear narrative progression with beginning, middle, end
- Skimmable formatting: use ## headings, bullet points, **bold** for emphasis
- A specific, useful takeaway the reader can apply immediately
- All claims must be grounded in the provided transcript context
- Cite sources naturally within the text

Context:
{context}"""

    llm = get_llm()
    if not llm:
        return "```markdown\nError: LLM provider not available.\n```"
        
    messages = [SystemMessage(content=system_prompt.format(context=context))]
    messages.extend(chat_history)
    messages.append(HumanMessage(content=query))
    
    try:
        response = llm.invoke(messages)
        content = response.content
        if not content.startswith("```markdown"):
            content = f"```markdown\n{content}\n```"
        return content
    except Exception as e:
        logger.error(f"LLM Error in ship30_skill: {e}")
        return f"```markdown\nError generating essay: {e}\n```"

def qa_skill(query, context, sources, chat_history):
    system_prompt = """You are 'The Lenny Growth Assistant'. Answer using ONLY the provided context. If context doesn't contain the answer, say so. Cite sources.

Context:
{context}"""

    llm = get_llm()
    if not llm:
        return "Error: LLM provider not available."
        
    messages = [SystemMessage(content=system_prompt.format(context=context))]
    messages.extend(chat_history)
    messages.append(HumanMessage(content=query))
    
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"LLM Error in qa_skill: {e}")
        return f"Error generating answer: {e}"

def generate_response(query, chat_history):
    try:
        context, sources = retrieve_context(query)
        skill = detect_skill(query)
        
        if skill == 'ship30':
            reply = ship30_skill(query, context, sources, chat_history)
        else:
            reply = qa_skill(query, context, sources, chat_history)
            
        return reply, sources, skill
    except Exception as e:
        logger.error(f"Error in generate_response: {e}")
        return "I encountered an error processing your request.", [], "error"
