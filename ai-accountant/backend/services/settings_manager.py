"""
Settings Management System
Handles AI model selection and configuration settings.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    name: str
    display_name: str
    provider: str  # 'openai', 'anthropic', 'custom'
    base_url: str
    api_key_env: str
    max_tokens: int
    temperature: float
    cost_per_1k_input: float
    cost_per_1k_output: float
    description: str
    capabilities: List[str]  # ['categorization', 'insights', 'suggestions']
    enabled: bool = True

@dataclass
class AppSettings:
    """Application settings"""
    default_model: str
    batch_size: int
    max_retries: int
    timeout_seconds: float
    enable_token_tracking: bool
    enable_circuit_breaker: bool
    circuit_breaker_threshold: int
    circuit_breaker_timeout: int
    auto_categorize: bool
    fallback_to_rules: bool
    custom_categories: List[str]
    data_retention_days: int

class SettingsManager:
    """Manages application settings and model configurations"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.settings_file = self.config_dir / "app_settings.json"
        self.models_file = self.config_dir / "model_configs.json"
        
        # Default model configurations
        self.default_models = [
            ModelConfig(
                name="gpt-4o-mini",
                display_name="GPT-4o Mini",
                provider="openai",
                base_url="https://api.openai.com/v1",
                api_key_env="OPENAI_API_KEY",
                max_tokens=2000,
                temperature=0.1,
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006,
                description="Fast and cost-effective model for transaction categorization",
                capabilities=["categorization", "insights", "suggestions"],
                enabled=True
            ),
            ModelConfig(
                name="gpt-4o",
                display_name="GPT-4o",
                provider="openai",
                base_url="https://api.openai.com/v1",
                api_key_env="OPENAI_API_KEY",
                max_tokens=4000,
                temperature=0.1,
                cost_per_1k_input=0.005,
                cost_per_1k_output=0.015,
                description="Most capable model with highest accuracy",
                capabilities=["categorization", "insights", "suggestions"],
                enabled=True
            ),
            ModelConfig(
                name="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                provider="openai",
                base_url="https://api.openai.com/v1",
                api_key_env="OPENAI_API_KEY",
                max_tokens=2000,
                temperature=0.1,
                cost_per_1k_input=0.0015,
                cost_per_1k_output=0.002,
                description="Balanced performance and cost",
                capabilities=["categorization", "insights", "suggestions"],
                enabled=True
            ),
            ModelConfig(
                name="claude-3-haiku",
                display_name="Claude 3 Haiku",
                provider="anthropic",
                base_url="https://api.anthropic.com/v1",
                api_key_env="ANTHROPIC_API_KEY",
                max_tokens=2000,
                temperature=0.1,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125,
                description="Fast and efficient Anthropic model",
                capabilities=["categorization", "insights", "suggestions"],
                enabled=False  # Disabled by default until API key is configured
            ),
            ModelConfig(
                name="claude-3-sonnet",
                display_name="Claude 3 Sonnet",
                provider="anthropic",
                base_url="https://api.anthropic.com/v1",
                api_key_env="ANTHROPIC_API_KEY",
                max_tokens=4000,
                temperature=0.1,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                description="Balanced Anthropic model with good reasoning",
                capabilities=["categorization", "insights", "suggestions"],
                enabled=False
            ),
            ModelConfig(
                name="claude-3-opus",
                display_name="Claude 3 Opus",
                provider="anthropic",
                base_url="https://api.anthropic.com/v1",
                api_key_env="ANTHROPIC_API_KEY",
                max_tokens=4000,
                temperature=0.1,
                cost_per_1k_input=0.015,
                cost_per_1k_output=0.075,
                description="Most capable Anthropic model",
                capabilities=["categorization", "insights", "suggestions"],
                enabled=False
            )
        ]
        
        # Default application settings
        self.default_settings = AppSettings(
            default_model="gpt-4o-mini",
            batch_size=10,
            max_retries=3,
            timeout_seconds=30.0,
            enable_token_tracking=True,
            enable_circuit_breaker=True,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=60,
            auto_categorize=True,
            fallback_to_rules=True,
            custom_categories=[
                "Fuel", "Health/Pharmacy", "Groceries", "Dining", "Transport",
                "Utilities", "Entertainment", "Shopping", "Education", "Travel",
                "Insurance", "Investment", "Misc"
            ],
            data_retention_days=90
        )
        
        # Load configurations
        self.models = self._load_models()
        self.settings = self._load_settings()
    
    def _load_models(self) -> Dict[str, ModelConfig]:
        """Load model configurations from file"""
        if not self.models_file.exists():
            # Create default models file
            self._save_models()
            return {model.name: model for model in self.default_models}
        
        try:
            with open(self.models_file, 'r') as f:
                data = json.load(f)
                return {
                    name: ModelConfig(**config) 
                    for name, config in data.items()
                }
        except Exception as e:
            logger.error(f"Error loading model configurations: {e}")
            return {model.name: model for model in self.default_models}
    
    def _save_models(self):
        """Save model configurations to file"""
        try:
            with open(self.models_file, 'w') as f:
                json.dump(
                    {name: asdict(config) for name, config in self.models.items()},
                    f, indent=2
                )
        except Exception as e:
            logger.error(f"Error saving model configurations: {e}")
    
    def _load_settings(self) -> AppSettings:
        """Load application settings from file"""
        if not self.settings_file.exists():
            # Create default settings file
            self._save_settings()
            return self.default_settings
        
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                return AppSettings(**data)
        except Exception as e:
            logger.error(f"Error loading application settings: {e}")
            return self.default_settings
    
    def _save_settings(self):
        """Save application settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(asdict(self.settings), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving application settings: {e}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with their configurations"""
        available_models = []
        
        for model in self.models.values():
            if not model.enabled:
                continue
            
            # Check if API key is available
            api_key = os.getenv(model.api_key_env)
            has_api_key = bool(api_key)
            
            available_models.append({
                "name": model.name,
                "display_name": model.display_name,
                "provider": model.provider,
                "description": model.description,
                "capabilities": model.capabilities,
                "has_api_key": has_api_key,
                "cost_per_1k_input": model.cost_per_1k_input,
                "cost_per_1k_output": model.cost_per_1k_output,
                "max_tokens": model.max_tokens,
                "temperature": model.temperature
            })
        
        return available_models
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        return self.models.get(model_name)
    
    def update_model_config(self, model_name: str, updates: Dict[str, Any]) -> bool:
        """Update configuration for a specific model"""
        if model_name not in self.models:
            return False
        
        model = self.models[model_name]
        
        # Update allowed fields
        allowed_fields = {
            'display_name', 'base_url', 'max_tokens', 'temperature',
            'cost_per_1k_input', 'cost_per_1k_output', 'description',
            'capabilities', 'enabled'
        }
        
        for field, value in updates.items():
            if field in allowed_fields and hasattr(model, field):
                setattr(model, field, value)
        
        self._save_models()
        return True
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current application settings"""
        return asdict(self.settings)
    
    def update_settings(self, updates: Dict[str, Any]) -> bool:
        """Update application settings"""
        try:
            # Update allowed fields
            allowed_fields = {
                'default_model', 'batch_size', 'max_retries', 'timeout_seconds',
                'enable_token_tracking', 'enable_circuit_breaker',
                'circuit_breaker_threshold', 'circuit_breaker_timeout',
                'auto_categorize', 'fallback_to_rules', 'custom_categories',
                'data_retention_days'
            }
            
            for field, value in updates.items():
                if field in allowed_fields and hasattr(self.settings, field):
                    setattr(self.settings, field, value)
            
            self._save_settings()
            return True
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return False
    
    def add_custom_model(self, model_config: ModelConfig) -> bool:
        """Add a custom model configuration"""
        try:
            self.models[model_config.name] = model_config
            self._save_models()
            return True
        except Exception as e:
            logger.error(f"Error adding custom model: {e}")
            return False
    
    def remove_model(self, model_name: str) -> bool:
        """Remove a model configuration (except default models)"""
        if model_name in [model.name for model in self.default_models]:
            logger.warning(f"Cannot remove default model: {model_name}")
            return False
        
        if model_name in self.models:
            del self.models[model_name]
            self._save_models()
            return True
        
        return False
    
    def reset_to_defaults(self):
        """Reset all configurations to defaults"""
        self.models = {model.name: model for model in self.default_models}
        self.settings = self.default_settings
        self._save_models()
        self._save_settings()
        logger.info("Settings reset to defaults")

# Global settings manager instance
settings_manager = SettingsManager()
