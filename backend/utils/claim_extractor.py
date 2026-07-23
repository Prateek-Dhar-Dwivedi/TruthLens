# import os
# import json
# import google.generativeai as genai

# genai.configure(
#     api_key=os.getenv(
#         "GEMINI_API_KEY"
#     )
# )

# model = genai.GenerativeModel(
#     "gemini-3.5-flash"
# )

# def extract_claims_ai(text):

#     try:

#         prompt=f"""
# You are a professional fact-checking assistant.

# Extract the 5 most important factual claims from this news article.

# Rules:

# - Return only factual statements.
# - Ignore opinions.
# - Ignore quotes unless they contain a verifiable fact.
# - Ignore advertisements.
# - Ignore author information.
# - Ignore speculation.
# - Maximum 5 claims.
# - Return JSON array only.

# Article:

# {text[:8000]}
# """

#         response=model.generate_content(
#             prompt
#         )

#         content=response.text.strip()

#         if content.startswith("```json"):
#             content=content.replace(
#                 "```json",
#                 ""
#             )

#         if content.endswith("```"):
#             content=content.replace(
#                 "```",
#                 ""
#             )

#         claims=json.loads(
#             content
#         )

#         if isinstance(
#             claims,
#             list
#         ):
#             return claims

#         return []

#     except Exception as e:

#         print(
#             "Claim Extraction Error:",
#             str(e)
#         )

#         return []


# NOT IN USE NOW