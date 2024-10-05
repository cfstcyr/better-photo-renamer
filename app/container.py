import logging.config

from dependency_injector import containers, providers

from . import sections, services
from .window import Window


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
    )


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    command = providers.Singleton(services.CommandService)


class Components(containers.DeclarativeContainer):
    config = providers.Configuration()
    services = providers.DependenciesContainer()

    # Sections

    config_section = providers.Factory(sections.ConfigSection)
    files_section = providers.Factory(sections.FilesSection)
    bottom_bar_section = providers.Factory(
        sections.BottomBarSection, command_service=services.command
    )
    toolbar_section = providers.Factory(
        sections.ToolbarSection, command_service=services.command
    )


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["app_config.yml"])

    core = providers.Container(
        Core,
        config=config.core,
    )

    # Containers

    services = providers.Container(
        Services,
        config=config,
    )

    components = providers.Container(
        Components,
        config=config,
        services=services,
    )

    # App

    window = providers.Singleton(
        Window,
        command_service=services.command,
        config_section=components.config_section,
        files_section=components.files_section,
        bottom_bar_section=components.bottom_bar_section,
        toolbar_section=components.toolbar_section,
    )
