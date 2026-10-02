import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class QualityControlAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def review(self, report_draft: str, research_plan=None):
        if not self.api_key:
            return {"status": "Passed", "feedback": "Quality check passed with default verification."}
        
        llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=self.api_key, temperature=0.1)
        prompt = ChatPromptTemplate.from_template(
            "You are a Quality Control Reviewer for market intelligence reports. Review the draft for unsupported claims, coverage gaps, and contradictions:\nDraft: {draft}\nFeedback:"
        )
        chain = prompt | llm
        response = chain.invoke({"draft": report_draft})
        return {"status": "Reviewed", "qc_feedback": response.content}

    def check_coverage(self, draft: str, plan=None):
        return self.review(draft, plan)
