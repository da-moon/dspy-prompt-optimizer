"""
DSPy-based prompt optimization module.
"""

import dspy
import logging
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PromptOptimizer:
    """Base class for prompt optimization strategies."""
    
    def __init__(self, model: str, api_key: str, verbose: bool = False):
        """
        Initialize the prompt optimizer.
        
        Args:
            model: The model to use for optimization
            api_key: Anthropic API key
            verbose: Whether to enable verbose output
        """
        self.model = model
        self.api_key = api_key
        self.verbose = verbose
           # Set up DSPy with Anthropic
        self._setup_dspy()
    
    def _setup_dspy(self) -> None:
        """Set up DSPy with the Anthropic model."""
        # Configure the LM using Anthropic
        self.lm = dspy.LM(
            model=self.model,
            provider="anthropic",
            api_key=self.api_key
        )
        
        # Set the LM as the default for DSPy
        dspy.settings.configure(lm=self.lm)
        
        if self.verbose:
            logger.info(f"DSPy configured with model: {self.model}")  
    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the given prompt.
        
        Args:
            prompt_text: The prompt text to optimize
            
        Returns:
            The optimized prompt text
        """
        raise NotImplementedError("Subclasses must implement the optimize method")


class SelfRefinementOptimizer(PromptOptimizer):
    """Optimizer that uses self-refinement to improve prompts."""
    
    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using self-refinement.
        
        Args:
            prompt_text: The prompt text to optimize
            
        Returns:
            The optimized prompt text
        """
        if self.verbose:
            logger.info("Using self-refinement optimization approach")
        
        # Define a signature for prompt refinement
        class PromptRefiner(dspy.Signature):
            """Refine a prompt to make it more effective."""
            
            prompt = dspy.InputField(desc="The original prompt that needs refinement")
            analysis = dspy.OutputField(desc="Analysis of the prompt's strengths and weaknesses")
            improved_prompt = dspy.OutputField(desc="A refined version of the prompt that addresses the weaknesses")
        
        # Create a module that uses the signature
        refiner = dspy.Predict(PromptRefiner)

        # Apply the module to refine the prompt
        result: Any = refiner(prompt=prompt_text)
        
        if self.verbose:
            logger.info(f"Analysis: {result.analysis}")
        
        return str(result.improved_prompt)


