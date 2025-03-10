from typing import Dict
from llama_cpp import Llama

def create_prompt_data() -> Dict:
  return {
      "system": """당신은 휠체어 사용자의 자연어 명령을 해석하여 적절한 이동 명령으로 변환하는 시스템입니다. 
          1. 사용 가능한 명령어는 다음과 같습니다:
              - call(person): 호출 (person: nurse, doctor)
              - go(location): 지정된 위치로 이동 (location: rooms, breakroom, toilet, home)
              - STOP: 정지
          2. 명령은 ```[command1(), command2(), ...]``` 형식으로 출력되어야 합니다.
          3. 수행하지 못하는 명령을 내렸을 때는 '수행하지 못하는 명령어 입니다.' 라고 반환합니다. 
      """,
      "examples": [
          {"input": "화장실로 가줘", "output": "화장실로 이동합니다. ```[go(toilet), STOP]```"},
          {"input": "병실로 가줘 ", "output": "병실로 이동합니다. ```[go(rooms), STOP]```"},
          {"input": "휴게실로 가줘 ", "output": "휴게실로 이동합니다. ```[go(breakroom), STOP]```"},
          {"input": "제자리로 돌아가", "output": "제자리로 이동합니다. ```[go(home), STOP]```"},
          {"input": "돌아가", "output": "제자리로 이동합니다. ```[go(home), STOP]```"},
          {"input": "간호사 호출해줘", "output": "간호사를 호출하겠습니다. ```[call(nurse), STOP]```"},
          # {"input": "무대로 가줘", "output": "무대로 이동합니다. ```[go(stage), STOP]```"},
      ],
      
      "locations": {
          "rooms": "병실",
          "breakroom": "휴게실",
          "toilet": "화장실",
          "home": "제자리"
          # "stage": "무대",
      }
  }

def prepare_model_prompt(prompt_data: Dict, user_input: str) -> str:
    prompt = prompt_data["system"] + "\n\nexample:\n"
    
    # Add example inputs and outputs
    for example in prompt_data["examples"]:
        prompt += f"input: {example['input']}\noutput: {example['output']}\n\n"
    
    # Add current user input
    # prompt += f"input: {user_input}\noutput:"
    
    return prompt

def load_wheelchair_model(model_path: str):
    llms = Llama(
        model_path=model_path,
        n_ctx=2048,
        n_gpu_layers=-1,
        temperature=0.1,
        stop =["\n", "\n\n", "input:", "```\n"],  # 모델이 적절한 위치에서 멈추도록 설정
        f16_kv=True,
        verbose=True,
        # chat_format="qwen",
    )
    return llms

def run(llms, template, user_input, **kwargs):
    
    messages = [
      {"role": "system", "content": template},
      {"role": "user", "content": user_input}
      ]

    kwargs["stream"] = True
    result = ""

    for chunk in llms.create_chat_completion(messages=messages, **kwargs):
        if "choices" in chunk and chunk["choices"][0].get("delta", {}).get("content"):
            print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
            result += chunk["choices"][0]["delta"]["content"]

    return result


def main():
    MODEL_PATH = "/app/models/qwen2.5-0.5b-instruct-fp16.gguf"
    prompt_data = create_prompt_data()  # 사용자 입력을 포함한 프롬프트 생성
    llms = load_wheelchair_model(MODEL_PATH)
    
    print("휠체어 명령 해석기 (종료하려면 'q' 입력)")
    while True:
        user_input = input(">> ")
        
        if user_input.lower() == "q":
            break

        try:
            full_prompt = prepare_model_prompt(prompt_data, user_input)
            run(llms, full_prompt, user_input)
            print("\n")
        except Exception as e:
            print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
