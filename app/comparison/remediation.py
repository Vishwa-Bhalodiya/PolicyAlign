from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import get_llm
from app.core.rate_limiter import rate_limiter

llm = get_llm()

REMEDIATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Rewrite the vendor clause minimally so that it satisfies the client obligation.

            Keep structure same.
            Add only missing elements.
            Do not over-expand.
            Return improved vendor text only.
            """
        ),
        (
            "user",
            """
            CLIENT:
            {client}

            VENDOR:
            {vendor}
            """
        )
    ]
)

chain = REMEDIATION_PROMPT | llm

def suggest_remediation(client_text: str, vendor_text: str):
    rate_limiter.wait()  # Ensure we respect rate limits
    response = chain.invoke({
        "client": client_text,
        "vendor": vendor_text
    })
    return response.content.strip()