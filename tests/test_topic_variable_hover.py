import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_topic_view_template_has_abstract_selectors():
    topic_view = os.path.join(PROJECT_ROOT, "app", "views", "physics", "topic.php")
    with open(topic_view, "r", encoding="utf-8") as f:
        content = f.read()

    assert 'id="topic-beginning-abstract"' in content, "topic.php missing #topic-beginning-abstract selector"
    assert 'subtopic-card-abstract' in content, "topic.php missing .subtopic-card-abstract selector"
    assert 'id="topic-var-map"' in content, "topic.php missing #topic-var-map script container"

def test_physics_controller_has_variable_trigger_wrapper():
    controller = os.path.join(PROJECT_ROOT, "app", "controllers", "PhysicsController.php")
    with open(controller, "r", encoding="utf-8") as f:
        content = f.read()

    assert "wrapVariableTriggers" in content, "PhysicsController missing wrapVariableTriggers function"
    assert "variable-hover-trigger" in content, "PhysicsController missing variable-hover-trigger markup"
    assert "topicVariableMap" in content, "PhysicsController missing topicVariableMap assembly"

def test_js_hub_interactions_has_popover_handler():
    js_file = os.path.join(PROJECT_ROOT, "public", "js", "hub_interactions.js")
    with open(js_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "topic-var-map" in content, "hub_interactions.js missing topic-var-map reader"
    assert "variable-hover-card-popover" in content, "hub_interactions.js missing popover container"
    assert "showPopover" in content, "hub_interactions.js missing showPopover logic"

def test_css_has_variable_hover_styles():
    css_file = os.path.join(PROJECT_ROOT, "public", "css", "physics.css")
    with open(css_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert ".variable-hover-trigger" in content, "physics.css missing .variable-hover-trigger styles"
    assert ".variable-hover-popover" in content, "physics.css missing .variable-hover-popover styles"

def test_equation_not_wrapped_as_variable_hover_trigger():
    controller_file = os.path.join(PROJECT_ROOT, "app", "controllers", "PhysicsController.php")
    with open(controller_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "strlen($tex) > 15" in content, "PhysicsController missing length limit for standalone variables"
    assert "strpbrk($tex," in content, "PhysicsController missing operator exclusion filter"


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

    assert "VariableAggregator::buildTopicVariables" in content, "PhysicsController should call VariableAggregator::buildTopicVariables"
    assert "SELECT title, semantic_variables FROM formulas" not in content, "PhysicsController should not use ad-hoc SQL for topic variables"
