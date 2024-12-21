from oscopilot import FridayAgent
from oscopilot import ToolManager
from oscopilot import FridayExecutor, FridayPlanner, FridayRetriever
from oscopilot.utils import setup_config, setup_pre_run
from oscopilot import LightFriday

args = setup_config()
if not args.query:
    args.query = "Add a schedule on google calendar for tomorrow morning 8:00, I'll go shopping"
task = setup_pre_run(args)
agent = FridayAgent(FridayPlanner, FridayRetriever, FridayExecutor, ToolManager, config=args)
agent.run(task=task)
#light_friday = LightFriday(args)
#light_friday.run(task)

