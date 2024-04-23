# Local models
The two websites benchmark are:
- Example 1:  https://perinim.github.io/projects
- Example 2: https://www.wired.com (at 17/4/2024)

Both are strored locally as txt file in .txt format  because in this way we do not have to think about the internet connection

In particular, is tested with SmartScraper

| Hardware           | Moodel                                  | Example 1 | Example 2 |
| ------------------ | --------------------------------------- | --------- | --------- |
| Macbook 14' m1 pro | Mistral on Ollama with nomic-embed-text | 11.60s    | 26.61s    |
| Macbook m2 max     | Mistral on Ollama with nomic-embed-text | 8.05s     | 12.17s    |
| Macbook 14' m1 pro | Llama3 on Ollama with nomic-embed-text  | 29.871    | 35.32     |
| Macbook m2 max     | Llama3 on Ollama with nomic-embed-text  | 18.36s    | 78.32s    |


**Note**: the examples on Docker are not runned on other devices than the Macbook because the performance are to slow (10 times slower than Ollama). Indeed the results are the following:

| Hardware           | Example 1 | Example 2 |
| ------------------ | --------- | --------- |
| Macbook 14' m1 pro | 139.89    | Too long  |
# Performance on APIs services
### Example 1: personal portfolio 
**URL**: https://perinim.github.io/projects
**Task**: List me all the projects with their description.

| Name                | Execution time | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ------------------- | ---------------| ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo       | 5.58s          | 445          | 272           | 173               | 1                   | 0.000754       |
| gpt-4-turbo         | 9.76s          | 445          | 272           | 173               | 1                   | 0.00791        |

### Example 2: Wired
**URL**: https://www.wired.com
**Task**: List me all the articles with their description.

| Name                | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo       | 6.50                     | 2442         | 2199          | 243               | 1                   | 0.003784       |
| gpt-4-turbo         | 76.07                    | 3521         | 2199          | 1322              | 1                   | 0.06165        |

