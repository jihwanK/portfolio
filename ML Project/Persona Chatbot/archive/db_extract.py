import requests
import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
import json

# OpenAI API 키 입력
openai.api_key = 'sk-'

# OpenAI GPT 모델 설정
class CustomOpenAI(OpenAI):
    def _call(self, prompt, **kwargs):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=1500, # 토큰 제한
            **kwargs
        )
        return response.choices[0].text.strip()

llm = CustomOpenAI()

# 발화자 추론
prompt_template = """
This is a description of Pooh in this novel.
In the Milne books, Pooh is naive and slow-witted, but he is also friendly, thoughtful, and steadfast. Although he and his friends agree that he is -a bear of very little brain-, Pooh is occasionally acknowledged to have a clever idea, usually driven by common sense. These include riding in Christopher Robin's umbrella to rescue Piglet from a flood, discovering -the North Pole- by picking it up to help fish Roo out of the river, inventing the game of Poohsticks, and getting Eeyore out of the river by dropping a large rock on one side of him to wash him towards the bank.

Pooh at Owl's house; illustration by E. H. Shepard
Pooh is also a talented poet and the stories are frequently punctuated by his poems and -hums-. Although he is humble about his slow-wittedness, he is comfortable with his creative gifts. When Owl's house blows down in a windstorm, trapping Pooh, Piglet and Owl inside, Pooh encourages Piglet (the only one small enough to do so) to escape and rescue them all by promising that -a respectful Pooh song- will be written about Piglet's feat. Later, Pooh muses about the creative process as he composes the song.

Pooh and a honey (-hunny-) pot, E. H. Shepard illustration from Winnie-the-Pooh (1926)
Pooh is very fond of food, particularly honey (which he spells -hunny-), but also condensed milk and other items. When he visits friends, his desire to be offered a snack is in conflict with the impoliteness of asking too directly. Though intent on giving Eeyore a pot of honey for his birthday, Pooh could not resist eating it on his way to deliver the present and so instead gives Eeyore -a useful pot to put things in-. When he and Piglet are lost in the forest during Rabbit's attempt to -unbounce- Tigger, Pooh finds his way home by following the -call- of the honeypots from his house. Pooh makes it a habit to have -a little something- around 11:00 in the morning. As the clock in his house -stopped at five minutes to eleven some weeks ago-, any time can be Pooh's snack time.
Pooh is very social. After Christopher Robin, his closest friend is Piglet, and he most often chooses to spend his time with one or both of them. But he also habitually visits the other animals, often looking for a snack or an audience for his poetry as much as for companionship. His kind-heartedness means he goes out of his way to be friendly to Eeyore, visiting him and bringing him a birthday present and building him a house, despite receiving mostly disdain from Eeyore in return. Devan Coggan of Entertainment Weekly saw a similarity between Pooh and Paddington Bear, two -extremely polite British bears without pants-, adding that -both bears share a philosophy of kindness and integrity-.

novel line:
{dialogues}

Dialogue including the speaker:

"""

# LangChain 프롬프트 템플릿과 체인 설정
prompt = PromptTemplate(
    input_variables=["dialogues"],
    template=prompt_template
)
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt
)

# 원작 소설을 다운로드
def download_novel(url):
    response = requests.get(url)
    response.raise_for_status()  # 오류 발생 시 예외 발생
    return response.text

# 원작 소설 텍스트에서 대사를 추출
def extract_dialogues(novel_text):
    dialogues = []
    in_dialogue = False
    current_dialogue = ""
    for line in novel_text.splitlines():
        if '"' in line:
            if in_dialogue:
                current_dialogue += " " + line.strip().strip('"')
                dialogues.append(current_dialogue)
                current_dialogue = ""
                in_dialogue = False
            else:
                current_dialogue = line.strip().strip('"')
                in_dialogue = True
        elif in_dialogue:
            current_dialogue += " " + line.strip()
    return dialogues

# 대사 텍스트 분할
def split_text(text, max_length=1500):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# JSON 파일에 데이터 저장
def save_to_json(data, filename='pooh_script.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 메인 함수
def main():
    url = "https://www.gutenberg.org/cache/epub/67098/pg67098.txt" # 위니더푸 원작 소설 링크
    
    # 원작 소설 다운로드
    novel_text = download_novel(url)
    
    # 대사 추출
    dialogues_list = extract_dialogues(novel_text)
    dialogues = "\n".join(dialogues_list)
    
    # 대사 텍스트를 최대 길이에 맞게 분할
    chunks = split_text(dialogues)
    
    results = []
    for chunk in chunks:
        # 발화자 태그
        result = llm_chain.run(chunk)

        
        # 결과를 JSON 형식으로 변환
        for line in result.split('\n'):
            if ':' in line:
                role, dialogue = line.split(':', 1)
                results.append({
                    "role": role.strip(),
                    "dialogue": dialogue.strip()
                })
    
    # JSON 파일에 저장
    save_to_json(results)

if __name__ == "__main__":
    main()
