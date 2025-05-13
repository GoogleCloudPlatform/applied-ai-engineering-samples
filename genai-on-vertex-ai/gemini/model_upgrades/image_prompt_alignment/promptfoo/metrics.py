import json
from typing import Any, Dict, Union

def assert_prompt_alignment(model_response: str, context: Dict[str, Any]) -> Union[Dict[str, Any], bool]:
    '''Parse the final score and the list of identified gaps from the JSON markdown block in model response.'''
    json_output = json.loads(model_response.split('```json\n')[1].split('\n```')[0])
    score = json_output['score']
    if score < 100: # The autorater prompt returns percentage scores
        return {'pass': False, 'score': score, 'reason': '\n'.join(json_output['gaps'])}
    else:
        return True