import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class ResearchPlanner:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def plan(self, topic: str):
        if not self.api_key:
            return {
                "topic": topic,
                "questions": [
                    f"Who are the key competitors in {topic}?",
                    f"What are the main features and pricing models?",
                    f"What are the strategic opportunities and market gaps?"
                ]
            }
        llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=self.api_key, temperature=0.3)
        prompt = ChatPromptTemplate.from_template(
            "You are an expert market research planner. Decompose the following research topic into 5-8 structured sub-questions:\nTopic: {topic}\nQuestions:"
        )
        chain = prompt | llm
        response = chain.invoke({"topic": topic})
        
        questions = [q.strip() for q in response.content.split("\n") if q.strip()]
        return {"topic": topic, "questions": questions, "raw_plan": response.content}

    def decompose_questions(self, scope_note: str):
        return self.plan(scope_note)
