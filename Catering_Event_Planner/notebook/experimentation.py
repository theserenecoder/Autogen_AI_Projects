import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent, SocietyOfMindAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
load_dotenv()

from autogen_agentchat.ui import Console

async def main():
    model_client = OpenAIChatCompletionClient(model='gpt-4o-mini')

    # Inner Agent Team

    planner_agent = AssistantAgent(
        name = 'PlannerAgent',
        model_client=model_client,
        description='An agent that interprests the user request and build a structured food menu',
        system_message="""
        You are a meticulous PlannerAgent specializing in event catering. 
        Your primary function is to interpret a user's high-level event brief, including the number of guests, dietary restrictions, event type (e.g., formal, casual), and food budget. 
        Break this information down into a structured, executable plan. 
        Your output should be a clear, actionable menu outline (e.g., "one appetizer, one main course, one dessert"). 
        Pass this plan to the 'RecipeAgent' to begin the creative process. 
        Do not create recipes yourself; your job is to set the stage.
        """
    )

    recipe_agent = AssistantAgent(
        name = 'RecipeAgent',
        model_client=model_client,
        description="An agent that create receipe based on the food menu",
        system_message="""
        You are a creative and knowledgeable RecipeAgent. 
        Your role is to generate detailed, appealing recipes based on the menu outline provided by the PlannerAgent. 
        Each recipe must include a list of ingredients, precise measurements, and step-by-step instructions. 
        You must adhere strictly to the dietary restrictions and event style. 
        After creating the recipes, pass the full menu to the CritiqueAgent for a quality check.
        """
    )

    critique_agent = AssistantAgent(
        name = 'CritiqueAgent',
        model_client=model_client,
        description = 'An agent that evaluate the menu and receipes',
        system_message="""
        You are the CritiqueAgent, a practical and experienced culinary expert. 
        Your job is to rigorously evaluate the menu and recipes from the RecipeAgent. 
        
        Check for potential issues:

        1. Feasibility: Is the menu too complex for the given time and resources?

        2. Ingredient Conflicts: Do multiple dishes require the same piece of equipment (e.g., the oven) at the same time?

        3. Budget Adherence: Does the menu align with the per-person food budget?

        4. Consistency: Does the menu flow well? Are there any odd flavor combinations?
        
        Your final output should be either an approval of the menu or a detailed list of suggestions for the RecipeAgent to correct. 
        
        Once the menu is approved, you will signal the UserProxyAgent to present the menu to the human for review.
        """
    )

    user_agent = UserProxyAgent(
        name = 'user',
        description='A proxy agent that represent the user',
        input_func=input
    )

    ## Termination Condition
    inner_team_termination = TextMentionTermination('APPROVE') | MaxMessageTermination(13)

    culinary_team = RoundRobinGroupChat(
        participants=[planner_agent,recipe_agent,critique_agent, user_agent],
        termination_condition=inner_team_termination
    )


    ## Society of mind team

    outer_culinary_team = SocietyOfMindAgent(
        name = 'CulinaryTeamAgent',
        team = culinary_team,
        model_client=model_client,
        description = 'A culinary team agent which will build the menu and receipes.',
        response_prompt="""
        You are the CulinaryTeamAgent, acting as a single, specialized expert within the outer team. 
        Your sole purpose is to produce a finalized, human-approved menu from the inner 'Culinary Team' workflow. 
        You do not generate recipes yourself. 
        Once the inner team has successfully created and gotten a menu approved by the human, you will provide this final menu and ingredients required to the LogisticsAgent as a complete input.
        You will also save the Complete Menu, Ingredients and Recipes as a .docx file.
        If the human rejects the menu, you will manage the inner team's revision process until a menu is approved.
        """
    )

    ## Logistic Agent
    logistic_agent = AssistantAgent(
        name = 'LogisticAgent',
        model_client=model_client,
        description='An agents which creates a complete blueprint.',
        system_message="""
        You are the LogisticsAgent, responsible for turning a finalized menu into a concrete action plan. 
        
        Your task is to receive the approved menu from the CulinaryTeamAgent and generate a detailed logistical blueprint. 
        
        This includes:

        1. Shopping List: A comprehensive list of all ingredients and quantities.

        2. Preparation Timeline: A step-by-step schedule from food prep to serving.

        3. Equipment List: A list of necessary cooking tools and equipment.
        
        Pass this complete logistics plan to the BudgetAgent.
        """
    )

    ## budget agent
    budget_agent = AssistantAgent(
        name = 'BudgetAgent',
        model_client=model_client,
        description='An agent which calculates total budget of the event.',
        system_message="""
        You are the BudgetAgent, a financial analyst for the event. 
        Your job is to calculate the total cost of the event based on the logistics plan and approved menu. 
        You will take the shopping list and equipment needs and generate a comprehensive financial report. 
        
        This report must include:

        1. Estimated cost of ingredients.

        2. Estimated cost of equipment rentals (if any).

        3. A final, total budget for the event.
        
        Provide this final budget report along with the logistics plan to the UserProxyAgent for final review and approval.
        """
    )
    
    final_approval = UserProxyAgent(
        name='FinalApproval',
        description='A proxy agent that represent the user for final approval',
        input_func=input
    )

    ## Termination condition
    outer_team_termination = TextMentionTermination('APPROVE')

    ## Defining outer team
    event_manager = RoundRobinGroupChat(
        participants=[outer_culinary_team, logistic_agent, budget_agent,final_approval],
        termination_condition=outer_team_termination,
        max_turns=3
    )
    
    task = """
    Please plan a menu for a formal dinner party for 30 people. The budget for food is $50 per person. 
    The guests have no dietary restrictions but prefer a menu that includes a mix of textures and flavors. Keep the item list to 5 items only
    """
    
    stream = event_manager.run_stream(task=task)
    await Console(stream)
    
asyncio.run(main())