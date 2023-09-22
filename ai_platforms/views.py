from django.shortcuts import render
import openai
import google.generativeai as palm
from ai_platforms.models import AIPlatform


# Create your views here.
class BaseAIPlatform:
    model = None
    prompt = []

    def __init__(self) -> None:
        pass

    async def get_answer(self, messages: list) -> str:
        pass


class OpenAI(BaseAIPlatform):
    def __init__(self) -> None:
        super().__init__()
        openai.api_key = AIPlatform.objects.get(name="OpenAI").key
        self.model = openai

    async def get_answer(self, messages: list) -> str:
        prompt = []
        for message in messages:
            if message["role"] == "user":
                prompt.append(message)
            else:
                prompt.append({"role": "assistant", "content": message["content"]})
        response = await self.model.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=prompt,
            temperature=0.2,
        )
        response = list(response.choices)[0]
        response = response.to_dict()["message"]["content"]
        if response == None:
            response = "Sorry, I can't understand your request."
        return {"role": "openai", "content": response}


class PaLM(BaseAIPlatform):
    def __init__(self) -> None:
        super().__init__()
        palm.configure(api_key=AIPlatform.objects.get(name="PaLM").key)
        self.model = palm

    async def get_answer(self, messages: list) -> str:
        prompt = []
        for message in messages:
            prompt.append(message["content"])
        response = await self.model.chat_async(
            model="models/chat-bison-001",
            messages=prompt,
            temperature=0.2,
        )
        if response.last == None:
            response = "Sorry, I can't understand your request."
        else:
            response = response.last
        return {"role": "palm", "content": response}