class ExampleBasedOptimizer(PromptOptimizer):
    """Optimizer that uses examples to improve prompts."""
    
    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using example-based optimization.
        
        Args:
            prompt_text: The prompt text to optimize
            
        Returns:
            The optimized prompt text
        """
        if self.verbose:
            logger.info("Using example-based optimization approach")
        
        # Define a signature for prompt refinement with examples
        class ExamplePromptRefiner(dspy.Signature):
            """Refine a prompt based on examples of good prompts."""
            
            prompt = dspy.InputField(desc="The original prompt that needs refinement")
            analysis = dspy.OutputField(desc="Analysis of the prompt's strengths and weaknesses")
            improved_prompt = dspy.OutputField(desc="A refined version of the prompt that addresses the weaknesses")
        
        # Examples of good prompts and their refined versions
        examples = [
            dspy.Example(
                prompt="Tell me about climate change",
                analysis="This prompt is too vague and doesn't specify what aspects of climate change to focus on or what depth of information is needed.",
                improved_prompt="Provide a comprehensive explanation of the primary causes of climate change, focusing on both natural and anthropogenic factors. Include recent scientific consensus on the rate of global warming and its projected impacts on ecosystems over the next 50 years."
            ),
            dspy.Example(
                prompt="How do I make a website?",
                analysis="This prompt lacks specificity about the type of website, the user's skill level, or what technologies they're interested in using.",
                improved_prompt="I'm a beginner with basic HTML/CSS knowledge looking to create a personal portfolio website. Please provide a step-by-step guide on how to build a responsive portfolio site, including recommended frameworks, hosting options, and essential features for showcasing my work effectively."
            )
        ]
        
        # Create a module that uses the signature with examples
        refiner = dspy.ChainOfThought(ExamplePromptRefiner)
        
        # Use the examples directly with the module
        # Modern DSPy no longer uses Teleprompter but instead uses the examples directly
        # Initialize refinement_payload to explicitly type it for mypy
        refinement_payload: Any = None
        
        # Process each example to train the module
        for example in examples:
            # Let the module learn from this example
            refiner.update_demos([example])
        
        # Apply the module with learned examples to refine the prompt
        refinement_payload = refiner(prompt=prompt_text)
        
        if self.verbose and refinement_payload:
            logger.info(f"Analysis: {refinement_payload.analysis}")
        
        return str(refinement_payload.improved_prompt) if refinement_payload else "Failed to optimize prompt using example-based approach"


class MetricBasedOptimizer(PromptOptimizer):
    """Optimizer that uses metrics to improve prompts."""
    
    def optimize(self, prompt_text: str) -> str:
        """
        Optimize the prompt using metric-based optimization.
        
        Args:
            prompt_text: The prompt text to optimize
            
        Returns:
            The optimized prompt text
        """
        if self.verbose:
            logger.info("Using metric-based optimization approach")
        
        # Define a signature for prompt generation
        class PromptGenerator(dspy.Signature):
            """Generate an improved prompt based on specific metrics."""
            
            original_prompt = dspy.InputField(desc="The original prompt to improve")
            improved_prompt = dspy.OutputField(desc="An improved version of the prompt")
        
        # Define a signature for evaluating prompts
        class PromptEvaluator(dspy.Signature):
            """Evaluate a prompt based on clarity, specificity, and actionability."""
            
            prompt = dspy.InputField(desc="The prompt to evaluate")
            clarity_score = dspy.OutputField(desc="Score for clarity (1-10)")
            specificity_score = dspy.OutputField(desc="Score for specificity (1-10)")
            actionability_score = dspy.OutputField(desc="Score for actionability (1-10)")
            total_score = dspy.OutputField(desc="Sum of all scores (3-30)")
            feedback = dspy.OutputField(desc="Feedback on how to improve the prompt")
        
        # Create modules
        generator = dspy.Predict(PromptGenerator)
        evaluator = dspy.ChainOfThought(PromptEvaluator)
        
        # Define the optimization loop
        max_iterations = 3
        best_prompt = prompt_text
        best_score = 0
        
        for i in range(max_iterations):
            if i == 0:
                # Evaluate the original prompt
                evaluation: Any = evaluator(prompt=best_prompt)
                best_score = int(evaluation.total_score)
                
                if self.verbose:
                    logger.info(f"Original prompt score: {best_score}")
                    logger.info(f"Feedback: {evaluation.feedback}")
            
            # Generate an improved prompt
            result: Any = generator(original_prompt=best_prompt)
            candidate_prompt = result.improved_prompt
            
            # Evaluate the candidate prompt
            candidate_evaluation: Any = evaluator(prompt=candidate_prompt)
            candidate_score = int(candidate_evaluation.total_score)
            
            if self.verbose:
                logger.info(f"Iteration {i+1} score: {candidate_score}")
                logger.info(f"Feedback: {candidate_evaluation.feedback}")
            
            # Keep the better prompt
            if candidate_score > best_score:
                best_prompt = candidate_prompt
                best_score = candidate_score
                
                if self.verbose:
                    logger.info(f"Found better prompt with score: {best_score}")
        
        return best_prompt


def optimize_prompt(
    prompt_text: str,
    model: str,
    api_key: str,
    optimization_type: str = "self",
    verbose: bool = False
) -> str:
    """
    Optimize a prompt using the specified optimization approach.
    
    Args:
        prompt_text: The prompt text to optimize
        model: The model to use for optimization
        api_key: Anthropic API key
        optimization_type: Type of optimization to perform ('self', 'example', or 'metric')
        verbose: Whether to enable verbose output
        
    Returns:
        The optimized prompt text
    """
    optimizer: PromptOptimizer
    # Select the appropriate optimizer based on the optimization type
    if optimization_type == "self":
        optimizer = SelfRefinementOptimizer(model=model, api_key=api_key, verbose=verbose)
    elif optimization_type == "example":
        optimizer = ExampleBasedOptimizer(model=model, api_key=api_key, verbose=verbose)
    elif optimization_type == "metric":
        optimizer = MetricBasedOptimizer(model=model, api_key=api_key, verbose=verbose)
    else:
        raise ValueError(f"Unknown optimization type: {optimization_type}")
    
    # Optimize the prompt
    return optimizer.optimize(prompt_text)
