# Routes user messages to the appropriate specialist agent:
# - Nova: Web search, current events
# - Wolf: Wikipedia, knowledge, research
# - Sage: Math, calculations
# - Pixel: Image generation & analysis
# - Scribe: Documents, writing, files
# - Onyx: Code, programming

import os
import time
from dotenv import load_dotenv
from typing import TypedDict, Literal

load_dotenv()