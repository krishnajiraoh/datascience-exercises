import openai


def test_open_ai(model_name):
    client = openai.OpenAI(
        api_key="sk-TnjQlouvvKw2LVrIXtdjsg",
        base_url="https://genai-gateway.azure-api.net/"
        # LiteLLM Proxy is OpenAI compatible, Read More: https://docs.litellm.ai/docs/proxy/user_keys
    )
    response = client.chat.completions.create(
        model=model_name,  # model to send to the proxy
        messages=[
            {
                "role": "user",
                "content": "this is a test request, write a short poem of 4 lines"
            }
        ]
    )
    print(f"\nResponse from {model_name}:")
    print(response.choices[0].message.content)


def test_all_models():
    # List of models to test
    azure_models = ["gpt-4", "gpt-4o", "gpt-4o-mini"]
    anthropic_models = ["claude-3-5-sonnet-v2", "claude-3-5-haiku"]
    llm_models = ["US-Nova-Micro", "Phi-3-small-128k-instruct", "command-r-plus-v1", "aws-mistral-mixtral-8x7b-instruct-v0"]
    
    print("\nTesting Azure OpenAI Models:")
    for model in azure_models:
        try:
            test_open_ai(model)
        except Exception as e:
            print(f"Error testing {model}: {str(e)}")
    
    print("\nTesting Anthropic Claude Models:")
    for model in anthropic_models:
        try:
            test_open_ai(model)
        except Exception as e:
            print(f"Error testing {model}: {str(e)}")
            
    print("\nTesting Other LLM Models:")
    for model in llm_models:
        try:
            test_open_ai(model)
        except Exception as e:
            print(f"Error testing {model}: {str(e)}")


def test_embedding_model():
    client = openai.OpenAI(
        api_key="sk-TnjQlouvvKw2LVrIXtdjsg",
        base_url="https://genai-gateway.azure-api.net/"
        # LiteLLM Proxy is OpenAI compatible, Read More: https://docs.litellm.ai/docs/proxy/user_keys
    )
    embedding_models = ["text-embedding-3-large", "Titan-Text-Embeddings-V2"]
    print("\nTesting Embedding Models:")
    for model in embedding_models:
        try:
            response = client.embeddings.create(
                model=model,
                input="This is a test"
            )
            print(f"✓ {model}: Embedding model test successful!")
            if hasattr(response, 'data'):
                print(f"Embedding dimensions: {len(response.data[0].embedding)}")
        except Exception as e:
            print(f"Error testing {model}: {str(e)}")


if __name__ == "__main__":
    test_all_models()
    test_embedding_model()
