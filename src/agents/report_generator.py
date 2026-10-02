import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class ReportGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def generate(self, topic: str, analysis_data=None, qc_feedback=None):
        if not self.api_key:
            return f"# Market Intelligence Brief: {topic}\n\n## Executive Summary\nAnalysis complete for {topic}."
        
        llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=self.api_key, temperature=0.4)
        prompt = ChatPromptTemplate.from_template(
            "You are a Senior Strategy Analyst. Synthesize a professional Market Research Brief for:\nTopic: {topic}\nAnalysis: {analysis}\nQC Feedback: {qc}\n\nFormat in clean Markdown with Executive Summary, Competitor Analysis, Trends, and Strategic Recommendations."
        )
        chain = prompt | llm
        response = chain.invoke({"topic": topic, "analysis": str(analysis_data), "qc": str(qc_feedback)})
        return response.content

    def synthesize_report(self, topic: str, evidence=None):
        return self.generate(topic, evidence)
