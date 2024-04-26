# Local models
The two websites benchmark are:
- Example 1:  https://perinim.github.io/projects
- Example 2: https://www.wired.com (at 17/4/2024)

Both are strored locally as txt file in .txt format  because in this way we do not have to think about the internet connection

The time is measured in seconds

The model runned for this benchmark is Mistral on Ollama with nomic-embed-text

In particular, is tested with ScriptCreatorGraph

| Hardware               | Model                                   | Example 1 | Example 2 |
| ---------------------- | --------------------------------------- | --------- | --------- |
| Macbook 14' m1 pro     | Mistral on Ollama with nomic-embed-text | 30.54s    | 35.76s    |
| Macbook m2 max         | Mistral on Ollama with nomic-embed-text | 18,46s    | 19.59     |
| Macbook 14' m1 pro<br> | Llama3 on Ollama with nomic-embed-text  | 27.82s    | 29.98s    |
| Macbook m2 max<br>     | Llama3 on Ollama with nomic-embed-text  | 20.83s    | 12.29s    |


**Note**: the examples on Docker are not runned on other devices than the Macbook because the performance are to slow (10 times slower than Ollama). 
# Performance on APIs services
### Example 1: personal portfolio 
**URL**: https://perinim.github.io/projects
**Task**: List me all the projects with their description.

| Name                | Execution time | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ------------------- | ---------------| ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo       | 4.50s          | 1897         | 1802          | 95                | 1                   | 0.002893       |
| gpt-4-turbo         | 7.88s          | 1920         | 1802          | 118               | 1                   | 0.02156        |

### Example 2: Wired
**URL**: https://www.wired.com
**Task**: List me all the articles with their description.

| Name                | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo       |   Error (text too long)  |      -       |      -        |         -         |           -         |        -       |
| gpt-4-turbo         |   Error (TPM limit reach)|      -       |      -        |         -         |           -         |        -       |

