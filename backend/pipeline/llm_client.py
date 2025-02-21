import openai
from openai import OpenAI
from openai import OpenAIError
import os
import time
import re
from typing import List, Dict, Optional

# Load API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


class LeetCodeAgent:
    """LLM-powered agent for answering LeetCode problems and follow-up questions."""

    def __init__(self, model: str = "gpt-4o", max_retries: int = 3):
        self.model = model
        self.max_retries = max_retries
        self.system_prompt = """You are an AI assistant that provides structured explanations for LeetCode problems.

        - Always follow the structured format for problem responses.
        - When users ask follow-up questions, answer concisely and directly.
        - If a new problem number and title are given, generate a new structured response.
        - If unsure, ask the user for clarification.
        """
        self.chat_history = []  # Store conversation context
        self.current_problem = None  # Store the last problem's number & title

    def extract_problem_details(self, user_input: str) -> Optional[Dict[str, str]]:
        """
        Extracts the problem number and title from user input.

        Args:
            user_input (str): The user's input query.

        Returns:
            dict: A dictionary with 'problem_number' and 'problem_title' or None if not found.
        """
        match = re.search(r"\b(?:Leetcode|LC|Problem)?\s*(\d{1,4})\b", user_input, re.IGNORECASE)
        problem_number = match.group(1) if match else None

        title_match = re.search(r"Leetcode \d{1,4}: (.+)", user_input, re.IGNORECASE)
        problem_title = title_match.group(1) if title_match else None

        if problem_number and problem_title:
            return {"problem_number": problem_number, "problem_title": problem_title}

        return None

    def infer_problem_details(self, user_input: str) -> Optional[Dict[str, str]]:
        """
        Uses OpenAI to infer the problem number and title if not explicitly mentioned.

        Args:
            user_input (str): The user's query.

        Returns:
            dict: A dictionary containing inferred problem details or None if uncertain.
        """
        prompt = f"""
        The user wants information about a LeetCode problem but didn't provide full details.
        Given this input: "{user_input}", infer the most likely problem number and title.
        Respond in JSON format as: {{"problem_number": "XXX", "problem_title": "YYY"}}.
        """

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": self.system_prompt},
                          {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )

            result = response.choices[0].message.content.strip()
            return eval(result) if result.startswith("{") else None

        except OpenAIError:
            return None

    def generate_solution(self, user_input: str) -> str:
        """
        Generates a structured response for a LeetCode problem.

        Args:
            user_input (str): The user's input query.

        Returns:
            str: Generated markdown response.
        """
        # Extract problem details from user input
        problem_details = self.extract_problem_details(user_input)

        if not problem_details:
            print("❓ Could not detect problem number and title. Trying AI-based inference...")
            problem_details = self.infer_problem_details(user_input)

        if not problem_details:
            return "I couldn't determine the exact LeetCode problem you're referring to. Can you clarify?"

        self.current_problem = problem_details  # Store current problem for follow-ups

        problem_number = problem_details["problem_number"]
        problem_title = problem_details["problem_title"]

        user_prompt = f"""
        Problem Name: "Leetcode {problem_number}. {problem_title}"

        Instructions:
        - Provide the problem pattern and solution approach.
        - Explain the algorithm used, including time and space complexity.
        - List when to use this pattern and how it scales to similar problems.
        - Format the output exactly as follows:

        ---

        ### **LeetCode {problem_number}: {problem_title}**  

        | No. | Name | Last Viewed | Tag | Problem Pattern/Solution | When to Use/Scale |
        |----|------|------------|-----|--------------------------|--------------------|
        | {problem_number} | {problem_title} | {time.strftime('%Y-%m-%d')} | {{problem_tags}} | **Problem Pattern:** {{Describe the problem pattern and general solution strategy.}} <br> **Solution Approach:** {{Explain the key idea behind the solution, including how it optimizes the problem.}} | 1. {{When to use this pattern, bullet point 1}} <br> 2. {{When to use this pattern, bullet point 2}} <br> 3. {{When to use this pattern, bullet point 3}} |

        ---

        ## **🔹 Algorithm Used**
        - **{{Algorithm Name}} (`{{Time Complexity}}`)**
          1. {{Step 1 explanation}}
          2. {{Step 2 explanation}}
          3. {{Step 3 explanation}}
        - **Time Complexity:** `{{O(complexity)}}`, explanation.  
        - **Space Complexity:** `{{O(complexity)}}`, explanation.  

        ---

        ## **🔹 Python Code**
        ```python
        {{Optimized Python code solution}}
        ```
        """

        return self._send_message(user_prompt, is_new_question=True)

    def handle_followup(self, user_query: str) -> str:
        """
        Handles user follow-up questions while maintaining problem context.

        Args:
            user_query (str): The user's follow-up question.

        Returns:
            str: LLM-generated response.
        """
        if not self.current_problem:
            return "I don't have an active problem context. Please specify the problem number or title."

        user_prompt = f"""
        Follow-up question about LeetCode {self.current_problem['problem_number']}: {self.current_problem['problem_title']}.

        Question: "{user_query}"

        Provide a relevant response based on the previous discussion.
        """

        return self._send_message(user_prompt, is_new_question=False)

    def _send_message(self, user_input: str, is_new_question: bool) -> str:
        """
        Sends a message to the OpenAI API while maintaining conversation history.

        Args:
            user_input (str): The user's question or follow-up.
            is_new_question (bool): Whether this is a new question.

        Returns:
            str: OpenAI response.
        """
        retries = 0
        if is_new_question:
            self.chat_history = []  # Reset chat history for a new question

        # Maintain conversation context
        self.chat_history.append({"role": "user", "content": user_input})

        while retries < self.max_retries:
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": self.system_prompt}] + self.chat_history,
                    temperature=0.7,
                    max_tokens=1500
                )

                answer = response.choices[0].message.content
                self.chat_history.append({"role": "assistant", "content": answer})
                return answer

            except OpenAIError as e:
                print(f"API Error: {e}. Retrying ({retries + 1}/{self.max_retries})...")
                time.sleep(2 ** retries)
                retries += 1

        return "Error: Failed to get a response after retries."


# Example Usage
if __name__ == "__main__":
    agent = LeetCodeAgent(model="gpt-4")

    while True:
        user_input = input("\nAsk a question about a LeetCode problem (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        response = agent.generate_solution(user_input)
        print("\nResponse:\n", response)

        while True:
            followup = input("\nAsk a follow-up (or type 'new' for another problem, 'exit' to quit): ")
            if followup.lower() == "new":
                break
            elif followup.lower() == "exit":
                exit()
            followup_response = agent.handle_followup(followup)
            print("\nAssistant:", followup_response)
