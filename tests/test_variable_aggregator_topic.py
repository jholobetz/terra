import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_variable_aggregator_has_build_topic_variables():
    aggregator_path = os.path.join(PROJECT_ROOT, "app", "logic", "VariableAggregator.php")
    with open(aggregator_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "function buildTopicVariables" in content, "VariableAggregator missing buildTopicVariables method"
    assert "function buildSubtopicVariables" in content, "VariableAggregator missing buildSubtopicVariables method"

def test_physics_controller_uses_variable_aggregator_for_topics():
    controller_path = os.path.join(PROJECT_ROOT, "app", "controllers", "PhysicsController.php")
    with open(controller_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify buildTopicVariables is called in PhysicsController
    assert "VariableAggregator::buildTopicVariables" in content, "PhysicsController should call VariableAggregator::buildTopicVariables"

    # Verify no raw SQL query for semantic_variables exists in topic view handler
    assert "SELECT title, semantic_variables FROM formulas" not in content, "PhysicsController should not use ad-hoc SQL for topic variables"
