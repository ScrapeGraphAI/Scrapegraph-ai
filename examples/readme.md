# Benchmark comparison for the models
- Hardware: Macbook pro 14 inches with m1 pro and 16 GB of ram

### Example 1: personal portfolio 
**URL**: https://perinim.github.io/projects
**Task**: List me all the projects with their description.

| Name                                | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ----------------------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo                       | 35.98                    | 858          | 512           | 346               | 2                   | 0.00146        |
| gpt-4-turbo-preview                 | 13.907                   | 866          | 512           | 354               | 2                   | 0.01574        |
| Ollama with Mistral and embeddings  | 26.10                    | 0            | 0             | 0                 | 0                   | 0              |
| Docker with  Mistral and embeddings | 240.22                   | 0            | 0             | 0                 | 0                   | 0              |
### Example 2: Wired
**URL**: https://www.wired.com
**Task**: List me all the articles with their description.

| Name                                | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ----------------------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo                       | 87.03                    | 3780         | 3760          | 3000              | 2                   | 0.01319        |
| gpt-4-turbo-preview                 | 74.90                    | 5306         | 3060          | 2246              | 2                   | 0.09798        |
| Ollama with Mistral and embeddings  | 60.915                   | 0            | 0             | 0                 | 0                   | 0              |
| Docker with  Mistral and embeddings | 612.48                   | 0<br>        | 0<br>         | 0<br>             | 0<br>               | 0<br>          |

### Example 3: Amazon product page
**URL**: https://www.amazon.it/s?k=alexa&__mk_it_IT=ÅMÅŽÕÑ&crid=1WWVF1RGDBBSB&sprefix=alex%2Caps%2C114&ref=nb_sb_noss_2
**Task**: List me all the articles with their the costs and image url.

| Name                                | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ----------------------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo                       | 145.55                   | 26038        | 18091         | 7947              | 5                   | 0.04303        |
| gpt-4-turbo-preview                 | 82.38                    | 15640        | 13698         | 1942              | 2                   | 0.19524        |
| Ollama with Llama2 and embeddings   | 200.77                   | 0<br>        | 0<br>         | 0<br>             | 0<br>               | 0<br>          |
| Docker with  Mistral and embeddings | 2008.32                  | 0<br>        | 0<br>         | 0<br>             | 0<br>               | 0<br>          |
## Hosting services
[[💻 Provider costs informations]]
