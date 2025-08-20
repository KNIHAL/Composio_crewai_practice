from crewai import Agent, Task, Crew
from composio import Composio
from composio_crewai import CrewAIProvider
from langchain_groq import ChatGroq


# --- Step 1: Setup Composio ---
composio = Composio(api_key="Your api key")

userEmail = "example@gmail.com"

composio = Composio(provider=CrewAIProvider())
# Get All the tools
tools = composio.tools.get(user_id="userEmail", toolkits=["GMAIL"])

# Initiate Gmail OAuth connection
connection_request = composio.connected_accounts.initiate(
    user_id=userEmail,
    auth_config_id="your id ",
)

print(f"👉 Redirect to authenticate Gmail: {connection_request.redirect_url}")

# Wait until user completes OAuth
connected_account = connection_request.wait_for_connection()
print("✅ Gmail connection established successfully!")


# --- Step 3: Setup Groq LLM ---
groq_client = ChatGroq(
    model="Your model type",
    temperature=0
)

# --- Step 4: Create Agent ---
gmail_agent = Agent(
    role="Gmail Assistant",
    goal="Send emails using Composio integration",
    backstory="This agent helps in sending Gmail messages via Composio API.",
    tools=tools,
    llm=groq_client
)

# --- Step 5: Define Task ---
task = Task(
    description=f"Send an email to {userEmail} with the subject 'Hello from Composio 👋🏻' "
                f"and the body 'Congratulations on sending your first email using CrewAI, Groq and Composio!'",
    expected_output="Send the few line of message",
    agent=gmail_agent,
)

# --- Step 6: Run Crew ---
crew = Crew(agents=[gmail_agent], tasks=[task])
result = crew.kickoff()
print("✅ Task result:", result)

# --- Step 7: Create Gmail Trigger ---
trigger = composio.triggers.create(
    user_id=userEmail,
    slug="GMAIL_NEW_GMAIL_MESSAGE",
    trigger_config={"labelIds": "INBOX", "userId": "me", "interval": 60},
)
print(f"✅ Trigger created successfully. Trigger Id: {trigger.trigger_id}")

# Subscribe to the trigger events (simple print handler)
subscription = composio.triggers.subscribe()

@subscription.handle(trigger_id=trigger.trigger_id)
def handle_gmail_event(data):
    print("📩 New Gmail Event:", data)
