The following command, if executed in this directory, generates the plugin code:
  aac gen-plugin --code-output . unique_requirement_ids.aac

However, the directory structure seems off. It creates an aac and test-aac directories,
with a directory hierarchy that mirrors the /workspace/Aac/python/src/aac directory.

Use:
  cp -r aac/plugins/unique_requirement_ids ../../../aac/plugins/
to copy the results where they should go to execute the plugin.

You can include:
   import pdb; pdb.set_trace()
to execute the python command line debugger when executing the plugin.

