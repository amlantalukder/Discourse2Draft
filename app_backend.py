from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from src.architecture import Architecture
from pydantic import BaseModel
import uvicorn
import json
import uuid

app = FastAPI()

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

class AgentResponse(BaseModel):
    response: str

@app.get(path="/")
def test():
    return 'success'

@app.get(path="/agent/create", response_model=str)
def create_agent(llm: str, temperature: float, instructions: str):
    global agent
    
    id = uuid.uuid4()
    with open(f'agent_{id}.json', 'w') as fp:
        json.dump({'LLM': llm, 'Temperature': temperature, 'Instructions': instructions}, fp)

    return 'success'

@app.get(path="/agent/query", response_model=AgentResponse)
def get_agent_response(agent_id: str, content_pre: str, current_section: str):
    
    with open(f'agent_{agent_id}.json') as fp:
        settings = json.load(fp)

    agent = Architecture(model_name=settings['LLM'], temperature=settings['Temperature'], instructions=settings['Instructions']).agent

    response = agent.invoke({'content_pre': content_pre, 'current_section': current_section}, {"configurable": {"thread_id": "abc123"}})

    return {'response': response['response']}

if __name__=='__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001)