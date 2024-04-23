"""
Provides the base class for all Agents 
"""

from abc import ABC
import vertexai
from vertexai.language_models import TextGenerationModel
from vertexai.language_models import CodeGenerationModel
from vertexai.language_models import CodeChatModel
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory,HarmBlockThreshold



from utilities import PROJECT_ID, PG_REGION
vertexai.init(project=PROJECT_ID, location=PG_REGION)



class Agent(ABC):
    """
    The core class for all Agents
    """

    agentType: str = "Agent"

    def __init__(self,
                model_id:str):
        """
        Args:
            PROJECT_ID (str | None): GCP Project Id.
            dataset_name (str): 
            TODO
        """

        self.model_id = model_id 

        if model_id == 'code-bison-32k':
            self.model = CodeGenerationModel.from_pretrained('code-bison-32k')
        elif model_id == 'text-bison-32k':
            self.model = TextGenerationModel.from_pretrained('text-bison-32k')
        elif model_id == 'codechat-bison-32k':
            self.model = CodeChatModel.from_pretrained("codechat-bison-32k")
        elif model_id == 'gemini-1.0-pro':
            self.model = GenerativeModel("gemini-1.0-pro-001")
            self.safety_settings: Optional[dict] = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        else:
            raise ValueError("Please specify a compatible model.")

    def generate_llm_response(self,prompt):
        context_query = self.model.generate_content(prompt,safety_settings=self.safety_settings,stream=False)
        return str(context_query.candidates[0].text).replace("```sql", "").replace("```", "")