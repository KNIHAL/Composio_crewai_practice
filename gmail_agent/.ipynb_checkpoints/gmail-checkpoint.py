from composio import Composio
from composio_langchain import LangchainProvider

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_groq import ChatGroq

composio = Composio(api_key="Your api key", provider=LangchainProvider())

userEmail = "Your email"

connection_request = composio.connected_accounts.initiate(
  user_id=userEmail,
  auth_config_id="Your config id",
)

# Redirect user to the OAuth flow
redirect_url = connection_request.redirect_url
print(f'Redirect URL: {redirect_url}')

# Wait for the connection to be established
connected_account = connection_request.wait_for_connection()
print('Connection established successfully!')



# Create toolkit for given user
tools = composio.tools.get(user_id=userEmail, tools=["GMAIL_SEND_EMAIL"])

# Pull relevant agent model.
prompt = hub.pull("hwchase17/openai-functions-agent")

# Initialize tools.
groq_client = ChatGroq(
    model="llama-3.3-70b-versatile",  # or another Groq-supported model
    temperature=0
)

# Define task
task = (
  f"Send an email to {userEmail} with the subject 'Hello from composio 👋🏻' and "
  "the body 'Congratulations on sending your first email using AI Agents and Composio!'"
)

# Define agent
agent = create_openai_functions_agent(groq_client, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Execute using agent_executor
agent_executor.invoke({"input": task})
print("Email sent successfully!")

# Create a new trigger for the user's connected account
trigger = composio.triggers.create(
  user_id=userEmail,
  slug="GMAIL_NEW_GMAIL_MESSAGE",
  trigger_config={"labelIds": "INBOX", "userId": "me", "interval": 60},
)
print(f"✅ Trigger created successfully. Trigger Id: {trigger.trigger_id}")

# Subscribe to the trigger events
# Note: For production usecases, use webhooks. Read more here -> https://docs.composio.dev/docs/using-triggers
# You can send an email to yourself and see the events being captured in the console.
subscription = composio.triggers.subscribe()

# Define a handler
@subscription.handle(trigger_id=trigger.trigger_id)
def handle_gmail_event(data):
    print(data)