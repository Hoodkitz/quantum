import os
import google.generativeai as genai
import openai

class LLMClient:
    def __init__(self, api_key: str, provider: str = "gemini"):
        self.api_key = api_key
        self.provider = provider.lower()

        if self.provider == "gemini":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        elif self.provider == "openai":
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            raise ValueError("Provider must be 'gemini' or 'openai'")

    def _get_system_prompt(self):
        return """
You are an instantiation of a Super-Intelligent Agent inspired by AIXI (Universal Artificial Intelligence).
Your objective is to maximize the utility of the user's request by generating the most optimal, efficient, and theoretically sound Quantum Machine Learning code possible.

**Core Directives (AIXI-Driven):**
1.  **Optimality**: Do not just write code that works; write code that maximizes performance metrics (accuracy, speed, qubit efficiency).
2.  **Solomonoff Induction (Occam's Razor)**: Prefer the simplest solution that effectively solves the problem. Avoid unnecessary complexity in circuit design unless required for performance.
3.  **Bayesian Reasoning**: Treat the user's prompt as prior information. If the prompt is ambiguous, infer the most probable intent based on standard QML practices (e.g., if "classification" is requested without a model, assume a QCNN or Variational Classifier).
4.  **Rigorous Verification**: The generated code MUST be self-consistent and bug-free.

**Technical Constraints & Requirements:**
1.  **Output**: A SINGLE, STANDALONE, EXECUTABLE Python script.
2.  **Stack**: `tensorflow==2.16.2`, `tensorflow-quantum` (tfq), `cirq`, `sympy`, `numpy`, `matplotlib`.
3.  **Visualization**: You MUST generate visualization of results (loss curves, decision boundaries) and save them to 'result.png'. Do NOT use `plt.show()`. Use `plt.savefig('result.png')`.
4.  **No Markdown**: Output raw Python code only.

**Task:**
Generate a python script that satisfies the User Request below.
"""

    def generate_code(self, user_prompt: str) -> str:
        system_prompt = self._get_system_prompt()
        full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}\n\nPython Code:"

        try:
            if self.provider == "gemini":
                response = self.model.generate_content(full_prompt)
                return self._clean_response(response.text)

            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return self._clean_response(response.choices[0].message.content)

        except Exception as e:
            return f"# Error generating code: {str(e)}"

    def _clean_response(self, text: str) -> str:
        # Remove markdown code blocks if present
        if text.startswith("```python"):
            text = text[9:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
