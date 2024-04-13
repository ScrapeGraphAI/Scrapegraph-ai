# Benchmark analysis
# Local models
The 3 websites benchmark are:
- Example 1:  https://perinim.github.io/projects
- Example 2: https://www.wired.com
- Example 3: https://www.amazon.it/s?k=alexa&__mk_it_IT=ÅMÅŽÕÑ&crid=1WWVF1RGDBBSB&sprefix=alex%2Caps%2C114&ref=nb_sb_noss_2

The time is measured in seconds

The model runned for this benchmark is Mistral on Ollama with nomic-embed-text

| Hardware                | Example 1 | Example 2 | Example 3 |
| ----------------------- | --------- | --------- | --------- |
| Macbook pro 14 inches   | 26.10<br> | 60.915    | 200.77    |
| Ubuntu with Radeon M260 | 296.98    | 1003.56   | /         |

**Note**: the examples on Docker are not runned on other devices than the Macbook because the performance are to slow (10 times slower than Ollama). Indeed the results are the following:

| Hardware              | Example 1 | Example 2 | Example 3 |
| --------------------- | --------- | --------- | --------- |
| Macbook pro 14 inches | 240.22    | 612.48    | 2008.32   |

# Performance on APIs services
### Example 1: personal portfolio 
**URL**: https://perinim.github.io/projects
**Task**: List me all the projects with their description.

| Name                | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo       | 35.98                    | 858          | 512           | 346               | 2                   | 0.00146        |
| gpt-4-turbo-preview | 13.907                   | 866          | 512           | 354               | 2                   | 0.01574        |

### Example 2: Wired
**URL**: https://www.wired.com
**Task**: List me all the articles with their description.

| Name                | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo       | 87.03                    | 3780         | 3760          | 3000              | 2                   | 0.01319        |
| gpt-4-turbo-preview | 74.90                    | 5306         | 3060          | 2246              | 2                   | 0.09798        |

### Example 3: Amazon product page
**URL**: https://www.amazon.it/s?k=alexa&__mk_it_IT=ÅMÅŽÕÑ&crid=1WWVF1RGDBBSB&sprefix=alex%2Caps%2C114&ref=nb_sb_noss_2
**Task**: List me all the articles with their the costs and image url.

| Name                | Execution time (seconds) | total_tokens | prompt_tokens | completion_tokens | successful_requests | total_cost_USD |
| ------------------- | ------------------------ | ------------ | ------------- | ----------------- | ------------------- | -------------- |
| gpt-3.5-turbo       | 145.55                   | 26038        | 18091         | 7947              | 5                   | 0.04303        |
| gpt-4-turbo-preview | 82.38                    | 15640        | 13698         | 1942              | 2                   | 0.19524        |

