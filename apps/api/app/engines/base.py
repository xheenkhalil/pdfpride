from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path

class EngineResult:
    def __init__(self, output_paths: List[Path], metrics: Optional[Dict[str, Any]] = None):
        self.output_paths = output_paths
        self.metrics = metrics or {}

class BaseEngine(ABC):
    """Abstract base class for all server-side document processing operations."""

    @abstractmethod
    def execute(
        self, 
        input_paths: List[Path], 
        output_dir: Path, 
        options: Dict[str, Any], 
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> EngineResult:
        """
        Executes the transformation safely.
        :param input_paths: Verified local file paths to input files.
        :param output_dir: Working directory dedicated for this job execution.
        :param options: User-configured options validated against tool registry schema.
        :param progress_callback: Optional hook to report progress (0-100) and status stage.
        """
        pass
