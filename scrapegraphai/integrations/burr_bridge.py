"""
Bridge class to integrate Burr into ScrapeGraphAI graphs
[Burr](https://github.com/DAGWorks-Inc/burr)
"""
import re
import uuid
from hashlib import md5
from typing import Any, Dict, List, Tuple
import inspect
try:
    import burr
    from burr import tracking
    from burr.core import (Application, ApplicationBuilder,
                            State, Action, default, ApplicationContext)
    from burr.lifecycle import PostRunStepHook, PreRunStepHook
except ImportError:
    raise ImportError("""burr package is not installed. 
                      Please install it with 'pip install scrapegraphai[burr]'""")


class PrintLnHook(PostRunStepHook, PreRunStepHook):
    """
    Hook to print the action name before and after it is executed.
    """

    def pre_run_step(self, *, state: "State", action: "Action", **future_kwargs: Any):
        print(f"Starting action: {action.name}")

    def post_run_step(self, *, state: "State", action: "Action", **future_kwargs: Any):
        print(f"Finishing action: {action.name}")


class BurrNodeBridge(Action):
    """Bridge class to convert a base graph node to a Burr action.
    This is nice because we can dynamically declare 
    the inputs/outputs (and not rely on function-parsing).
    """

    def __init__(self, node):
        """Instantiates a BurrNodeBridge object.
        """
        super(BurrNodeBridge, self).__init__()
        self.node = node

    @property
    def reads(self) -> list[str]:
        return parse_boolean_expression(self.node.input)

    def run(self, state: State, **run_kwargs) -> dict:
        node_inputs = {key: state[key] for key in self.reads if key in state}
        result_state = self.node.execute(node_inputs, **run_kwargs)
        return result_state

    @property
    def writes(self) -> list[str]:
        return self.node.output

    def update(self, result: dict, state: State) -> State:
        return state.update(**result)

    def get_source(self) -> str:
        return inspect.getsource(self.node.__class__)


def parse_boolean_expression(expression: str) -> List[str]:
    """
    Parse a boolean expression to extract the keys 
    used in the expression, without boolean operators.

    Args:
        expression (str): The boolean expression to parse.

    Returns:
        list: A list of unique keys used in the expression.
    """

    # Use regular expression to extract all unique keys
    keys = re.findall(r'\w+', expression)
    return list(set(keys))  # Remove duplicates


class BurrBridge:
    """
    Bridge class to integrate Burr into ScrapeGraphAI graphs.

    Args:
        base_graph (BaseGraph): The base graph to convert to a Burr application.
        burr_config (dict): Configuration parameters for the Burr application.

    Attributes:
        base_graph (BaseGraph): The base graph to convert to a Burr application.
        burr_config (dict): Configuration parameters for the Burr application.
        tracker (LocalTrackingClient): The tracking client for the Burr application.
        app_instance_id (str): The instance ID for the Burr application.
        burr_inputs (dict): The inputs for the Burr application.
        burr_app (Application): The Burr application instance.

    Example:
        >>> burr_bridge = BurrBridge(base_graph, burr_config)
        >>> result = burr_bridge.execute(initial_state={"input_key": "input_value"})
    """

    def __init__(self, base_graph, burr_config):
        self.base_graph = base_graph
        self.burr_config = burr_config
        self.project_name = burr_config.get("project_name", "scrapegraph_project")
        self.app_instance_id = burr_config.get("app_instance_id", "default-instance")
        self.burr_inputs = burr_config.get("inputs", {})
        self.burr_app = None

    def _initialize_burr_app(self, initial_state: Dict[str, Any] = None) -> Application:
        """
        Initialize a Burr application from the base graph.

        Args:
            initial_state (dict): The initial state of the Burr application.

        Returns:
            Application: The Burr application instance.
        """
        if initial_state is None:
            initial_state = {}

        actions = self._create_actions()
        transitions = self._create_transitions()
        hooks = [PrintLnHook()]
        burr_state = State(initial_state)
        application_context = ApplicationContext.get()
        builder = (
            ApplicationBuilder()
            .with_actions(**actions)
            .with_transitions(*transitions)
            .with_entrypoint(self.base_graph.entry_point)
            .with_state(**burr_state)
            .with_identifiers(app_id=str(uuid.uuid4())) # TODO -- grab this from state
            .with_hooks(*hooks)
        )
        if application_context is not None:
            builder = (
                builder
                .with_tracker(
                    application_context.tracker.copy() if application_context.tracker is not None else None
                )
                .with_spawning_parent(
                    application_context.app_id,
                    application_context.sequence_id,
                    application_context.partition_key,
                )
            )
        else:
            # This is the case in which nothing is spawning it
            # in this case, we want to create a new tracker from scratch
            builder = builder.with_tracker(tracking.LocalTrackingClient(project=self.project_name))
        return builder.build()

    def _create_actions(self) -> Dict[str, Any]:
        """
        Create Burr actions from the base graph nodes.

        Returns:
            dict: A dictionary of Burr actions with the node name 
            as keys and the action functions as values.
        """

        actions = {}
        for node in self.base_graph.nodes:
            action_func = BurrNodeBridge(node)
            actions[node.node_name] = action_func
        return actions

    def _create_transitions(self) -> List[Tuple[str, str, Any]]:
        """
        Create Burr transitions from the base graph edges.

        Returns:
            list: A list of tuples representing the transitions between Burr actions.
        """

        transitions = []
        for from_node, to_node in self.base_graph.edges.items():
            transitions.append((from_node, to_node, default))
        return transitions

    def _convert_state_from_burr(self, burr_state: State) -> Dict[str, Any]:
        """
        Convert a Burr state to a dictionary state.

        Args:
            burr_state (State): The Burr state to convert.

        Returns:
            dict: The dictionary state instance.
        """

        state = {}
        for key in burr_state.__dict__.keys():
            state[key] = getattr(burr_state, key)
        return state

    def execute(self, initial_state: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Execute the Burr application with the given initial state.

        Args:
            initial_state (dict): The initial state to pass to the Burr application.

        Returns:
            dict: The final state of the Burr application.
        """

        self.burr_app = self._initialize_burr_app(initial_state)

        # TODO: to fix final nodes detection
        final_nodes = [self.burr_app.graph.actions[-1].name]

        last_action, result, final_state = self.burr_app.run(
            halt_after=final_nodes,
            inputs=self.burr_inputs
        )

        return self._convert_state_from_burr(final_state)
