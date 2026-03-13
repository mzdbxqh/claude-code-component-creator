"""
Detectors Package

检测器模块集合，用于反模式检测和迁移分析。

Modules:
- pattern_detector: Command 模式检测 (Alias vs Workflow)
- migration_analyzer: Command 到 Skill 迁移分析

Author: mzdbxqh
Created: 2026-03-13
"""

from .pattern_detector import CommandPatternDetector, detect_command_pattern
from .migration_analyzer import MigrationAnalyzer, analyze_migration, generate_migration_report

__all__ = [
    'CommandPatternDetector',
    'detect_command_pattern',
    'MigrationAnalyzer',
    'analyze_migration',
    'generate_migration_report',
]
