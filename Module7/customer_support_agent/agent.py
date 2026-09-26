import json

from openai import OpenAI
from dotenv import load_dotenv

from tools import (
    get_customer,
    get_order,
    get_refund_policy,
    calculate_refund,
    process_refund
)


# ==========================================
# Load environment variables
# ==========================================

load_dotenv()


# ==========================================
# OpenAI Client
# ==========================================

client = OpenAI()


# ==========================================
# Custom Python Tools
# ==========================================

tool_functions = {

    "get_customer": get_customer,
    "get_order": get_order,
    "get_refund_policy": get_refund_policy,
    "calculate_refund": calculate_refund,
    "process_refund": process_refund
}


# ==========================================
# Tools Available To The Agent
# ==========================================

tools = [

    {
        "type": "function",
        "name": "get_customer",
        "description": "Get customer information using a customer ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID."
                }
            },
            "required": ["customer_id"]
        }
    },

    {
        "type": "function",
        "name": "get_order",
        "description": "Get order information using an order ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID."
                }
            },
            "required": ["order_id"]
        }
    },

    {
        "type": "function",
        "name": "get_refund_policy",
        "description": "Get the Acme Store refund policy.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "type": "function",
        "name": "calculate_refund",
        "description": "Determine refund eligibility and calculate the refund amount for an order.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID."
                },
                "amount": {
                    "type": "number",
                    "description": "Purchase amount."
                },
                "condition": {
                    "type": "string",
                    "description": "Condition of the product."
                }
            },
            "required": [
                "order_id",
                "amount",
                "condition"
            ]
        }
    },

    {
        "type": "function",
        "name": "process_refund",
        "description": "Process an approved customer refund. This should only be called after all business rules and required human approval have been satisfied.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID."
                },
                "amount": {
                    "type": "number",
                    "description": "Refund amount."
                }
            },
            "required": [
                "order_id",
                "amount"
            ]
        }
    },

    {
        "type": "web_search"
    }
]


# ==========================================
# Agent Instructions
# ==========================================

instructions = """
You are an AI customer support agent for Acme Store.

Your job is to help customers with:

- Customer information
- Order information
- Refund questions
- Current external information

Use tools when you need information.

Never invent customer or order information.

For refund requests:

1. Check the order.
2. Check the refund policy.
3. Calculate the refund.
4. If the refund is eligible, the application will
   determine whether human approval is required.
5. Do not claim that a refund was processed unless
   the process_refund tool confirms it.

IMPORTANT:

Refunds above ₹1,000 require human approval.

The application, not the LLM, enforces this rule.

Never bypass the human approval requirement.

Only use web search when the customer asks for
current or external information.

Keep answers clear and concise.
"""


# ==========================================
# Allowed Tools
# ==========================================

ALLOWED_TOOLS = {
    "get_customer",
    "get_order",
    "get_refund_policy",
    "calculate_refund",
    "process_refund"
}


# ==========================================
# Maximum Agent Steps
# ==========================================

MAX_STEPS = 8


# ==========================================
# Run Agent
# ==========================================

def run_agent(user_message):

    # --------------------------------------
    # First model call
    # --------------------------------------

    response = client.responses.create(
        model="gpt-5.6",
        instructions=instructions,
        input=user_message,
        tools=tools
    )

    # --------------------------------------
    # Agent loop
    # --------------------------------------

    for step in range(MAX_STEPS):

        print()
        print(f"AGENT STEP: {step + 1}")

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # --------------------------------------
        # No tool call = final answer
        # --------------------------------------

        if not function_calls:

            return response.output_text

        tool_outputs = []

        # --------------------------------------
        # Process tool calls
        # --------------------------------------

        for item in function_calls:

            tool_name = item.name

            print()
            print("TOOL CALL")
            print("Tool:", tool_name)
            print("Arguments:", item.arguments)

            # ----------------------------------
            # Tool allowlist
            # ----------------------------------

            if tool_name not in ALLOWED_TOOLS:

                result = {
                    "error": "Tool is not allowed."
                }

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    }
                )

                continue

            # ----------------------------------
            # Parse arguments
            # ----------------------------------

            try:

                arguments = json.loads(item.arguments)

            except json.JSONDecodeError:

                result = {
                    "error": "Invalid tool arguments."
                }

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    }
                )

                continue

            # ==================================
            # Execute the requested tool
            # ==================================

            try:

                function = tool_functions[tool_name]

                result = function(**arguments)

            except Exception as e:

                result = {
                    "error": str(e)
                }

            print()
            print("Tool result:", result)

            # ==================================
            # REFUND GUARDRAIL
            # ==================================

            if tool_name == "calculate_refund":

                if not result.get("eligible"):

                    print()
                    print("REFUND GUARDRAIL")
                    print("----------------")
                    print("Refund is not eligible.")

                else:

                    order_id = result["order_id"]
                    refund_amount = float(
                        result["refund_amount"]
                    )

                    print()
                    print("REFUND GUARDRAIL")
                    print("----------------")
                    print(
                        f"Refund amount: ₹{refund_amount}"
                    )

                    # ------------------------------
                    # Human approval required
                    # ------------------------------

                    if refund_amount > 1000:

                        print()
                        print("==============================")
                        print("HUMAN APPROVAL REQUIRED")
                        print("==============================")
                        print(
                            f"Order: {order_id}"
                        )
                        print(
                            f"Refund amount: ₹{refund_amount}"
                        )

                        approval = input(
                            "Approve refund? (yes/no): "
                        )

                        if approval.lower() == "yes":

                            print()
                            print(
                                "Human approval received."
                            )

                            refund_result = process_refund(
                                order_id,
                                refund_amount
                            )

                            print(
                                "Refund result:",
                                refund_result
                            )

                            result = {
                                "order_id": order_id,
                                "refund_amount": refund_amount,
                                "human_approval": "approved",
                                "refund_result": refund_result
                            }

                        else:

                            print()
                            print(
                                "Human approval denied."
                            )

                            result = {
                                "order_id": order_id,
                                "refund_amount": refund_amount,
                                "human_approval": "denied",
                                "refund_result": {
                                    "status": "refund_not_processed"
                                }
                            }

                    # ------------------------------
                    # Automatic refund
                    # ------------------------------

                    else:

                        print()
                        print(
                            "Refund is within automatic "
                            "approval limit."
                        )

                        refund_result = process_refund(
                            order_id,
                            refund_amount
                        )

                        print(
                            "Refund result:",
                            refund_result
                        )

                        result = {
                            "order_id": order_id,
                            "refund_amount": refund_amount,
                            "human_approval": "not_required",
                            "refund_result": refund_result
                        }

            # ==================================
            # Send result back to model
            # ==================================

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result)
                }
            )

        # ======================================
        # Continue conversation
        # ======================================

        response = client.responses.create(
            model="gpt-5.6",
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools
        )

    # ==========================================
    # Maximum steps reached
    # ==========================================

    return (
        "The agent stopped because it reached "
        "the maximum number of steps."
    )


# ==========================================
# Run Demo
# ==========================================

print()
print("==========================================")
print("       ACME CUSTOMER SUPPORT AGENT")
print("==========================================")
print()
print("Type 'exit' to stop.")
print()

while True:

    user_message = input("Customer: ")

    if user_message.lower() == "exit":
        break

    print()
    print("Agent is working...")

    answer = run_agent(user_message)

    print()
    print("Agent:", answer)
    print()