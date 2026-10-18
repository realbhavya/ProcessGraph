from app.observability.metrics import MetricsRegistry
def test_registry_renders_counts_and_durations():
 r=MetricsRegistry(); r.increment("x_total",{"status":"200"}); r.observe("x_seconds",.25,{"status":"200"}); text=r.render()
 assert 'x_total{status="200"} 1' in text and 'x_seconds_count{status="200"} 1' in text and 'x_seconds_sum{status="200"} 0.250000' in text
def test_labels_are_stably_sorted():
 r=MetricsRegistry(); r.increment("x",{"z":"2","a":"1"}); assert 'x{a="1",z="2"}' in r.render()
