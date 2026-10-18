from pathlib import Path
ROOT=Path(__file__).parents[3]
def test_server_never_marks_process_variables_writable():
 text=(ROOT/'backend/app/opcua/server.py').read_text(); assert 'set_writable' not in text and 'SourceType' in text and 'ReadOnly' in text
def test_collector_has_reconnect_backoff_and_subscription():
 text=(ROOT/'backend/app/opcua/collector.py').read_text(); assert 'create_subscription' in text and 'subscribe_data_change' in text and 'min(delay*2,30)' in text and 'check_connection' in text
