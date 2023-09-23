from aac.cli.aac_command import AacCommand

class LanguageContext(object):
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(LanguageContext, cls).__new__(cls)
    return cls.instance
  
  def parse_and_load(self, args: list[str]) -> None:
    pass
  
  def get_plugin_commands(self) -> list[AacCommand]:
    return []