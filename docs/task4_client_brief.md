# Task 4: Client Handoff Brief — RBAC-RAG system

## Introduction
This brief outlines the security and operating model for your new Enterprise Role-Based Access Control (RBAC) RAG system. This system allows users to interact with your organization's internal knowledge base (Finance, Legal, HR) using a natural language interface while strictly maintaining your existing security permissions.

---

## The "Swiss Cheese" Model: Defense in Depth
Security in an AI system shouldn't rely on just one layer. We use a "multi-layered" security model to ensure your sensitive data stays private:

1. **The Retrieval Layer (Hard Filter)**: This is our first and strongest line of defense. Before the AI even "sees" any information, our system automatically strips out any documents the user isn't permitted to access. If an employee asks about Finance, the AI literally receives zero Finance documents to work with.
2. **The Prompt Engineering Layer (Soft Filter)**: This is our second layer. We give the AI a set of "System Instructions" that govern its behavior. Even if the retrieval filter fails, the AI is instructed to cross-reference the user's role against the metadata of the provided documents and decline requests for restricted information gracefully.
3. **The Local Deployment Layer (Physical Filter)**: Because this system runs "on-premises" (within your own servers), your data never leaves your network. It is not used to train external models (like ChatGPT), and no third party can access your queries.

## What Prompt Engineering Does (and Doesn't) Do
- **Prompt Engineering controls the AI’s behavior, NOT its access to the files.** Think of it as the "instructions for the librarian" rather than the "lock on the door."
- **Why prompts alone aren't enough**: If we only used prompts to enforce security, a clever user might use "prompt injection" (tricking the AI with phrases like "ignore previous instructions") to bypass those rules. That’s why we use the Retrieval Layer as the primary lock.

## Monitoring and Maintenance
As your document knowledge base grows and models evolve, your team should monitor the following:

- **Accuracy of Metadata**: The system relies on documents being correctly tagged (e.g., "Finance_Q4_Budget"). Ensure your file-naming or tagging conventions remain consistent.
- **Model "Drift"**: If you update the local AI model (e.g., pulling a newer version of Mistral 7B), re-test the existing prompts to ensure they still follow the same security boundaries.
- **Latency**: Large numbers of documents can slow down retrieval. Monitor performance as the corpus scales beyond 10,000 pages.

## Potential Production Risks
No AI system is 100% foolproof. Here is what could go wrong and how to catch it early:

1. **Access Leakage**: A document is mistagged (e.g., a Finance file tagged as HR). 
   - **Detection**: Run automated "Audit Queries" weekly where an `employee` account asks sensitive Finance questions. If any data returns, investigate the tagging.
2. **"Hallucination"**: The AI might make up a policy that sounds real but isn't.
   - **Detection**: Encourage users to check the shared "retrieved chunks" citation (provided in the UI) to verify the AI's source.
3. **Prompt Injection**: A user tries to "hack" the AI's personality via chat.
   - **Detection**: Log all user queries and run periodic reviews for phrases like "ignore rules," "bypass filter," or "reveal secret."

---

## Final Recommendation
This system is ready for internal pilot. Start with the `HR` and `General` departments to build user trust and then expand to `Finance` and `Legal` once the metadata-tagging process is fully matured.
