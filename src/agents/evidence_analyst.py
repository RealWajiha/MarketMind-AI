import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class EvidenceAnalyst:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def analyze(self, topic: str, research_plan=None):
        if not self.api_key:
            return {
                "findings": [
                    {"claim": f"Market analysis for {topic}", "epistemic_type": "fact", "provenance": "Industry Reports"},
                    {"claim": "Market expected to grow rapidly", "epistemic_type": "inference", "provenance": "Analyst Estimate"}
                ]
            }
        llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=self.api_key, temperature=0.2)
        prompt = ChatPromptTemplate.from_template(
            "You are a market evidence analyst. Analyze the following topic and extract key findings with epistemic typing (Fact vs Inference):\nTopic: {topic}\nPlan: {plan}\nFindings:"
        )
        chain = prompt | llm
        response = chain.invoke({"topic": topic, "plan": str(research_plan)})
        return {"raw_analysis": response.content, "topic": topic}

    def extract_evidence(self, query: str):
        return self.analyze(query)
