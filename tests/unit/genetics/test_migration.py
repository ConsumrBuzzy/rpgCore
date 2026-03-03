"""
Tests for Phase 4B migration to SlimeEntityTemplate.
Verifies that all active creation sites use the template
and that hard rejection works in RosterSyncService.
"""

import pytest
from unittest.mock import Mock, patch

from src.shared.genetics.entity_template import SlimeEntityTemplate
from src.shared.genetics.genome import SlimeGenome
from src.shared.teams.roster import RosterSlime, Roster
from src.shared.state.roster_sync import RosterSyncService
from src.shared.state.entity_registry import EntityRegistry
from src.shared.genetics.cultural_base import CulturalBase
from src.apps.slime_breeder.ui.scene_garden import GardenScene
from src.apps.slime_breeder.scenes.breeding_scene import BreedingScene
from src.shared.ui.spec import SPEC_720


class TestMigrationToEntityTemplate:
    """Test suite for Phase 4B migration verification."""
    
    @pytest.fixture
    def valid_genome(self):
        """Create a valid genome for testing."""
        return SlimeGenome(
            shape='round',
            size='medium',
            base_color=(100, 150, 200),
            pattern='solid',
            pattern_color=(50, 75, 100),
            accessory='none',
            curiosity=0.5,
            energy=0.5,
            affection=0.5,
            shyness=0.5,
            cultural_base=CulturalBase.EMBER,
            culture_expression={'ember': 1.0, 'gale': 0.0, 'marsh': 0.0, 'crystal': 0.0, 'tundra': 0.0, 'tide': 0.0},
            generation=1,
            level=3
        )
    
    @pytest.fixture
    def mock_roster_sync(self):
        """Create mock RosterSyncService for testing."""
        roster = Roster()
        registry = EntityRegistry()
        return RosterSyncService(roster, registry)
    
    def test_scene_garden_sync_uses_template(self, valid_genome):
        """Test that scene_garden.py _sync_roster_with_garden uses template."""
        # Create mock garden scene
        manager = Mock()
        manager.width = 1024
        manager.height = 768
        
        scene = GardenScene(manager, SPEC_720)
        scene.roster = Roster()
        
        # Create mock slime in garden state
        from src.apps.slime_breeder.entities.slime import Slime
        from src.shared.physics import Vector2
        
        slime = Slime("Test Slime", valid_genome, Vector2(100, 100), level=1)
        scene.garden_state.slimes = [slime]
        
        # Mock the template.build to verify it gets called
        with patch.object(SlimeEntityTemplate, 'build') as mock_build:
            mock_build.return_value = RosterSlime(
                slime_id="test_slime",
                name="Test Slime",
                genome=valid_genome
            )
            
            scene._sync_roster_with_garden()
            
            # Verify template.build was called
            mock_build.assert_called_once_with(
                genome=valid_genome,
                name="Test Slime",
                slime_id="test_slime"
            )
    
    def test_scene_garden_add_new_uses_template(self, valid_genome):
        """Test that scene_garden.py _add_new_slime uses template."""
        # Create mock garden scene
        manager = Mock()
        manager.width = 1024
        manager.height = 768
        
        scene = GardenScene(manager, SPEC_720)
        scene.roster = Roster()
        scene.garden_state.slimes = []
        
        # Mock the template.build to verify it gets called
        with patch.object(SlimeEntityTemplate, 'build') as mock_build:
            mock_build.return_value = RosterSlime(
                slime_id="mochi_1",
                name="Mochi 1",
                genome=valid_genome
            )
            
            with patch('src.apps.slime_breeder.ui.scene_garden.generate_random', return_value=valid_genome):
                with patch('src.apps.slime_breeder.ui.scene_garden.random.choice', return_value="Mochi"):
                    scene._add_new_slime()
            
            # Verify template.build was called
            mock_build.assert_called_once()
            args, kwargs = mock_build.call_args
            assert kwargs['name'] == "Mochi 1"
            assert kwargs['genome'] == valid_genome
            assert 'slime_id' in kwargs
    
    def test_breeding_scene_uses_template(self, valid_genome):
        """Test that breeding_scene.py finalize_breeding uses template."""
        # Create mock breeding scene
        manager = Mock()
        manager.width = 1024
        manager.height = 768
        
        scene = BreedingScene(manager, SPEC_720)
        scene.offspring_genome = valid_genome
        scene.offspring_name = "Test Offspring"
        
        # Create mock parents
        from src.shared.teams.roster import RosterSlime
        parent_a = RosterSlime("parent_a", "Parent A", valid_genome, level=3)
        parent_b = RosterSlime("parent_b", "Parent B", valid_genome, level=3)
        scene.parent_a = parent_a
        scene.parent_b = parent_b
        
        # Mock the template.build to verify it gets called
        with patch.object(SlimeEntityTemplate, 'build') as mock_build:
            mock_build.return_value = RosterSlime(
                slime_id="slime_12345",
                name="Test Offspring",
                genome=valid_genome,
                level=1,
                generation=2
            )
            
            with patch('random.randint', return_value=12345):
                scene.finalize_breeding()
            
            # Verify template.build was called
            mock_build.assert_called_once_with(
                genome=valid_genome,
                name="Test Offspring",
                slime_id="slime_12345",
                team='unassigned',
                level=1,
                generation=2
            )
    
    def test_roster_sync_hard_rejection(self, valid_genome):
        """Test that RosterSyncService now rejects invalid slimes."""
        # Create invalid slime (missing required fields)
        invalid_genome = SlimeGenome(
            shape=None,  # Invalid
            size=None,  # Invalid
            base_color=None,  # Invalid
            pattern=None,  # Invalid
            pattern_color=None,  # Invalid
            accessory=None,  # Invalid
            curiosity=0.5,
            energy=0.5,
            affection=0.5,
            shyness=0.5,
            cultural_base=CulturalBase.EMBER,
            culture_expression={'ember': 1.0, 'gale': 0.0, 'marsh': 0.0, 'crystal': 0.0, 'tundra': 0.0, 'tide': 0.0},
            generation=1,
            level=3
        )
        
        invalid_slime = RosterSlime(
            slime_id="invalid_slime",
            name="Invalid Slime",
            genome=invalid_genome
        )
        
        # Test that invalid slime is rejected
        result = mock_roster_sync.add_slime(invalid_slime)
        
        assert result is False
        assert len(mock_roster_sync.roster.entries) == 0
        assert len(mock_roster_sync.registry._entities) == 0
    
    def test_roster_sync_accepts_valid_slime(self, valid_genome, mock_roster_sync):
        """Test that RosterSyncService accepts valid slimes."""
        valid_slime = RosterSlime(
            slime_id="valid_slime",
            name="Valid Slime",
            genome=valid_genome
        )
        
        # Test that valid slime is accepted
        result = mock_roster_sync.add_slime(valid_slime)
        
        assert result is True
        assert len(mock_roster_sync.roster.entries) == 1
        assert len(mock_roster_sync.registry._entities) == 1
        assert "valid_slime" in mock_roster_sync.registry._entities
    
    def test_roster_load_validation_warns_only(self, valid_genome):
        """Test that roster.py load path validates but doesn't reject."""
        # Create save data with invalid slime
        save_data = {
            "version": 1,
            "slimes": [{
                "slime_id": "loaded_slime",
                "name": "Loaded Slime",
                "team": "unassigned",
                "locked": False,
                "alive": True,
                "genome": {
                    "shape": None,  # Invalid
                    "size": None,  # Invalid
                    "base_color": (100, 150, 200),
                    "pattern": "solid",
                    "pattern_color": (50, 75, 100),
                    "accessory": "none",
                    "curiosity": 0.5,
                    "energy": 0.5,
                    "affection": 0.5,
                    "shyness": 0.5,
                    "cultural_base": "ember",
                    "generation": 1,
                    "level": 3
                }
            }]
        }
        
        # Test that load still works but logs warning
        with patch('src.shared.teams.roster.logger') as mock_logger:
            roster = Roster.from_dict(save_data)
            
            # Should still load the slime (data integrity)
            assert len(roster.entries) == 1
            assert roster.entries[0].slime_id == "loaded_slime"
            
            # Should log warning about validation issues
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "loaded_slime" in warning_call
            assert "validation issues" in warning_call
