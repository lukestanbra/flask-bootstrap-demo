from demo import create_app


def test_config():
  """Test create_app without passing test config."""
  assert not create_app().testing
  assert create_app({"TESTING": True}).testing

def test_init_db_command(runner, monkeypatch):
  class Recorder:
    called = False

  def fake_init_db():
    Recorder.called = True

  monkeypatch.setattr("demo.init_db", fake_init_db)
  result = runner.invoke(args=["init-db"])
  assert "Initialized" in result.output
  assert Recorder.called