import logging 

from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand

from grano.core import db, migrate
from grano.views import app
from grano.model import Project
from grano.logic import import_schema, export_schema
from grano.logic import import_aliases, export_aliases
from grano.logic import rebuild as rebuild_
from grano.logic.accounts import console_account
from grano.logic.projects import save as save_project
from grano.plugins import list_plugins, notify_plugins


log = logging.getLogger('grano')
manager = Manager(app)
manager.add_command('db', MigrateCommand)
    
notify_plugins('grano.startup', lambda o: o.configure(manager))


@manager.command
def schema_import(project, path):
    """ Load a schema specification from a YAML file. """
    pobj = Project.by_slug(project)
    if pobj is None:
        pobj = save_project({
            'slug': project,
            'label': project,
            'author': console_account()
            })
    with open(path, 'r') as fh:
        import_schema(pobj, fh)


@manager.command
def schema_export(project, path):
    """ Export the current schema to a YAML file. """
    pobj = Project.by_slug(project)
    assert pobj is not None, 'Project not available: %s' % project
    export_schema(pobj, path)


@manager.command
def alias_import(project, path):
    """ Load a set of entity aliases from a CSV file. """
    pobj = Project.by_slug(project)
    assert pobj is not None, 'Project not available: %s' % project
    with open(path, 'r') as fh:
        import_aliases(pobj, console_account(), fh)


@manager.command
def alias_export(project, path):
    """ Export all known entity aliases to a CSV file. """
    pobj = Project.by_slug(project)
    assert pobj is not None, 'Project not available: %s' % project
    export_aliases(pobj, path)


@manager.command
def rebuild():
    """ Trigger change processing on all relations and entities. """
    rebuild_()


@manager.command
def plugins():
    """ List all available plugins. """
    for namespace, plugins in list_plugins().items():
        print "%s: %s" % (namespace, ' '.join(plugins)) 


def run():
    manager.run()

if __name__ == "__main__":
    run()    
