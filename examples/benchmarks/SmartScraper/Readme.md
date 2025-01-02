# Local models
# Local models
The two websites benchmark are:
- Example 1:  https://perinim.github.io/projects
- Example 2: https://www.wired.com (at 17/4/2024)

Both are strored locally as txt file in .txt format  because in this way we do not have to think about the internet connection

| Hardware               | Model                                   | Example 1 | Example 2 |
| ---------------------- | --------------------------------------- | --------- | --------- |
| Macbook 14' m1 pro     | Mistral on Ollama with nomic-embed-text | 16.291s   | 38.74s    |
| Macbook m2 max         | Mistral on Ollama with nomic-embed-text |           |           |
| Macbook 14' m1 pro<br> | Llama3 on Ollama with nomic-embed-text  | 12.88s    | 13.84s    |
| Macbook m2 max<br>     | Llama3 on Ollama with nomic-embed-text  |           |           |

**Note**: the examples on Docker are not runned on other devices than the Macbook because the performance are to slow (10 times slower than Ollama). Indeed the results are the following:

| Hardware           | Example 1 | Example 2 |
| ------------------ | --------- | --------- |
| Macbook 14' m1 pro | 139.89    | Too long  |
# Performance on APIs services
### Example 1: personal portfolio 
**URL**: https://perinim.github.io/projects
**Task**: List me all the projects with their description.

| Name                            | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ------------------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo                   | 4.132s                   | 438          | 303           | 135               | 1                   | 0.000724       |
| gpt-4-turbo-preview             | 6.965s                   | 442          | 303           | 139               | 1                   | 0.0072         |
| gpt-4-o                         | 4.446s                   | 444          | 305           | 139               | 1                   | 0              |
| Grooq with nomic-embed-text<br> | 1.335s                   | 648          | 482           | 166               | 1                   | 0              |

### Example 2: Wired
**URL**: https://www.wired.com
**Task**: List me all the articles with their description.

| Name                            | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ------------------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo                   | 8.836s                   | 1167         | 726           | 441               | 1                   | 0.001971       |
| gpt-4-turbo-preview             | 21.53s                   | 1205         | 726           | 479               | 1                   | 0.02163        |
| gpt-4-o                         | 15.27s                   | 1400         | 715           | 685               | 1                   | 0              |
| Grooq with nomic-embed-text<br> | 3.82s                    | 2459         | 2192          | 267               | 1                   | 0              |
