import os
from scrapegraphai.graphs import SmartScraperGraph
from openai import OpenAI
from trulens_eval import Feedback, OpenAI as fOpenAI, Tru, Provider, Select, TruBasicApp

class TrulensEvaluator:
    """
    Class for evaluating Trulens using SmartScraperGraph.

    Attributes:

        tru_llm_standalone_recorder: TruBasicApp instance for recording.

    Methods:
        evaluate: Evaluates Trulens using SmartScraperGraph.
        llm_standalone: Standalone function for Trulens evaluation.
    """

    def __init__(self):
        standalone = StandAlone()
        f_custom_function = Feedback(standalone.json_complaint).on(
            my_text_field=Select.RecordOutput
        )
        os.environ["OPENAI_API_KEY"] = os.environ["OPENAI_APIKEY"]
        client = OpenAI()
        tru = Tru()
        tru.reset_database()
        fopenai = fOpenAI()
        f_relevance = Feedback(self.fopenai.relevance).on_input_output()
        tru_llm_standalone_recorder = TruBasicApp(self.llm_standalone, app_id="smart_scraper_evaluator", feedbacks=[self.f_relevance, self.f_custom_function])

    def evaluate(self, graph_params : list[tuple[str, str, dict]]):
        """
        Evaluates Trulens using SmartScraperGraph and starts the dashboard.

        Args:
            graph_params: List of tuples containing graph parameters.

        Returns:
            None
        """
        with self.tru_llm_standalone_recorder as recording:
            for params in graph_params:
                output = SmartScraperGraph(*params).run()
                self.tru_llm_standalone_recorder.app(params[0], output)
        self.tru.run_dashboard()

    def llm_standalone(self, prompt, response):
        """
        Standalone function for Trulens evaluation. Private method.

        Args:
            prompt: Prompt for evaluation.
            response: Response from evaluation.

        Returns:
            str: Response as a string.
        """
        print(f"Prompt: {prompt}")
        return str(response)

"""
Class for standalone Trulens evaluation. Personalise
"""
class StandAlone(Provider):
    def json_complaint(self, my_text_field: str) -> float:
        if '{' in my_text_field and '}' in my_text_field and ':' in my_text_field:
            return 1.0
        else:
            return 0.0
        
