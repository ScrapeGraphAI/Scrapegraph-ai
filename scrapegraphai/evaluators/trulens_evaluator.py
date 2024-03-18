"""Module for making the RAG"""
from trulens_eval import Feedback, OpenAI, Tru, Provider, Select, TruBasicApp
from scrapegraphai.graphs import SmartScraperGraph


class TrulensEvaluator:
    """
    Class for evaluating Trulens using SmartScraperGraph.

    Attributes:

        tru_llm_standalone_recorder: TruBasicApp instance for recording.

    Methods:
        evaluate: Evaluates Trulens using SmartScraperGraph.
        llm_standalone: Standalone function for Trulens evaluation.
    """

    def __init__(self, key: str):
        """ 
            Initialization of the class
            Arguments:
            -  key (str): openai key
        """
        standalone = StandAlone()
        self.f_custom_function = Feedback(standalone.json_complaint).on(
            my_text_field=Select.RecordOutput
        )
        self.tru = Tru()
        self.tru.reset_database()
        self.openai = OpenAI(api_key=key)
        self.f_relevance = Feedback(self.openai.relevance).on_input_output()
        self.tru_llm_standalone_recorder = TruBasicApp(self.llm_standalone,
                                                       app_id="smart_scraper_evaluator",
                                                       feedbacks=[self.f_relevance,
                                                                  self.f_custom_function])
        self.graph_output = []

    def evaluate(self, graph_params: list[tuple[str, str, dict]], dashboard: bool = True):
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
                self.graph_output.append(output)
                
        if dashboard:
            self.tru.run_dashboard()
        
        return (self.tru.get_records_and_feedback(app_ids=[])[0], self.graph_output)

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


class StandAlone(Provider):
    """
    Class for standalone Trulens evaluation. 
    """

    def json_complaint(self, my_text_field: str) -> float:
        """ 
        Args:
            - my_text_field (str): textfield
        """
        if '{' in my_text_field and '}' in my_text_field and ':' in my_text_field:
            return 1.0
        return 0.0
