"""AaC Plugin implementation module for the aac-gen-design-doc plugin."""

plugin_version = "0.0.1"


def gen_design_doc(architecture_files: list[str], output_directory: str):
    """
    Generate a System Design Document from Architecture-as-Code models.

    Args:
        architecture_files <list[str]>: The yaml files containing the modelled system for which to
                                            generate the System Design document.
        output_directory <str>: The directory to which the System Design document will be written.
    """

    # TODO add implementation here
    raise NotImplementedError("gen_design_doc is not implemented.")
