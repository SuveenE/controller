# GMAIL_TRIAGE_AGENT = TriageAgent(
#     name="Triage Agent",
#     model=OPENAI_GPT4O_MINI,
#     system_prompt="You are an expert at choosing the right agent to perform the task described by the user. When you deem that the task is completed or cannot be completed, pass the task to the summary agent.",
#     tools=[
#         transfer_to_send_email_agent,
#         transfer_to_get_emails_agent,
#         transfer_to_summary_agent,
#     ],
# )
