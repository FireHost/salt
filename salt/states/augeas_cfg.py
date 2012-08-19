import logging
import os
import difflib
from contextlib import nested

logger = logging.getLogger(__name__)


def __virtual__():
    try:
        from augeas import Augeas
        _ = Augeas
    except ImportError:
        return False
    else:
        return "augeas"


def _resolve_changes(sfn, dfn):
    ret = {}
    # Augeas won't tell us if it made any changes, so we have to go about this
    # the hard way. The existence of the backup file will tell us.
    if os.path.isfile(sfn) and os.path.isfile(dfn):
        with nested(open(sfn, 'rb'), open(dfn, 'rb')) as (src, dst):
            diff = ''.join(difflib.unified_diff(src.readlines(),
                                                dst.readlines(),
                                                sfn,
                                                dfn))
        if __opts__['test']:
            if len(diff) > 0:
                ret['comment'] = ('Files differ, would make the following '
                                  'changes\n%s' % diff)
                ret['result'] = None
            os.remove(dfn)
        else:
            if len(diff) > 0:
                ret['changes'] = {'diff': diff}
                ret['comment'] = 'Changes made'
            os.remove(sfn)
    return ret


def setvalue(name, expressions):
    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': 'No changes made'}

    from augeas import Augeas

    if len(expressions) < 1:
        ret['comment'] = "No expressions given"
        ret['result'] = False
        return ret

    if __opts__['test']:
        aug = Augeas(flags=Augeas.SAVE_NEWFILE)
        sfn = name
        dfn = '%s.augnew' % name
    else:
        aug = Augeas(flags=Augeas.SAVE_BACKUP)
        sfn = '%s.augsave' % name
        dfn = name

    if not os.path.isfile(name):
        ret['comment'] = "Unable to find file '%s'" % name
        ret['result'] = False
        return ret

    for (subpath, value) in expressions:
        try:
            path = '/files%s/%s' % (name, subpath)
            aug.set(path, value)
        except ValueError as e:
            ret['comment'] = 'Multiple values: %s' % e
            ret['result'] = False
            return ret
        except TypeError as e:
            ret['comment'] = ("Error setting values, wrong type\n"
                              "Expression was '%s' '%s'" % (path, value))
            ret['result'] = False
            return ret

    try:
        aug.save()
    except IOError as e:
        ret['comment'] = str(e)
        ret['result'] = False
        return ret

    ret.update(_resolve_changes(sfn, dfn))
    return ret


def remove(name, values):
    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': ''}

    from augeas import Augeas

    if len(values) < 1:
        ret['comment'] = "No values given"
        ret['result'] = False
        return ret

    if __opts__['test']:
        aug = Augeas(flags=Augeas.SAVE_NEWFILE)
        sfn = name
        dfn = '%s.augnew' % name
    else:
        aug = Augeas(flags=Augeas.SAVE_BACKUP)
        sfn = '%s.augsave' % name
        dfn = name

    if not os.path.isfile(name):
        ret['comment'] = "Unable to find file '%s'" % name
        ret['result'] = False
        return ret

    for value in values:
        try:
            path = '/files%s/%s' % (name, value)
            aug.remove(path)
        except TypeError as e:
            ret['comment'] = ("Error removing, wrong type\n"
                              "Expression was '%s'" % path)
            ret['result'] = False
            return ret

    try:
        aug.save()
    except IOError as e:
        ret['comment'] = str(e)
        ret['result'] = False
        return ret

    ret.update(_resolve_changes(sfn, dfn))
    return ret
