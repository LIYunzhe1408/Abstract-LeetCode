from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import LeetCodeProblem
from .serializers import LeetCodeProblemSerializer
from pipeline.llm_client import LeetCodeAgent
from pipeline.parse_response_to_csv import extract_table, parse_table_to_xlsx
from django.http import FileResponse, HttpResponseNotFound
import os
from django.conf import settings


def download_excel(request):
    file_path = "./data/leetcode_solutions.xlsx"

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, "rb"), as_attachment=True, filename="./data/leetcode_solutions.xlsx")
        return response
    else:
        return HttpResponseNotFound("File not found.")


@api_view(["POST"])
def solve_question_api(request):
    user_input = request.data.get("question")
    agent = LeetCodeAgent(model="gpt-4")

    # if user_input.lower() == "exit":
    #     break
    response = agent.generate_solution(user_input)
    print("\nResponse:\n", response)
    if response:
        # Extract table and convert to Excel with Cambria font and Markdown conversion
        table_data = extract_table(response)
        if table_data:
            parse_table_to_xlsx(table_data)
        else:
            print("❌ No table found in response!")

        # while True:
        #     followup = input("\nAsk a follow-up (or type 'new' for another problem, 'exit' to quit): ")
        #     if followup.lower() == "new":
        #         break
        #     elif followup.lower() == "exit":
        #         exit()
        #     followup_response = agent.handle_followup(followup)
        #     print("\nAssistant:", followup_response)
        #     if followup_response:
        #         # Extract table and convert to Excel with Cambria font and Markdown conversion
        #         table_data = extract_table(followup_response)
        #         if table_data:
        #             parse_table_to_xlsx(table_data)
        #         else:
        #             print("❌ No table found in response!")

    return Response({"question": user_input, "response": response})