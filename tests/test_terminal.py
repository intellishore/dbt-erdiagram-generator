from dbterd import cli
from click.testing import CliRunner
import filecmp

def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli, ["schema.yml", "catalog.json", "test.dbml", "testproject", "False"])
    assert result.exit_code == 0
    assert filecmp.cmp('example.dbml', 'test.dbml')
    