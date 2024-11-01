import openai
import os

# The file secret_key_setup.py contains a single line of code with the variable imported_secret_key set equal
# to the API secret key received from OpenAI's API platform
from secret_key_setup import imported_secret_key

# Set up
os.environ["OPENAI_API_KEY"] = imported_secret_key
openai_api_key = os.environ["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=openai_api_key)

# Actual Function Code
def openai_setup(model_name:str='gpt-3.5-turbo',
                 messages:list=['Hello'],
                 temperature: float=0.6):
    """
    Retrieves an AI response by making a request to the OpenAI API.
    :param model_name: a string with the name of the open AI model
    :param messages: a list of messages to pass to the AI
    :param temperature: the temperature to use. A value of 0 ensures reproducibility/no creativity from the
        AI while numbers closer to 1 yield more creative and more variable responses
    :return: out, a string of the AI's response to messages
    """
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature
        )
        out = completion.choices[0].message.content
        return out
    except openai.Timeout as e:
        # Handle timeout error, e.g. retry or log
        print(f"OpenAI API request timed out: {e}")
        pass
    except openai.APIConnectionError as e:
        # Handle connection error, e.g. check network or log
        print(f"OpenAI API request failed to connect: {e}")
        pass
    except openai.APIError as e:
        # Handle API error, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    # except openai.InvalidRequestError as e:
    #     # Handle invalid request error, e.g. validate parameters or log
    #     print(f"OpenAI API request was invalid: {e}")
    #     pass
    except openai.AuthenticationError as e:
        # Handle authentication error, e.g. check credentials or log
        print(f"OpenAI API request was not authorized: {e}")
        pass
    # except openai.PermissionError as e:
    #     # Handle permission error, e.g. check scope or log
    #     print(f"OpenAI API request was not permitted: {e}")
    #     pass
    except openai.RateLimitError as e:
        # Handle rate limit error, e.g. wait or log
        print(f"OpenAI API request exceeded rate limit: {e}")
        pass

def chatbot(user_input:str,
            temperature:float=0.60,
            model:str="gpt-3.5-turbo",
            system_prompt:str=None):
    """
    Geneartes a response from the AI-based chat bot. The conversation history is not retained.
    :param user_input:
    :param temperature:
    :param model:
    :param system_prompt:
    :return:
    """
    if system_prompt is None:
        system_prompt = "You are a friendly bot that seeks to provide the best answers possible."

    msg_temp = [{"role": "system",
                 "content": system_prompt},
                {"role": "user",
                 "content": user_input}]
    out = openai_setup(model_name=model,
                       temperature=temperature,
                       messages=msg_temp)
    return out


if __name__ == "__main__":
    question = "Tell me a joke"
    print(f"User's Question: {question}")
    print(f"\nAI's Response: {chatbot(user_input=question)}")
    print()
